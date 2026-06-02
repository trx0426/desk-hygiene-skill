#!/usr/bin/env python3
"""
每日早报 · 综合版
━━━━━━━━━━━━━━━━━━━━━
模块：天气 + 要闻 + 桌面卫生
输出纯文本，供 cron / 直接调用呈现
"""

import datetime
import json
import os
import pathlib
import subprocess
import sys
import time
import urllib.error
import urllib.request

# ─── 配置 ──────────────────────────────────────────────
CITY = "Beijing"
WATCH_DIRS = [
    pathlib.Path(r"C:\Users\TRX\Desktop"),
    pathlib.Path(r"C:\Users\TRX\Downloads"),
]
STALE_DAYS = 180
# ────────────────────────────────────────────────────────


def fetch_url(url: str, timeout: int = 10) -> str | None:
    """GET 一个 URL 并返回文本，失败返回 None"""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except Exception as exc:
        return None


def section_weather(city: str) -> list[str]:
    """🌤 今日天气 —— 用 wttr.in JSON 接口"""
    lines: list[str] = []
    raw = fetch_url(f"https://wttr.in/{city}?format=j1")
    if raw is None:
        lines.append("   ❌ 天气服务暂时不可用")
        return lines

    try:
        data = json.loads(raw)
        cc = data.get("current_condition", [{}])[0]
        temp = cc.get("temp_C", "?")
        feels = cc.get("FeelsLikeC", "?")
        desc = cc.get("weatherDesc", [{}])[0].get("value", "?")
        humid = cc.get("humidity", "?")
        wind = cc.get("windspeedKmph", "?")
        wind_dir = cc.get("winddir16Point", "?")

        lines.append(f"   🌡 {desc}，{temp}°C（体感 {feels}°C）")
        lines.append(f"   💧 湿度 {humid}%  |  💨 {wind_dir} {wind} km/h")

        # 今明预报
        weather = data.get("weather", [])
        for idx, label in enumerate(["今日", "明日"]):
            if idx < len(weather):
                w = weather[idx]
                date = w.get("date", "")
                hi = w.get("maxtempC", "?")
                lo = w.get("mintempC", "?")
                sunr = w.get("astronomy", [{}])[0].get("sunrise", "?")
                suns = w.get("astronomy", [{}])[0].get("sunset", "?")
                lines.append(f"   {label} {date}  {lo}~{hi}°C  🌅 {sunr}  🌇 {suns}")
    except (KeyError, IndexError, json.JSONDecodeError) as exc:
        lines.append(f"   ⚠️ 天气解析异常: {exc}")

    return lines


def _title_link_extract(html: str, base_url: str) -> list[tuple[str, str]]:
    """提取 <a> 标签内的标题文本 + 链接，返回 [(title, url), ...]"""
    import re
    pattern = re.compile(r'<a[^>]*href="([^"]+)"[^>]*>([^<]{8,80})<\/a>')
    results: list[tuple[str, str]] = []
    seen = set()
    noise_kw = ["查看更多", "更多新闻", "下一页", "上一页", "点击排行", "全部", "详细"]
    for m in pattern.finditer(html):
        href = m.group(1).strip()
        text = m.group(2).strip()
        if not text or text in seen:
            continue
        if len(text) < 8:
            continue
        han_count = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
        if han_count < 3:
            continue
        if any(kw in text for kw in noise_kw):
            continue
        if not ("\u4e00" <= text[0] <= "\u9fff"):
            continue
        # 拼完整 URL
        if href.startswith("//"):
            href = "https:" + href
        elif href.startswith("/"):
            href = base_url.rstrip("/") + href
        elif not href.startswith("http"):
            href = base_url.rstrip("/") + "/" + href
        seen.add(text)
        results.append((text, href))
    return results


