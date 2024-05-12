import requests
from dotenv import load_dotenv
import os 
import json
load_dotenv()

# food = input("type in your food name\n")
# quantity = input("type in quantity\n")

food = "steak"
quantity = "1"
print(f"User input: {food}, {quantity}")

# send requests to USDA 
USDA_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"
# Query parameters
params = {
    'api_key': os.environ['USDA_API_KEY'],
    'query': food,
}

# Sending the GET request with query parameters
response = requests.get(USDA_URL, params=params)
data=json.loads(response.content)['foods']
# see the top matches and find the most probable (some are just wrong)
for d in data[:3]:
    print(f"\n {d['description']} --------------")
    if "servingSize" in d and "servingSizeUnit" in d:
        print(f"Serving size in database: {d['servingSize']} {d['servingSizeUnit']}")
    elif "foodMeasures" in d and len(d['foodMeasures']) > 0:
        print(f"Serving size in database: {d['foodMeasures'][0]['disseminationText']} or {d['foodMeasures'][0]['gramWeight']} g")
    for n in d['foodNutrients']:
        if n['nutrientName'] in ["Energy", "Protein", "Carbohydrate, by difference", "Total lipid (fat)"]: #"Total Sugars", "Fiber, total dietary", 
            print(f"{n['nutrientName']}: {n['value']} {n['unitName']}")
# curl https://api.nal.usda.gov/fdc/v1/foods/search\?api_key\=eZG3K1svl8z1OoewSZ2xwFy3PUS4lmtJFQwLn0HM\&query\=Herb%20Butter
