# 桌面卫生早报 Desk Hygiene / Daily Briefing

## 文件说明

| 文件 | 用途 |
|---|---|
| `scan.py` | 扫描 Desktop / Downloads，列出超过 180 天未改动的文件 |
| `morning_report.py` | 生成综合早报（天气 + 要闻 + 桌面卫生），可独立运行 |
| `SKILL.md` | 本说明文件 |

## 快速扫描

```bash
python scan.py
```

输出纯文本清单，显示 Desktop 和 Downloads 中超过半年未动的文件。

## 每日早报

```bash
python morning_report.py
```

生成包含以下模块的纯文本报告：
- 🌤 今日天气（wttr.in 数据源）
- 📰 今日要闻（百度热搜 / 新浪新闻 / 腾讯新闻）
- 🧹 桌面卫生（半年未动文件概览）

## 依赖

- Python 3.x（内置标准库，无需额外 pip install）
- Windows 系统（路径硬编码 `C:\Users\TRX\Desktop`、`C:\Users\TRX\Downloads`）
- 网络可达 wttr.in、news.qq.com、news.sina.com.cn、top.baidu.com

## 注意事项

- 只读扫描，绝不修改/删除文件
- 如需更改扫描目录，修改脚本中的 `WATCH_DIRS` 列表
- 如需更改过期天数，修改脚本中的 `STALE_DAYS` / `DAYS` 变量
