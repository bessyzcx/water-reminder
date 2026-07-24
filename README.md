# 喝水提醒 - 企业微信群机器人

工作日自动推送 7 次喝水提醒到企业微信群，内容每天不重样，多语言轮换。

## 提醒时刻表

| 次序 | 时间  | 规则 | 示例 |
|------|-------|------|------|
| 1 | 08:50 | 1字 + 1个! | 喝! / 水! / H2O! |
| 2 | 09:40 | 2字 + 2个! | 喝水!! / Drink!! / 물!! |
| 3 | 10:30 | 3字 + 3个! | 该喝水!!! / 飲む!!! / boire!!! |
| 4 | 12:55 | 4字 + 4个! | 该喝水啦!!!! / Hydrate now!!!! |
| 5 | 14:10 | 短句 + 5个! | 起来倒杯水吧!!!!! / Water break time!!!!! |
| 6 | 15:40 | 短句 + 6个! | 今天喝够水了吗？!!!!!! / Stay hydrated!!!!! |
| 7 | 17:20 | 短句 + 7个! | 今天最后冲刺多喝水!!!!!!! / Last call for H2O!!!!!!! |

所有时间均避开整点（避免与会议冲突）。每天同一时刻的提醒内容按日期轮换，中/英/日/韩/法/德多语言混排。

## 部署步骤

### 1. 创建 GitHub 仓库

```bash
cd /Users/chixiang/geelyclaw/project
git init
git add .
git commit -m "init: 喝水提醒机器人"
git remote add origin https://github.com/你的用户名/仓库名.git
git push -u origin main
```

### 2. 配置 Webhook Secret

1. 进入 GitHub 仓库 → **Settings** → **Secrets and variables** → **Actions**
2. 点击 **New repository secret**
3. Name: `WECOM_WEBHOOK_URL`
4. Value: 你的 webhook 地址
5. 点击 **Add secret**

### 3. 完成

配置好后自动运行。GitHub Actions 在工作日每 10 分钟检查一次，到了提醒时间就发送对应内容。

## 自定义

### 修改提醒时间

编辑 `config.json` 中的 `schedule` 数组，同时更新 `.github/workflows/send-message.yml` 中的 cron 表达式。

cron 使用 UTC 时间，北京时间 = UTC + 8。例如北京时间 14:10 = UTC 06:10。

### 修改提醒内容

编辑 `config.json` 中的 `reminders` 对象。每个级别是一个数组，脚本按 `日期 % 数组长度` 轮换选取。数组越长，重复周期越长。

### 手动触发

进入 GitHub 仓库 → **Actions** → **喝水提醒** → **Run workflow**，可指定提醒级别（1-7）进行测试。

### 本地测试

```bash
# 设置 webhook 环境变量后测试
WECOM_WEBHOOK_URL="你的webhook地址" python3 send.py --test 1
```

## 技术细节

- 纯 Python 标准库，无需安装任何依赖
- GitHub Actions 免费额度 2000 分钟/月，每次运行约 10 秒，月消耗约 10 分钟
- 脚本在非提醒时间被触发时立即退出（SKIP），不产生额外开销
