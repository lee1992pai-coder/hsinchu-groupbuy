"""
綠界 ECPay 分帳金流服務
文件：https://developers.ecpay.com.tw/?p=7327
"""
import hashlib
import urllib.parse
from datetime import datetime, timezone

import httpx

from app.core.config import settings


def _check_mac_value(params: dict) -> str:
    """產生 CheckMacValue（綠界簽章）"""
    sorted_params = sorted(params.items())
    raw = "&".join(f"{k}={v}" for k, v in sorted_params)
    raw = f"HashKey={settings.ECPAY_HASH_KEY}&{raw}&HashIV={settings.ECPAY_HASH_IV}"
    encoded = urllib.parse.quote_plus(raw).lower()
    return hashlib.sha256(encoded.encode()).hexdigest().upper()


def build_payment_form(
    merchant_trade_no: str,
    total_amount: int,
    description: str,
    return_url: str,
    notify_url: str,
) -> dict:
    """
    建立綠界 AIO 付款表單參數。
    前端拿到這組參數後以 POST form 方式導到綠界付款頁。
    """
    trade_date = datetime.now(timezone.utc).strftime("%Y/%m/%d %H:%M:%S")
    params = {
        "MerchantID": settings.ECPAY_MERCHANT_ID,
        "MerchantTradeNo": merchant_trade_no,
        "MerchantTradeDate": trade_date,
        "PaymentType": "aio",
        "TotalAmount": str(total_amount),
        "TradeDesc": urllib.parse.quote(description),
        "ItemName": description,
        "ReturnURL": return_url,      # 後端接收付款結果
        "OrderResultURL": return_url, # 前端跳轉頁
        "ClientBackURL": return_url,
        "ChoosePayment": "ALL",
        "EncryptType": "1",
    }
    params["CheckMacValue"] = _check_mac_value(params)

    api_url = (
        "https://payment-stage.ecpay.com.tw/Cashier/AioCheckOut/V5"
        if settings.ECPAY_STAGE
        else settings.ECPAY_API_URL
    )
    return {"action_url": api_url, "fields": params}


def verify_payment_notify(form_data: dict) -> bool:
    """驗證綠界付款通知的 CheckMacValue"""
    received_mac = form_data.pop("CheckMacValue", "")
    expected_mac = _check_mac_value(form_data)
    return received_mac == expected_mac


async def query_trade_info(merchant_trade_no: str) -> dict:
    """查詢訂單狀態"""
    params = {
        "MerchantID": settings.ECPAY_MERCHANT_ID,
        "MerchantTradeNo": merchant_trade_no,
        "TimeStamp": str(int(datetime.now(timezone.utc).timestamp())),
    }
    params["CheckMacValue"] = _check_mac_value(params)

    query_url = (
        "https://payment-stage.ecpay.com.tw/Cashier/QueryTradeInfo/V5"
        if settings.ECPAY_STAGE
        else settings.ECPAY_QUERY_URL
    )
    async with httpx.AsyncClient() as client:
        resp = await client.post(query_url, data=params)
    result = dict(urllib.parse.parse_qsl(resp.text))
    return result


def calculate_split(gross: float, commission_rate: float) -> tuple[float, float]:
    """回傳 (平台抽成, 商家實收)，金額以元為單位（無條件捨去至整數）"""
    commission = int(gross * commission_rate)
    merchant_amount = int(gross) - commission
    return float(commission), float(merchant_amount)
