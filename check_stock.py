import os
import requests
from bs4 import BeautifulSoup

URL = "https://www.rossmann.com.tr/rossmann-advent-calendar-2027-1-adet-p-kt26100299"
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

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

def main() -> None:
    response = requests.get(URL, headers=HEADERS, timeout=20)
    print("HTTP Status:", response.status_code)
    print("HTML Length:", len(response.text))

    soup = BeautifulSoup(response.text, "html.parser")
    visible_text = " ".join(soup.get_text().split()).lower()

    print("Rossmann var mi:", "rossmann" in visible_text)
    print("Advent calendar var mi:", "advent calendar" in visible_text)
    print("Bildir ifadesi var mi:", "bana bildir" in visible_text or "stokta olduğunda" in visible_text)
    print("Metin onizleme:", visible_text[:600])

    # Şimdilik yanlış alarm vermesin diye mesaj göndermeyi kapalı tutuyoruz
    if ("bana bildir" in visible_text) or ("stokta olduğunda" in visible_text):
        print("SONUC: Hala stokta yok.")
    else:
        print("SONUC: 'bana bildir' metni bulunamadi (ya stok acildi ya da sayfa JS ile yukleniyor).")

if __name__ == "__main__":
    main()
