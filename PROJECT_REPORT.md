# S4 Watch Dashboard 项目报告

生成日期：2026-07-17  
项目目录：`D:\DevProject\watch_dashboard\watch_dashboard`  
当前目标设备：Xiaomi Watch S4（466 × 466 圆形屏幕）

## 1. 项目结论

项目已收敛为 S4 专用版本，正式入口为 `pages/s4`，提供天气、运动、健康三个可横向滑动页面。指南针页面、状态变量、传感器订阅和 S4 样式均已删除；manifest 中只有 S4 页面可路由。

最终工程能够完成 AIoT/Vela 编译、生成 RPK、安装至 `xiaomi_s4` 模拟器并通过三页横滑截图回归。天气页的体感、湿度、风速已改为水平排列，未发现文字截断、组件越界或页面黑屏。

## 2. 当前功能

### 2.1 天气页

- 重庆实时天气标题与写实雷雨背景。
- 当前温度和天气状态。
- 水平排列的体感、湿度、风速胶囊。
- 今天、明天、周日三日天气预报。
- 圆形屏幕底部的大圆角预报底座。
- 代码保留定位、天气请求、网络状态和缓存能力。

水平胶囊在 466px 画布中的实测范围：

| 指标 | 左边界 | 右边界 | 结果 |
| --- | ---: | ---: | --- |
| 体感 | 约 25px | 约 157px | 安全 |
| 湿度 | 约 161px | 约 289px | 安全 |
| 风速 | 约 297px | 约 443px | 安全 |

最外侧仍保留约 23px 安全空间，没有横向溢出。

### 2.2 运动页

- 活动、锻炼、站立三色运动环。
- 热量、锻炼分钟数、站立小时数。
- 步数、距离、爬楼和站立提醒。
- 下半部分使用黑色遮罩和两排胶囊卡片收口，避免圆环越过卡片区域。
- 两排卡片高度为 54px，并放大图标、数值和单位文字，以填充圆屏下半部留白。

### 2.3 健康页

- 当前心率和历史测量时间。
- 血氧、呼吸、腕温、HRV。
- 指标胶囊根据圆形屏幕宽度逐级缩短，减少圆盘边缘裁切。
- 已移除底部“模拟预览”胶囊，仅保留健康数据和分页指示器。

## 3. 页面与运行架构

- 设计宽度：466。
- 设备类型：watch。
- 正式入口：`pages/s4`。
- 正式路由数量：1。
- Swiper 页面数量：3。
- 页面顺序：天气 → 运动 → 健康。
- S4 页面不包含 `@media`、倾斜 transform 或 Band Pro 分支。
- S4 页面指南针引用数量：0。

旧的 `pages/index`、`pages/detail` 和 `pages/feasibility` 源码仍保留在仓库中作为历史参考，但已经从 manifest 路由表移除，正式应用无法导航到这些页面。

`system.router` feature 仍保留在 manifest。原因是 AIoT 构建器会扫描未路由的历史 `detail.ux`，该文件仍导入 `@system.router`；删除 feature 会导致全工程构建失败。这个声明不会开放旧页面。

## 4. 数据模式与系统能力

当前 `previewMode` 为 `true`，默认使用与设计图一致的固定预览数据，保证视觉验收稳定。

将 `previewMode` 改为 `false` 后，代码会启用：

- Open-Meteo 天气请求。
- BigDataCloud 反向地理编码。
- 定位权限。
- 网络状态监听。
- 本地天气、位置和步数缓存。
- 加速度计步数估算。

已声明的系统 feature：

- `system.router`
- `system.sensor`
- `system.fetch`
- `system.geolocation`
- `system.storage`
- `system.network`

已声明定位权限：`hapjs.permission.LOCATION`。

允许访问的域名：

- `api.open-meteo.com`
- `api.bigdatacloud.net`

## 5. 项目完整性检查

### 5.1 文件与资源

- UX 文件：9 个（包括保留的历史页面和通用组件）。
- JavaScript 工具脚本：1 个。
- Python 资源处理脚本：3 个。
- PNG 图片：38 个。
- 全项目静态资源引用：39 处。
- 缺失静态资源：0。
- S4 当前使用的图片引用：14 处。
- 检测到的乱码替换字符：0。

