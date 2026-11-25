import os
import time
import requests
from bs4 import BeautifulSoup

URL = "https://www.rossmann.com.tr/rossmann-advent-calendar-2027-1-adet-p-kt26100299"
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

INTERVAL_SECONDS = 300  # 5 dakika = 300 saniye
MAX_RUNTIME_SECONDS = 5 * 3600 + 50 * 60  # GitHub 6 saat limitinden önce güvenli kapanış

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
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

def check_once() -> None:
    response = requests.get(URL, headers=HEADERS, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    visible_text = " ".join(soup.get_text().split()).lower()

    page_loaded_properly = ("rossmann" in visible_text) and ("advent calendar" in visible_text)
    if not page_loaded_properly:
        print("Sayfa beklenen ürün içeriğini döndürmedi. Alarm verilmedi.")
        return

    out_of_stock_phrases = [
        "stokta olduğunda bana bildir",
        "bana bildir",
        "stokta yok",
        "tükendi",
    ]

    is_out_of_stock = any(phrase in visible_text for phrase in out_of_stock_phrases)

    if is_out_of_stock:
        print("Sayfa doğrulandı, ürün hala stokta yok.")
    else:
        send_telegram(
            "🚨 Rossmann Advent Calendar 2027 STOKTA OLABİLİR!\n"
            f"Hemen kontrol et: {URL}"
        )

def main() -> None:
    start_time = time.monotonic()
    while True:
        try:
            check_once()
        except Exception as exc:
            print(f"Kontrol sırasında hata oluştu: {exc}")

        elapsed = time.monotonic() - start_time
        if elapsed + INTERVAL_SECONDS >= MAX_RUNTIME_SECONDS:
            print("Güvenli süre sınırına yaklaşıldı, döngü sonlandırılıyor.")
            break

        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
