from dataclasses import dataclass


@dataclass
class ColorScheme:
    name: str
    light_start: str
    light_end: str
    dark_start: str
    dark_end: str


SCHEMES: list[ColorScheme] = [
    ColorScheme("暖阳", "#FFF5E1", "#FFE4B5", "#4A3F30", "#3D3528"),
    ColorScheme("樱花", "#FFE4E1", "#FFB6C1", "#4A3035", "#3D282E"),
    ColorScheme("薄荷", "#E0FFF0", "#B2F2D8", "#2D4038", "#25352E"),
    ColorScheme("天空", "#E0F4FF", "#B8DFFF", "#2A3645", "#222E3D"),
    ColorScheme("薰衣草", "#F0E6FF", "#D4B8FF", "#352E45", "#2C263D"),
    ColorScheme("蜜桃", "#FFE8D0", "#FFD4A0", "#45382A", "#3D3025"),
    ColorScheme("抹茶", "#E8F5E0", "#C8E6B0", "#303A28", "#283522"),
    ColorScheme("雾蓝", "#E8EEFF", "#C8D8FF", "#2A2E3D", "#22283A"),
    ColorScheme("玫瑰", "#FFE8EC", "#FFC8D0", "#452E33", "#3D282E"),
    ColorScheme("月光", "#F5F0E8", "#E8E0D0", "#3D3830", "#353028"),
]


def get_scheme(index: int) -> ColorScheme:
    """按索引获取配色方案，越界则循环."""
    return SCHEMES[index % len(SCHEMES)]


def random_scheme_index() -> int:
    """生成随机配色索引."""
    import random
    return random.randint(0, len(SCHEMES) - 1)
