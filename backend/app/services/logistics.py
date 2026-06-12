"""
新竹限定物流驗證
區域配送僅限：新竹市、新竹縣（竹北市、竹東鎮、橫山鄉…）各區
"""

# 允許的地址前綴（台灣地址格式：縣市＋區）
ALLOWED_PREFIXES = [
    "新竹市",
    "新竹縣竹北市",
    "新竹縣竹東鎮",
    "新竹縣新埔鎮",
    "新竹縣關西鎮",
    "新竹縣湖口鄉",
    "新竹縣新豐鄉",
    "新竹縣芎林鄉",
    "新竹縣橫山鄉",
    "新竹縣北埔鄉",
    "新竹縣寶山鄉",
    "新竹縣峨眉鄉",
    "新竹縣尖石鄉",
    "新竹縣五峰鄉",
]


def validate_delivery_address(address: str) -> bool:
    """回傳 True 表示地址在配送範圍內"""
    return any(address.startswith(prefix) for prefix in ALLOWED_PREFIXES)


def get_address_error() -> str:
    return "區域配送僅限新竹市及新竹縣各鄉鎮市，請確認收件地址"