旧的 `common/images/compass/dial-scale.png` 仍是未引用资源，并会被当前打包工具复制进 RPK。它不包含可执行功能，可在后续资源瘦身时删除。

### 5.2 JSON 与脚本

- 检查 JSON：10 个。
- JSON 解析失败：0。
- `package-lock.json` 可由 Node.js 正常解析。
- `tools/capture_visual_regression.js` 通过 Node 语法检查。
- 3 个 Python 脚本通过 AST 语法解析。

检查期间发现根目录 `jsconfig.json` 原本是 0 字节空文件，已修复为合法的最小 JSON：`{}`。

### 5.3 依赖

直接开发依赖：

- `aiot-toolkit@2.0.5`
- `@aiot-toolkit/jsc@1.0.8`

`npm ls --depth=0` 正常完成，未发现缺失的直接依赖。

## 6. 构建与模拟器测试

### 6.1 构建

执行命令：

```text
npm.cmd run build
```

结果：成功。AIoT toolkit 完成 JavaScript 编译、资源复制、RPK 打包和资源检查。

最终产物：

```text
dist/com.application.watch.dashboard.debug.1.0.2.rpk
```

当前产物为 debug 签名包，正式发布前仍需执行 release 签名流程。

### 6.2 S4 模拟器

测试设备：`xiaomi_s4`。  
测试动作：推送最新 RPK、安装、启动应用、模拟鼠标连续左滑、逐页截图。

| 页面 | 截图大小 | SHA-256 前缀 | 结果 |
| --- | ---: | --- | --- |
| 天气 | 95,316 bytes | `cb3b65235b22` | 通过 |
| 运动 | 35,731 bytes | `a0f96d4cb2fb` | 通过 |
| 健康 | 37,580 bytes | `b6e16e333476` | 通过 |

三个页面哈希均不同，证明横滑确实切换了页面；所有截图均超过黑屏判定阈值。

最终天气截图：

```text
build/s4-filled-activity/xiaomi_s4/page-1.png
```

完整回归报告：

```text
build/s4-filled-activity/xiaomi_s4/report.json
```

## 7. 已知限制

1. 默认使用预览数据。要验证真实天气和运动数据，需要把 `previewMode` 改为 `false` 并在真机授权定位。
2. 加速度计计步是演示级估算，不等同于系统健康服务的正式步数。
3. 当前自动截图通过模拟器 gRPC 鼠标事件完成，尚未覆盖长时间运行、断网恢复和定位拒绝等异常场景。
4. 项目原有 ESLint 配置依赖旧版 UX 解析方式和已移出的 `codeframe` formatter，不能作为当前 `.ux` 文件的可靠检查器；本次以 AIoT 正式编译器、Node/Python 语法检查和模拟器回归为准。
5. 仓库保留历史多设备源码和部分未使用图片，功能不受影响，但会增加维护与包体积成本。

## 8. 维护建议

1. 视觉验收完成后，将 S4 页面拆分为天气、运动、健康三个子组件，降低单文件维护成本。
2. 若确定永久不再支持旧设备，可删除未路由页面、旧通用组件和指南针图片，再同步精简 manifest feature。
3. 为真实数据模式增加定位拒绝、网络超时、缓存过期和天气接口异常测试。
4. 发布前更新版本号、配置正式签名并执行 `npm run release`。
5. 后续每次调整布局后运行：

```text
npm.cmd run build
node tools/capture_visual_regression.js xiaomi_s4 build/final-project-check
```

## 9. 交付文件

- S4 主页面：`src/pages/s4/s4.ux`
- 应用配置：`src/manifest.json`
- 回归脚本：`tools/capture_visual_regression.js`
- 项目说明：`README.md`
- 项目会话记录：`PROJECT_SESSION.md`
- 本项目报告：`PROJECT_REPORT.md`
- 安装包：`dist/com.application.watch.dashboard.debug.1.0.2.rpk`
- 最终截图与报告：`build/s4-filled-activity/xiaomi_s4/`
