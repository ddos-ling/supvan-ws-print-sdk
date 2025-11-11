from __future__ import annotations

import json
import threading
import time
from dataclasses import asdict
from typing import Any, Dict, List, Optional, Callable

from .models import SDKPrintSet, SDKPrintPage
from .exceptions import SupvanError

try:
    import websocket  # websocket-client 库
    from websocket import WebSocketTimeoutException
except ImportError as e:  # pragma: no cover
    raise RuntimeError("缺少 websocket-client 依赖，请先安装: pip install websocket-client") from e


class SupvanPrinterClient:
    """硕方打印机 WebSocket SDK 客户端封装。

    基于文档的四类 Action: GetDevicePaths, GetPrintResult, DoPrint, StopPrint.
    提供同步调用方法；内部维持连接。服务端地址示例: ws://127.0.0.1:15268
    """

    def __init__(self, url: str = "ws://127.0.0.1:15268", timeout: float = 5.0, recv_timeout: float = 10.0, auto_connect: bool = True):
        """
        :param url: WebSocket 服务地址，如 ws://127.0.0.1:15268
        :param timeout: 连接超时（秒）
        :param recv_timeout: 默认接收超时（秒），用于等待服务端响应
        :param auto_connect: 是否在构造时自动连接
        """
        self.url = url
        self.timeout = float(timeout)
        self.recv_timeout = float(recv_timeout)
        self._ws: Optional[websocket.WebSocket] = None
        self._lock = threading.Lock()
        if auto_connect:
            self.connect()

    # ---------------- Connection -----------------
    def connect(self):
        if self._ws:
            return
        try:
            self._ws = websocket.create_connection(self.url, timeout=self.timeout)
            # 为后续 recv 设置默认的等待时长
            try:
                self._ws.settimeout(self.recv_timeout)
            except Exception:
                pass
        except Exception as e:
            raise SupvanError(f"无法连接到 {self.url}: {e}")

    def close(self):
        if self._ws:
            try:
                self._ws.close()
            finally:
                self._ws = None

    # ---------------- Low level send/recv -----------------
    def _ensure(self):
        if not self._ws:
            raise SupvanError("WebSocket 未连接")

    def _send_action(self, action: str, content: Dict[str, Any], recv_timeout: Optional[float] = None,
                     expect_reply: bool = True):
        self._ensure()
        payload = json.dumps({"Action": action, "Content": content}, ensure_ascii=False)
        with self._lock:
            # 发送请求
            assert self._ws is not None  # 类型静态提示
            self._ws.send(payload)
            if not expect_reply:
                # 某些 Action（例如 DoPrint）不会立即或根本不返回应答，直接返回 None
                return None
            # 处理临时接收超时（websocket-client 暴露 settimeout/recv）
            if recv_timeout is not None:
                try:
                    self._ws.settimeout(recv_timeout)
                except Exception:
                    pass
            try:
                raw = self._ws.recv()
            except (WebSocketTimeoutException, TimeoutError) as e:
                raise SupvanError(
                    f"等待服务端响应超时（action={action}, timeout={recv_timeout or self.recv_timeout}s）。"
                ) from e
            finally:
                if recv_timeout is not None:
                    try:
                        self._ws.settimeout(self.recv_timeout)
                    except Exception:
                        pass

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            raise SupvanError(f"返回非 JSON: {raw}") from e
        if data.get("ResultCode") != 0:
            raise SupvanError(data.get("ErrorMsg", "未知错误"), result_code=data.get("ResultCode"))
        return data.get("ResultValue")

    # ---------------- Public API -----------------
    def get_device_paths(self, timeout: Optional[float] = None) -> List[Dict[str, Any]]:
        """获取设备列表。"""
        return self._send_action("GetDevicePaths", {}, recv_timeout=timeout) or []

    def get_print_result(self, device_path: str | None = None, timeout: Optional[float] = None) -> Dict[str, Any]:
        content = {"DevicePath": device_path or ""}
        return self._send_action("GetPrintResult", content, recv_timeout=timeout) or {}

    def do_print(self, pages: List[SDKPrintPage], print_set: SDKPrintSet, device_path: str | None = None,
                 timeout: Optional[float] = None, expect_reply: bool = False) -> Any:
        content = {
            "DevicePath": device_path or "",
            "PrintSet": print_set.to_dict(),
            "PrintPages": [p.to_dict() for p in pages],
        }
        # 默认不等待服务端回复（部分实现不会回包）。如需等待可传 expect_reply=True。
        if not expect_reply:
            return self._send_action("DoPrint", content, expect_reply=False)
        # 若明确需要等待，则允许更长等待
        recv_timeout = timeout if timeout is not None else max(self.recv_timeout, 20.0)
        return self._send_action("DoPrint", content, recv_timeout=recv_timeout, expect_reply=True)

    def stop_print(self, device_path: str | None = None, timeout: Optional[float] = None) -> Any:
        content = {"DevicePath": device_path or ""}
        return self._send_action("StopPrint", content, recv_timeout=timeout)

    # ---------------- Helper high-level -----------------
    def print_text_label(self, text: str, x: float = 15.0, y: float = 3.0, width: float = 15.0, height: float = 4.0,
                          device_path: str | None = None, print_set: Optional[SDKPrintSet] = None,
                          font_name: str = "黑体", font_size_mm: int = 4, align: int = 1,
                          timeout: Optional[float] = None, expect_reply: bool = False) -> Any:
        from .models import SDKPrintPageDrawObject
        if not print_set:
            print_set = SDKPrintSet()
        obj = SDKPrintPageDrawObject(
            X=x, Y=y, Width=width, Height=height,
            Content=text, FontName=font_name, FontSize=str(font_size_mm), Align=align, Format="TEXT"
        )
        page = SDKPrintPage(DrawObjects=[obj])
        return self.do_print([page], print_set=print_set, device_path=device_path, timeout=timeout, expect_reply=expect_reply)

    # ---------------- Context manager -----------------
    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()


__all__ = [
    "SupvanPrinterClient",
]
