class SupvanError(Exception):
    """通用异常：服务返回非 0 结果码或通讯失败。"""

    def __init__(self, message: str, result_code: int | None = None):
        super().__init__(message)
        self.result_code = result_code
