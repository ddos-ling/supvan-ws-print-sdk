from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any


@dataclass
class SDKPrintPageDrawObject:
    # 基础
    AntiColor: bool = False
    Align: int = 0  # 0=左,1=中,2=右
    X: float = 0.0
    Y: float = 0.0
    Width: float = 0.0
    Height: float = 0.0

    # 文本/图形
    Content: str = ""
    FontName: str = "平方字体"
    FontStyle: int = 0
    FontSize: str = "0"  # 单位 mm，接口要求为字符串
    AutoReturn: bool = False
    Format: str = ""  # TEXT, QRCODE, CODE_128, EAN_13, Image, LINE

    # 其他
    ColumnIndex: int = -1
    X1: int = 0  # 线条终点 X（mm）
    Y1: int = 0  # 线条终点 Y（mm）

    def to_dict(self) -> Dict[str, Any]:
        # Direct return without intermediate variable for better performance
        return asdict(self)


@dataclass
class SDKPrintPage:
    Rotate: int = 0  # 0=不旋转, 3=180°
    Width: int = 20  # mm (仅部分机型使用)
    Repeat: int = 1
    ExcelFilePath: str = ""
    DrawObjects: List[SDKPrintPageDrawObject] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "Rotate": self.Rotate,
            "Width": self.Width,
            "Repeat": self.Repeat,
            "ExcelFilePath": self.ExcelFilePath,
            "DrawObjects": [o.to_dict() for o in self.DrawObjects],
        }


@dataclass
class SDKPrintSet:
    # 基础走纸/介质
    Direction: int = 0  # 0上 1下 2左 3右
    PaperType: int = 1  # 0连续、1间隙、2中间黑标、5黑标卡纸
    Height: int = 30  # mm（走纸方向）
    Width: int = 50   # mm（打印头方向）
    Gap: int = 3

    # 打印参数
    Speed: int = 60
    Deepness: int = 4  # 0-9
    Copy: int = 1
    OneByOne: bool = True
    MaxDotValue: int = 384
    DPI: float = 8.0
    OffsetH: int = 0
    OffsetV: int = 0

    # 材料/边距/检测
    MaterialCode: int = 3  # 1连续贴纸、2有孔贴纸、3普通标牌、4=2mm厚、5=3mm厚
    MaterialHeightmm: float = 30.0
    MaterialWidthmm: float = 50.0
    MarginLeft: float = 0.0
    MarginRight: float = 0.0
    HoleWidth: float = 0.0

    # 其他
    PrintHeightdot: int = 60
    Interval: int = 1
    CutType: int = 1      # 0=全无 1=划线 2=半切
    CutDeepness: int = 4  # 固定值：4
    RIBBONType: int = 0   # 0热转印 1热敏（MP5056）
    Threshold: int = 240  # 0-255 越高越深

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
