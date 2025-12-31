import pandas as pd
import requests

URLS = {
    "obesity_adults": "https://ghoapi.azureedge.net/api/NCD_BMI_30C",
    "obesity_children": "https://ghoapi.azureedge.net/api/NCD_BMI_PLUS2C",
    "malnutrition_adults": "https://ghoapi.azureedge.net/api/NCD_BMI_18C",
    "malnutrition_children": "https://ghoapi.azureedge.net/api/NCD_BMI_MINUS2C"
}

def fetch_who_data():
    result = {}
    for name, url in URLS.items():
        print("⬇ Fetching", name, "...")
        try:
            r = requests.get(url, timeout=30)
            json_data = r.json().get("value", [])
            result[name] = pd.DataFrame(json_data)
        except Exception as e:
            print("❌ Error downloading", name, ":", e)
            result[name] = pd.DataFrame()
    return result
