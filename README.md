# 🧹 桌面卫生早报

> 扫 Desktop / Downloads 的陈年文件，每天推送天气 + 要闻 + 桌面卫生综合报告到 QQ 私聊。

**Desk Hygiene — Daily Briefing** for Windows QQ Bot users.

---

## 📦 文件说明

| 文件 | 用途 |
|---|---|
| `scan.py` | 扫描 Desktop + Downloads，列出超过 **180 天** 未改动的文件 |
| `morning_report.py` | 生成综合早报（天气 + 要闻 + 桌面卫生），可独立运行 |
| `SKILL.md` | OpenClaw Skill 配置文档 |
| `README.md` | 本文件 |

---

## 🚀 快速使用

### 桌面卫生扫描

```bash
python scan.py
```

扫描 C 盘 Desktop 和 Downloads 目录，输出超过半年未动的"陈年文件"清单。

### 每日早报

```bash
python morning_report.py
```

生成包含以下模块的纯文本报告：

- 🌤 **今日天气** — 北京实时天气 + 今明两日预报（数据源：wttr.in）
- 📰 **今日要闻** — 百度热搜 / 新浪新闻 / 腾讯新闻热点标题
- 🧹 **桌面卫生** — 半年未动文件概览（每个目录最多展示最久的 5 个）

---

## ⚙️ 自定义配置

在脚本头部修改以下变量：

| 变量 | 所在文件 | 说明 |
|---|---|---|
| `WATCH_DIRS` | `scan.py` / `morning_report.py` | 扫描目录列表 |
| `DAYS` / `STALE_DAYS` | `scan.py` / `morning_report.py` | 过期天数（默认 180） |
| `CITY` | `morning_report.py` | 天气城市（默认 Beijing） |

示例 — 改为扫描 D 盘工作目录，阈值 90 天：

```python
WATCH_DIRS = [
    pathlib.Path(r"D:\work"),
    pathlib.Path(r"D:\downloads"),
]
STALE_DAYS = 90
```

---

## 📋 依赖

- Python 3.x（内置标准库，无需 pip install）
- Windows 系统
- 网络可达 wttr.in、news.qq.com、news.sina.com.cn、top.baidu.com

---

## 🔒 安全

- 只读扫描：`stat()` 读取文件元数据，绝不写磁盘
- 绝不自动移动 / 重命名 / 删除任何文件
- 所有路径硬编码于脚本配置区，不拼接用户输入
- 仅在用户明确指令下执行文件操作

---

## 🧩 OpenClaw 集成（可选）

搭配 [OpenClaw](https://github.com/openclaw) 使用，可作为 Agent Skill 自动触发。

1. 将 `SKILL.md` 放入 OpenClaw workspace 的 `skills/desk-hygiene/` 目录
2. 将 `scan.py` 和 `morning_report.py` 放在同目录
3. 配置 Cron 每天早上 08:00 执行每日早报推送

---

## 📄 License

MIT
