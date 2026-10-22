# 0.1.0

- **✨ 新增** `jf公告列表` 显示最新 5 条公告，`jf公告` 显示最新详情，`jf公告ID` 查询指定公告。[`150af73`](https://github.com/tyql688/JFZRUID/commit/150af73)
- **✨ 新增** 公告使用 `pytakumi` 渲染图片，标题和正文通过 OpenCC 转为简体，详情附原文链接。[`150af73`](https://github.com/tyql688/JFZRUID/commit/150af73)
- **✨ 新增** 群管理员可以订阅或取消公告推送；插件每 10 分钟检查一次，各群独立保存推送进度。[`150af73`](https://github.com/tyql688/JFZRUID/commit/150af73)
- **✨ 新增** 查询数据和图片缓存 1 小时，`jf清理公告缓存` 可手动清空；定时检查主动刷新列表。[`150af73`](https://github.com/tyql688/JFZRUID/commit/150af73)
- **✨ 新增** `jf帮助` 使用 Core 帮助图和快捷按钮，插件图标显示在帮助图及插件帮助一览中。[`150af73`](https://github.com/tyql688/JFZRUID/commit/150af73)
- **🐛 修复** 公告详情显示官网 `img.fxegames.com` 提供的配图。
- **🎨 调整** 公告正文使用深棕色，加粗的重点文字统一使用深红色。
- **🎨 调整** 公告详情清理纯空段落，正文段间距统一为 16px，行高设为 1.7 倍，配图沿用所在段落的间距。
