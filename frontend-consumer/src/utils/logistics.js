const ALLOWED = [
  '新竹市', '新竹縣竹北市', '新竹縣竹東鎮', '新竹縣新埔鎮',
  '新竹縣關西鎮', '新竹縣湖口鄉', '新竹縣新豐鄉', '新竹縣芎林鄉',
  '新竹縣橫山鄉', '新竹縣北埔鄉', '新竹縣寶山鄉', '新竹縣峨眉鄉',
]

export function validate_delivery_address(addr) {
  return ALLOWED.some((p) => addr.startsWith(p))
}
