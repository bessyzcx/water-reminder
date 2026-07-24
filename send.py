#!/usr/bin/env python3
"""企业微信群机器人 - 喝水提醒推送脚本
纯标准库，云端运行（GitHub Actions），不依赖本地电脑。
"""

import json
import sys
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

BJT = timezone(timedelta(hours=8))


def load_config():
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def send_webhook(webhook_url, content):
    """发送文本消息到企业微信 webhook"""
    payload = json.dumps(
        {"msgtype": "text", "text": {"content": content}},
        ensure_ascii=False,
    ).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    if result.get("errcode") != 0:
        raise RuntimeError(f"企业微信返回错误: {result}")
    return result


def main():
    config = load_config()

    # webhook URL：优先环境变量（GitHub Actions Secret），其次配置文件
    webhook_url = os.environ.get("WECOM_WEBHOOK_URL") or config.get("webhook_url", "")
    if not webhook_url:
        print("[FAIL] 未配置 webhook URL")
        sys.exit(1)

    now = datetime.now(BJT)
    now_hhmm = f"{now.hour:02d}:{now.minute:02d}"

    # --test 模式：发送第 N 条提醒（用于验证）
    if "--test" in sys.argv:
        idx = sys.argv[sys.argv.index("--test") + 1] if len(sys.argv) > sys.argv.index("--test") + 1 else "1"
        reminders = config["reminders"][str(idx)]
        msg = reminders[now.timetuple().tm_yday % len(reminders)]
        print(f"[TEST] Level {idx} message: {msg}")
        result = send_webhook(webhook_url, msg)
        print(f"[OK] {result}")
        return

    # 匹配当前时间到 schedule 中的某个提醒
    schedule = config.get("schedule", [])
    matched = None
    for entry in schedule:
        if entry["time"] == now_hhmm:
            matched = entry
            break

    if not matched:
        # 不是提醒时间，静默退出（GitHub Actions 每 10 分钟触发一次检查）
        print(f"[SKIP] {now_hhmm} - 不在提醒时间表")
        return

    # 根据日期轮换消息内容，确保每天不重样
    level = str(matched["level"])
    reminders = config["reminders"][level]
    day_of_year = now.timetuple().tm_yday
    message = reminders[day_of_year % len(reminders)]

    result = send_webhook(webhook_url, message)
    print(f"[OK] {now.strftime('%Y-%m-%d %H:%M')} | Level {level} | {message}")


if __name__ == "__main__":
    main()
