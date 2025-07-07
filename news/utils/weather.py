import requests

def get_almaty_weather():
    api_key = "00665463193f99ca4289ea01d7b3f069"
    city = "Almaty"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        weather = {
            "temp": data["main"]["temp"],
            "description": data["weather"][0]["description"],
            "icon": data["weather"][0]["icon"],
            "city": data["name"]
        }
        return weather
    except Exception:
        return None 