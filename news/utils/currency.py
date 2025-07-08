import requests
import xml.etree.ElementTree as ET

def get_usd_kzt_rate():
    url = "https://nationalbank.kz/rss/rates_all.xml"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        for item in root.findall('.//item'):
            title = item.find('title').text
            if title == 'USD':
                rate = item.find('description').text
                return float(rate.replace(',', '.'))
        return None
    except Exception:
        return None 