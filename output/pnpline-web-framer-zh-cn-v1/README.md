# PNPLINE 简体中文站

基于 PNPLINE Framer 英文版制作的独立简体中文站。项目包含本地图片、字体和背景视频，页面布局及视频滚动逻辑沿用英文版。

```sh
npm ci
npm run dev
```

本地访问 http://127.0.0.1:3213/ 。可运行 `npm run build` 生成生产构建。部署时可设置 `SITE_URL` 为正式站点源地址，供规范链接和结构化数据使用。

询价表单用于预览与校验。草稿仅存于当前浏览器标签页的会话存储。

## OSS 静态部署构建

```powershell
$env:SITE_URL = 'https://pnpline.cn'
$env:SITE_INDEXING = 'block'
npm run build:static
```

上传 `out/` 中的文件。构建默认关闭索引，正式上线并完成验证后，设置
`SITE_INDEXING=allow` 并重新构建。静态部署的隐私页路径为 `/privacy/`。