def section_news() -> list[str]:
    """📰 今日要闻 —— 多源抓取标题 + 链接"""
    sources: list[tuple[str, str, int]] = [
        ("🔥 百度热搜", "https://top.baidu.com/board?tab=realtime", 7),
        ("📌 新浪新闻", "https://news.sina.com.cn/", 7),
        ("📌 腾讯新闻", "https://news.qq.com/", 5),
    ]

    lines: list[str] = []
    fetched_any = False

    for name, url, limit in sources:
        html = fetch_url(url)
        if html is None:
            continue
        items = _title_link_extract(html, url)
        if items:
            fetched_any = True
            lines.append(f"\n  {name}")
            for t, link in items[:limit]:
                max_len = 40
                display = t if len(t) <= max_len else t[:max_len-1] + "…"
                lines.append(f"     · {display}")
                lines.append(f"       {link}")

    if not fetched_any:
        lines.append("   ❌ 新闻源暂时无法访问，稍后重试")

    return lines


def section_hygiene() -> list[str]:
    """🧹 桌面卫生 —— 复用 scan.py 逻辑，精简版"""
    lines: list[str] = []
    now = time.time()
    cutoff = now - STALE_DAYS * 86400

    stale_by_dir: dict[str, list[tuple[str, int]]] = {}

    for base in WATCH_DIRS:
        key = str(base)
        stale_by_dir[key] = []
        if not base.exists():
            lines.append(f"  ⚠️ 目录不存在: {base.name}")
            continue
        for p in base.iterdir():
            if not p.is_file():
                continue
            try:
                mtime = p.stat().st_mtime
            except (OSError, FileNotFoundError):
                continue
            if mtime < cutoff:
                days = int((now - mtime) / 86400)
                stale_by_dir[key].append((p.name, days))

    total = sum(len(v) for v in stale_by_dir.values())

    if total == 0:
        lines.append("  ✅ 桌面 + 下载区干净，没有半年以上的陈年文件 ✨")
    else:
        lines.append(f"  📦 共 {total} 个文件超过 {STALE_DAYS} 天未改动")
        for dir_key, items in stale_by_dir.items():
            dir_name = pathlib.Path(dir_key).name
            if not items:
                continue
            items.sort(key=lambda x: x[1], reverse=True)
            lines.append(f"  📁 {dir_name}（{len(items)} 个）")
            # 只展示最久的 5 个
            for name, days in items[:5]:
                lines.append(f"     · {name}  ({days}天)")
            if len(items) > 5:
                lines.append(f"     ……还有 {len(items)-5} 个")
        lines.append("  💡 建议：花 5 分钟归档或清理一下")

    return lines


# ═══════════════ 主入口 ══════════════════════

def main():
    today = datetime.date.today()
    weekday_cn = ["一", "二", "三", "四", "五", "六", "日"][today.weekday()]
    date_str = today.strftime("%Y-%m-%d")

    report: list[str] = []
    sep = "─" * 48

    # 头部
    report.append(f"🌤 早安！北京 · {date_str} 星期{weekday_cn}")
    report.append(sep)

    # ── 天气 ──
    report.append("\n🌤 今日天气")
    report.append("─" * 20)
    report.extend(section_weather(CITY))

    # ── 要闻 ──
    report.append(f"\n📰 今日要闻")
    report.append("─" * 20)
    report.extend(section_news())

    # ── 桌面卫生 ──
    report.append(f"\n🧹 桌面卫生")
    report.append("─" * 20)
    report.extend(section_hygiene())

    # 尾部
    report.append(f"\n{sep}")
    report.append("💬 回复我聊聊今天的计划，或者直接说“继续”")

    # ── 输出 ──
    output = "\n".join(report)
    print(output)

    # 同时写入 memory 存档
    mem_dir = pathlib.Path(__file__).parent.parent / "memory" / "daily-briefing"
    mem_dir.mkdir(parents=True, exist_ok=True)
    mem_path = mem_dir / f"{today.isoformat()}.md"
    mem_path.write_text(output, encoding="utf-8")


if __name__ == "__main__":
    main()
