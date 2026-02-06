import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

URL = "https://www.giet.edu/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

print(f"Fetching {URL}...")
try:
    response = requests.get(URL, headers=HEADERS, timeout=10)
    print(f"Status: {response.status_code}")
    soup = BeautifulSoup(response.content, 'html.parser')
    
    print("\n--- SEARCHING FOR 'NOTICE' LINKS ---")
    links = soup.find_all('a', href=True)
    found_any = False
    for link in links:
        text = link.get_text(" ", strip=True).lower()
        href = link['href']
        if any(kw in text for kw in ['notice', 'exam', 'circular', 'news', 'announcement']):
            full_url = urljoin(URL, href)
            print(f"MATCH: [{text}] -> {full_url}")
            found_any = True
            
    if not found_any:
        print("No obvious notice links found on homepage.")
        
except Exception as e:
    print(f"Error: {e}")
