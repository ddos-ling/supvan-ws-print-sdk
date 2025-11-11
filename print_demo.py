#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""硕方打印机 SDK 使用示例

步骤:
1. 获取设备列表
2. 选择第一台设备路径 (如果存在)
3. 打印一页简单文本
4. 轮询状态直到状态变为 完成/终止 (State=4 或 3) 或超时
5. 演示终止打印 (可选)

运行前确保本地服务已启动，WebSocket 地址默认 ws://127.0.0.1:15268
"""
from __future__ import annotations

import time
from supvan_sdk import SupvanPrinterClient, SDKPrintSet


def main():
    client = SupvanPrinterClient(url="ws://127.0.0.1:15268")
    try:
        devices = client.get_device_paths()
        if not devices:
            print("未发现设备，请确认打印机已连接与服务端正常。")
            return
        device_path = devices[0].get("DevicePath")
        print(f"使用设备: {device_path}")

        # 打印一页文本
        print("发送打印任务...")
        client.print_text_label(
            text="HelloWorld", device_path=device_path,
            x=15.0, y=3.0, width=15.0, height=4.0,
            font_name="黑体", font_size_mm=4, align=1,
            print_set=SDKPrintSet(Height=30, Width=30, Threshold=240)
        )

        # 轮询状态: 0待机、2打印中、3终止、4完成
        print("轮询打印状态...")
        deadline = time.time() + 60  # 最多等待 60 秒
        last_state = None
        while time.time() < deadline:
            status = client.get_print_result(device_path)
            state = status.get("State")
            if state != last_state:
                print(f"状态变更: State={state} PrintDes={status.get('PrintDes','')} ErrorMsg={status.get('ErrorMsg','')}")
                last_state = state
            if state in (3, 4):
                print("打印结束。")
                break
            time.sleep(1.0)
        else:
            print("等待状态超时，尝试终止打印...")
            client.stop_print(device_path)
    finally:
        client.close()


if __name__ == "__main__":
    main()
