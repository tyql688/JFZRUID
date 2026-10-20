<p align="center">
  <img src="ICON.png" width="192" height="192" alt="JFZRUID">
</p>

<h1 align="center">JFZRUID</h1>
<p align="center">疾风之刃插件 · 早柚核心扩展</p>

<p align="center">
  <a href="https://docs.sayu-bot.com/">Core 安装文档</a> ·
  <a href="https://github.com/Genshin-bots/gsuid_core">gsuid_core</a> ·
  <a href="CHANGELOG.md">更新记录</a>
</p>

JFZRUID 是 [早柚核心（GsCore）](https://github.com/Genshin-bots/gsuid_core)的疾风之刃插件。目前提供官网公告查询与群订阅，无需登录游戏账号。

## 丨功能

- 公告列表显示最新 5 条公告的标题、日期和 ID。
- 公告详情可查询最新公告或指定 ID，消息附原文链接。
- 公告文字自动转为简体，列表和详情使用 `pytakumi` 渲染。
- 群订阅每 10 分钟检查新公告；查询缓存保留 1 小时，可手动清理。
- 帮助图使用 Core 帮助系统，附查询和管理快捷按钮。

## 丨安装

运行环境为 Python `>=3.11,<4.0`。请先安装 GsCore，并连接机器人适配器。

1. 在 Core 根目录执行以下命令：

   ```sh
   git clone https://github.com/tyql688/JFZRUID.git gsuid_core/plugins/JFZRUID
   ```

2. 开启 Core 的「自动安装依赖」设置。
3. 重启 Core。
4. 向机器人发送 `jf帮助`。

如果关闭了「自动安装依赖」，请在 Core 根目录执行以下命令，再重启 Core：

```sh
uv pip install -r gsuid_core/plugins/JFZRUID/pyproject.toml
```

插件无需填写 API Key 或 Cookie。前缀、权限和启用状态可在 Core 的插件设置页修改。

## 丨常用命令

| 命令 | 功能 | 默认权限 |
| --- | --- | --- |
| `jf帮助` | 查看帮助图和快捷按钮 | 所有人 |
| `jf公告列表` | 查看最新 5 条公告 | 所有人 |
| `jf公告` | 查看最新公告详情 | 所有人 |
| `jf公告1020` | 查看 ID 为 1020 的公告 | 所有人 |
| `jf订阅公告` | 开启本群的新公告推送 | 群管理员或更高权限 |
| `jf取消订阅公告` | 关闭本群的公告推送 | 群管理员或更高权限 |
| `jf清理公告缓存` | 清理本插件的查询和图片缓存 | 群管理员或更高权限 |

`jf公告 1020` 也可查询详情。请将示例 ID 替换为 `jf公告列表` 中的官网 ID。

首次订阅只记录当前进度，之后按 ID 顺序推送新增公告。各群独立保存进度，重复订阅保留原进度。定时检查会刷新公告列表，不受 1 小时查询缓存限制。

`jf清理公告缓存` 清空所有群共用的查询和图片缓存，保留订阅记录和推送进度。
