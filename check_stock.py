import os
import requests
from bs4 import BeautifulSoup

URL = "https://www.rossmann.com.tr/rossmann-advent-calendar-2027-1-adet-p-kt26100299"
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
    ),
    "Accept-Language": "tr-TR,tr;q=0.9,en;q=0.8",
}

def send_telegram(message: str) -> None:
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "disable_web_page_preview": False,
    }
    resp = requests.post(api_url, json=payload, timeout=15)
    resp.raise_for_status()

def main() -> None:
    response = requests.get(URL, headers=HEADERS, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    visible_text = " ".join(soup.get_text().split()).lower()

    page_loaded_properly = ("rossmann" in visible_text) and ("advent calendar" in visible_text)
    if not page_loaded_properly:
        print("Sayfa beklenen ürün içeriğini döndürmedi (koruma veya eksik yanıt olabilir). Alarm verilmedi.")
        return

    out_of_stock_phrases = [
        "stokta yok",
        "tükendi",
        "stokta bulunmamaktadır",
    ]

    is_out_of_stock = any(phrase in visible_text for phrase in out_of_stock_phrases)

    if not is_out_of_stock:
        send_telegram(
            "🚨 Rossmann Advent Calendar 2027 stokta görünüyor!\n"
            f"Hemen kontrol et: {URL}"
        )
    else:
        print("Sayfa doğrulandı, ürün hala stokta yok.")

if __name__ == "__main__":
    main()
