import streamlit as st
from PIL import Image
from io import BytesIO
import base64
from openai import OpenAI
from dotenv import load_dotenv
import json 
import pandas as pd 
import logging 
from pillow_heif import register_heif_opener

load_dotenv()
client = OpenAI()

register_heif_opener()
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(message)s')


st.set_page_config(layout="wide", page_title="Personalized Dietician Bot")

st.write("## Identify Food and Nutrition Intake with AI")
st.write(
    ":apple: No more manual logging of your calories. Get all the nutrition info by sending us a snapshot of your plate. Forming healthy eating habits is easy and rewarding. :apple:"
)
st.sidebar.write("## Upload :gear:")

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB



def get_llm_image_response(base64_image):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
            "role": "user",       
            "content": [
                {"type": "text", "text": "You are a health dietician coach and you will help users quantify the food they are consuming from photos. Write a list of food ingredient and their quantity in this image. For example: - baked chicken breast, 2 piece \n - brocolli, a cup. Only list items of food and their amount."},
                {
                    "type": "image_url",
                    "image_url": { "url": f"data:image/jpeg;base64,{base64_image}", "detail": "low"}
                },
            ],
            }
        ],
        max_tokens=1000,
    )
    return response.choices[0].message.content

def get_llm_nutrition_summary(user_description):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {
            "role": "system",
            "content": "You are a health dietician coach and you will help users compute the macro nutrients from a description of food they ate. List each food name, protein, carbonhydrate, and fat, in json format. For example: {'food': [{'name': 'apple', 'protein': 0.5, 'carbohydrate': 25, 'fat': 0.5}]}" 
            },
            {
            "role": "user",
            "content": user_description,
            }
        ],
        response_format={ "type": "json_object" },
    )
    return response.choices[0].message.content


def encode_image(image_file):
    if isinstance(image_file, BytesIO):
        if image_file.type == 'image/heic':
            img = Image.open(image_file)
            new_img = BytesIO()
            img_byte_arr = Image.frombytes(mode=img.mode, size=img.size, data=img.tobytes())
            img_byte_arr.save(new_img, format='PNG')
            encoded_string = base64.b64encode(new_img.getvalue()).decode('utf-8')
        else:
            encoded_string =  base64.b64encode(image_file.getvalue()).decode('utf-8')
    else:
        with open(image_file, "rb") as f:
            encoded_string = base64.b64encode(f.read()).decode('utf-8')
    return encoded_string


def analyze_image(upload_img, default_image=False):
    image = Image.open(upload_img)
    col1.write("### Original Image :camera:")
    col1.image(image)
    # optionally upload image to s3, not for now.
        
    col2.write("### Food Analysis :cook:")
    col2.write("\n")
    if default_image:
        image_llm_response = "- Grilled steak, 1 piece (approximately 6-8 ounces)\n- Broccoli, 1 cup\n- Roasted baby potatoes, 1/2 cup\n- Herb butter, 1 tablespoon"
    else:
        base64_image = encode_image(upload_img)
        image_llm_response = get_llm_image_response(base64_image=base64_image)
        logging.info(f"get_llm_image_response returns: {image_llm_response}")

    col2.code(image_llm_response)
    return image_llm_response


def summarize_nutrition_table(description, default_image=False):
    col2.write("\n### Nutrition Summary")
    if default_image:
        nutrition_response = [{"name": "Grilled steak", "protein": "60.0", "carbohydrate": "0.0", "fat": "20.0", "calories": "420.0"}, {"name": "Broccoli", "protein": "2.0", "carbohydrate": "6.0", "fat": "0.0", "calories": "32.0"}, {"name": "Roasted baby potatoes", "protein": "2.0", "carbohydrate": "15.0", "fat": "0.0", "calories": "68.0"}, {"name": "Herb butter", "protein": "0.0", "carbohydrate": "0.0", "fat": "11.0", "calories": "99.0"}, {"name": "Total", "protein": "64.0", "carbohydrate": "21.0", "fat": "31.0", "calories": "619.0"}]
    else:
        response = get_llm_nutrition_summary(user_description=description)
        logging.info(f"get_llm_nutrition_summary returns: {response}")
        res = json.loads(response)
        first_key = list(res.keys())[0]
        nutrition_response = res[first_key]

        protein = []
        carbohydrate= []
        fat = []
        calories = []
        for food in nutrition_response:
            p = float(str(food['protein']).rstrip('g'))
            c = float(str(food['carbohydrate']).rstrip('g'))
            f = float(str(food['fat']).rstrip('g'))
            protein.append(p)
            carbohydrate.append(c)
            fat.append(f)
            cal = 4*c + 4*p + 9*f
            calories.append(cal)
            food['calories'] = cal
        nutrition_response.append({"name": "Total", "protein": float(sum(protein)), "carbohydrate": float(sum(carbohydrate)), "fat": float(sum(fat)), "calories": float(sum(calories))})
        logging.info(f"nutrition table: {nutrition_response}")

    df = pd.DataFrame(nutrition_response).astype(str)
    col2.dataframe(df,hide_index=True)

col1, col2 = st.columns(2)
my_upload = st.sidebar.file_uploader("Upload an image", type=["png", "jpg", "jpeg", "heic"])

if my_upload is not None:
    if my_upload.size > MAX_FILE_SIZE:
        st.error("The uploaded file is too large. Please upload an image smaller than 10MB.")
    else:
        description = analyze_image(upload_img=my_upload)
        summarize_nutrition_table(description)
        # base64_image = encode_image(my_upload)
else:
    description = analyze_image("./default_food.jpg", default_image=True)   
    summarize_nutrition_table(description, default_image=True)