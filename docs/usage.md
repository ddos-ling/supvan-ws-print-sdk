# 硕方打印机 SDK 用例说明

本文示例演示典型使用流程以及关键参数，并提供重要的依赖与合规提示。

## 重要说明（依赖与合规）
- 本程序基于官方提供的“supvanweb.exe”WebSocket 共享打印服务进行开发与联调；本项目不包含该服务程序。
- 请通过硕方官方渠道（客服/经销商/官网）获取 supvanweb.exe，并按官方文档完成安装与启动。
- 使用本程序时，请务必遵守相关法律法规和产品使用注意事项、使用限制等；本程序不对使用中造成的耗材损耗、设备损坏、数据丢失、业务中断等做保证。
- 默认服务地址：`ws://127.0.0.1:15268`；如需跨主机访问，请确保网络安全、权限控制与防火墙放行。

## 前置条件
- 已正确安装并启动官方 supvanweb.exe，且可通过浏览器或客户端连通对应端口。
- 系统具备访问 supvanweb.exe 的网络权限（本机或局域网）。
- 已安装 Python 3.8+，并在虚拟环境中安装项目依赖：`pip install -r requirements.txt`。

## 1. 初始化客户端
```python
from supvan_sdk import SupvanPrinterClient
client = SupvanPrinterClient()  # 默认 ws://127.0.0.1:15268
```

可修改地址:
```python
client = SupvanPrinterClient(url="ws://192.168.1.10:15268")
```

## 2. 获取设备列表
```python
devices = client.get_device_paths()
if not devices:
    raise RuntimeError("未检测到设备")
for d in devices:
    print(d["DeviceName"], d["DevicePath"], d.get("MaxDotValue"), d.get("DPI"))
```

## 3. 打印文本标签
使用快捷方法 `print_text_label` (默认不等待 DoPrint 回包):
```python
from supvan_sdk import SDKPrintSet
client.print_text_label(
    text="HelloWorld",
    device_path=devices[0]["DevicePath"],
    print_set=SDKPrintSet(Height=30, Width=50, Threshold=240),
    expect_reply=False  # 默认即可，不等待服务端立即返回
)
```

## 4. 自定义复杂页面
```python
from supvan_sdk import SDKPrintPage, SDKPrintPageDrawObject, SDKPrintSet
objs = [
    SDKPrintPageDrawObject(Content="HELLO", X=5, Y=5, Width=20, Height=5, FontName="黑体", FontSize="6", Align=0, Format="TEXT"),
    SDKPrintPageDrawObject(Content="123456789012", X=5, Y=12, Width=30, Height=10, Format="CODE_128"),
]
page = SDKPrintPage(DrawObjects=objs)
client.do_print([page], print_set=SDKPrintSet())
"""如果你的服务端实现会对 DoPrint 返回结果，可改为:
client.do_print([page], print_set=SDKPrintSet(), expect_reply=True, timeout=30.0)
"""
```

## 5. 查询状态与轮询
```python
status = client.get_print_result(devices[0]["DevicePath"])
print("State=", status.get("State"), "PrintDes=", status.get("PrintDes"))
```

轮询直到完成:
```python
import time
while True:
    st = client.get_print_result(devices[0]["DevicePath"])
    if st.get("State") in (3,4):
        break
    time.sleep(1)
```

## 6. 终止打印
```python
client.stop_print(devices[0]["DevicePath"])  # 指定设备
# 或终止全部
client.stop_print()
```

## 7. 异常处理
所有服务端错误 (ResultCode != 0) 会抛出 `SupvanError`:
```python
from supvan_sdk import SupvanError
try:
    client.get_device_paths()
except SupvanError as e:
    print("服务端错误", e.result_code, e)
```

## 8. 常见字段速查
| 字段 | 含义 |
|------|------|
| State | 0待机、1检测、2打印中、3终止、4完成、5复位 |
| PrintDes | 状态描述信息 |
| DevPrintedPageCount | 本轮已打印页数 |
| PrintPageTotalCount | 本轮待打印总页数 |

## 9. 提示与最佳实践
- 建议打印后开始轮询，频率 1s；批量打印可降低频率。
- `FontSize` 必须字符串形式。
- 条形码、二维码 Content 内容格式请符合设备支持规范。
- 长文本可使用 `AutoReturn=True` 实现自动换行。
- 如果业务需要等待 DoPrint 回包（某些定制服务端会返回一次确认），请传 `expect_reply=True` 并设置更长 `timeout`。

### 故障排查（FAQ）
1. 连接失败或超时：
    - 确认 supvanweb.exe 已启动并监听正确地址与端口（默认 127.0.0.1:15268）。
    - 检查 Windows 防火墙或安全软件是否放行对应端口与应用。
    - 跨主机访问时，确认服务端绑定地址不是仅 127.0.0.1，且路由/ACL 放行。
2. 查询不到设备：
    - 确认打印机驱动安装完成并被 supvanweb.exe 识别；更换 USB 口尝试。
    - 尝试重启服务端与设备，检查线缆与供电。
3. 打印异常或乱码：
    - 确认字体在系统中已安装，字段类型与协议一致（如 FontSize 需为字符串）。
    - 检查二维码/条码内容格式是否符合设备要求。

## 10. 下一步扩展
- 增加 asyncio 版本
- 增加自动重连与心跳检测
- 支持图片/二维码编码辅助函数

---
本 SDK 示例可直接嵌入业务系统，按需裁剪。使用本程序即表示您理解并接受前述依赖与免责声明条款。

### 运行示例
可直接运行仓库根目录下的示例脚本：

```bash
python print_demo.py
```