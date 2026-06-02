#!/usr/bin/env python3
"""桌面卫生早报：扫 Desktop + Downloads，列超过半年没动过的文件"""

import os
import time
import pathlib
import sys

# ── 只盯这两个 ───────────────────────────────────────────
WATCH_DIRS = [
    pathlib.Path(r"C:\Users\TRX\Desktop"),
    pathlib.Path(r"C:\Users\TRX\Downloads"),
]

DAYS = 180          # 半年≈180天；要精确按月自己改下面注释
NOW  = time.time()
CUT  = NOW - DAYS * 86400
# ─────────────────────────────────────────────────────────

stale = []

for base in WATCH_DIRS:
    if not base.exists():
        print(f"[!] 目录不存在（跳过）: {base}", file=sys.stderr)
        continue
    for p in base.iterdir():          # ← iterdir() 只扫顶层，不钻子文件夹
        if not p.is_file():
            continue
        try:
            m = p.stat().st_mtime
        except FileNotFoundError:
            continue
        if m < CUT:
            days = int((NOW - m) / 86400)
            stale.append((p, days))

# ── 输出 ─────────────────────────────────────────────────
today = pathlib.Path(__file__).stat().st_mtime
import datetime as _dt
today_str = _dt.date.today().isoformat()

print(f"🧹 桌面卫生早报 · {today_str}")
print(f"⏰ 只看 Desktop / Downloads，阈值：>{DAYS}天（约半年）\n")

if not stale:
    print("✅  干净，没有半年以上的陈年文件。\n")
else:
    stale.sort(key=lambda x: x[1], reverse=True)
    print(f"📋  {len(stale)} 个文件超过半年没改动：\n")
    for p, d in stale:
        print(f"  · {p.name}")
        print(f"    路径 : {p}")
        print(f"    闲置 : {d} 天\n")
    print("💡 建议：开工前 5 分钟，归档/分类/处理掉。\n")