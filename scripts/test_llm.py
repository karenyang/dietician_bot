from openai import OpenAI
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List
import pandas as pd
import re 
load_dotenv()
import collections, functools, operator

client = OpenAI()

# #GPT4V
# response = client.chat.completions.create(
#   model="gpt-4-turbo",
#   messages=[
#     {
#       "role": "user",       
#       "content": [
#         {"type": "text", "text": "You are a health dietician coach and you will help users quantify the food they are consuming from photos. Write a list of food ingredient and their quantity in this image. For example: - baked chicken breast, 2 piece \n - brocolli, a cup"},
#         {
#           "type": "image_url",
#           "image_url": {
#             "url": "https://public-test-image-bucket.s3.us-east-2.amazonaws.com/IMG_4962.jpg",
#           },
#         },
#       ],
#     }
#   ],
#   max_tokens=300,
# )

# response = client.chat.completions.create(
#   model="gpt-3.5-turbo-1106",
#   messages=[
#     {
#      "role": "system",
#       "content": "You are a health dietician coach and you will help users compute the macro nutrients from a description of food they ate. List each food name, quantity, protein, carbonhydrate, fat, and calories, in a list of json." 
#     },
#     {
#       "role": "user",
#       "content": "- Grilled steak with herb butter, 1 piece (approximately 6-8 ounces)\n - Broccoli, about 1 cup (steamed) \n -  Roasted potatoes, about 6 to 8 halves (depending on the size of the potatoes)"
#     }
#   ],
#   response_format={ "type": "json_object" },
# )


# print(response.choices[0].message.content)

data = {
  "foods": [
    {
      "name": "Grilled steak",
      "protein": "64g",
      "carbohydrate": "0g",
      "fat": "26g",
      "calories": "500"
    },
    {
      "name": "Herb butter",
      "protein": "0g",
      "carbohydrate": "0g",
      "fat": "11g",
      "calories": "100"
    },
    {
      "name": "Roasted potatoes",
      "protein": "5g",
      "carbohydrate": "30g",
      "fat": "2g",
      "calories": "150"
    },
    {
      "name": "Steamed broccoli",
      "protein": "4g",
      "carbohydrate": "6g",
      "fat": "0g",
      "calories": "50"
    }
  ]
}


total_protein = 0
total_carbohydrate= 0
total_fat = 0
total_calories = 0

for food in data['foods']:
    total_protein += float(food['protein'].rstrip('g'))
    total_carbohydrate += float(food['carbohydrate'].rstrip('g'))
    total_fat += float(food['fat'].rstrip('g'))
    total_calories +=float(food['calories'].rstrip('g'))

data['foods'].append({"name": "Total", "protein": int(total_protein), "carbohydrate": int(total_carbohydrate), "fat": int(total_fat), "calories": int(total_calories)})
print(data['foods'])


# RE_D = re.compile(r'\d')
# def contain_numbers(string):
#     return RE_D.search(string)
# df = pd.DataFrame(data['foods'])
# df = df.map(lambda x: x.rstrip('g') if contain_numbers(x) else x)
# # print(df)
# df.loc['Total'] = df[["protein", "carbohydrate", "fat", "calories"]].astype(int).sum()
# df.loc['Total', "name"] = ""
# print(df)