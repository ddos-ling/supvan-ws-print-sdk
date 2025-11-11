# 硕方打印机 WebSocket Python SDK

一个基于 WebSocket 的轻量级 Python 封装，支持获取设备列表、查询状态、发起打印与终止打印。

## 重要说明（依赖与合规）
- 本程序是在官方提供的“supvanweb.exe”WebSocket 共享打印服务上进行开发与联调的。
- 本项目不包含该服务程序 supvanweb.exe。请通过硕方官方渠道（客服/经销商/官网）获取并按官方文档安装与启动。
- 使用本程序时，务必遵守相关法律法规以及产品使用注意事项、使用限制等；确保具备相应的使用授权与场景合规性。
- 本程序为开发示例与集成 SDK，不对使用过程中造成的耗材损耗、设备损坏、数据丢失、业务中断等承担保证或责任。请先在测试环境充分验证后再用于生产环境。

默认服务地址：`ws://127.0.0.1:15268`（如需远程访问，请确保网络与权限设置安全可控）。

## 环境要求
- 操作系统：建议 Windows（需能安装并运行官方 supvanweb.exe 服务）
- Python：3.8 及以上
- 网络：可访问 supvanweb.exe 所在主机与端口（默认 15268），注意本机/域策略、防火墙放行

## 安装依赖

确保已有虚拟环境，并安装依赖:

```bash
pip install -r requirements.txt
```

> 当前依赖: `websocket-client`

## 快速开始

```python
from supvan_sdk import SupvanPrinterClient, SDKPrintSet

client = SupvanPrinterClient()  # 默认 ws://127.0.0.1:15268

# 1. 获取设备
devices = client.get_device_paths()
if not devices:
    raise SystemExit("未发现设备")
path = devices[0]["DevicePath"]

# 2. 打印一页文本
client.print_text_label(
    text="HelloWorld",
    device_path=path,
    print_set=SDKPrintSet(Height=30, Width=50, Threshold=240)
)

# 3. 查询状态
status = client.get_print_result(path)
print("状态:", status)

client.close()
```

或运行示例:

```bash
python print_demo.py
```

## API 说明

### SupvanPrinterClient(url="ws://127.0.0.1:15268", timeout=5.0, recv_timeout=10.0)
- `get_device_paths()` -> List[Dict]
- `get_print_result(device_path: str|None)` -> Dict
- `do_print(pages: List[SDKPrintPage], print_set: SDKPrintSet, device_path: str|None, timeout: float|None = None, expect_reply: bool = False)`
- `stop_print(device_path: str|None)`
- `print_text_label(text, x, y, width, height, ..., timeout: float|None = None, expect_reply: bool = False)` 快捷文本打印

返回值中统一采用服务端 JSON 协议：`ResultCode=0` 表示成功；非 0 会抛出 `SupvanError`。

说明：
- 某些实现的 `DoPrint` 不会返回应答或不会立即返回，本 SDK 默认不等待（`expect_reply=False`）。
- 如需等待服务端回包，可传 `expect_reply=True` 并适当增大 `timeout` 或 `recv_timeout`。

### 数据模型
- `SDKPrintSet` 打印配置，字段与默认值参考协议文档
- `SDKPrintPage` 打印页，包含 `DrawObjects`
- `SDKPrintPageDrawObject` 绘制对象：文本、条码、二维码、线条等

> 所有模型提供 `to_dict()` 用于序列化。

## 常见状态码与字段
- 打印状态字段 `State`：0待机、1检测设备、2打印中、3打印终止、4打印完成、5复位设备
- 错误统一通过抛出异常 `SupvanError(message, result_code)`

## 轮询建议
打印后可每 1 秒调用 `get_print_result` 直到状态进入终止/完成或超时。

## 注意事项
1. 字体名需本地已安装，否则可能渲染失败。
2. 服务端地址请确保可访问；Windows 防火墙可能阻止连接。
3. 终止打印可能不会立即生效，会等待当前页完成。
4. `FontSize` 按协议需要字符串形式。
5. 图片、二维码等高级绘制需按服务端支持格式填入 `Format` 与 `Content`。
6. 如需从其他主机访问 supvanweb.exe，请正确配置服务端监听地址、端口与防火墙策略，并在受控网络内使用。

## 扩展方向
- 增加异步实现 (websockets / asyncio)
- 增加队列与重试策略
- 支持事件回调与自动状态轮询

## 免责声明
- 本项目不打包、不分发 supvanweb.exe 服务端程序；仅提供对其 WebSocket 协议的 Python 封装示例。
- 请通过官方渠道获取、安装与使用 supvanweb.exe，并严格遵循官方的产品说明、使用限制与安全指引。
- 因使用本项目或与其相关的示例代码造成的直接或间接损失（包括但不限于耗材损耗、设备损坏、数据丢失、业务中断），本项目不承担任何保证或责任。

## 许可证
本项目的授权条款请参见仓库根目录的 `LICENSE` 文件；在遵守相应许可的前提下，您可以按需修改并集成到您的系统中。

## 支持与反馈
- 如需获取 supvanweb.exe，请联系硕方官方客服/经销商或访问官方渠道。
- 如对本 SDK 有问题或建议，欢迎通过项目 Issue 进行反馈与交流。
