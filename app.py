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
                {"type": "text", "text": "You are a health dietician coach and you will help users quantify the food they are consuming from photos. Write a list of food ingredient and their quantity in this image. For example: - baked chicken breast, 2 piece \n - brocolli, a cup"},
                {
                    "type": "image_url",
                    "image_url": { "url": f"data:image/jpeg;base64,{base64_image}"}
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
            "content": "You are a health dietician coach and you will help users compute the macro nutrients from a description of food they ate. List each food name, protein, carbonhydrate, fat, and calories, in a list of json." 
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
        image_llm_response = "Based on the image provided, here is a list of the food ingredients and their estimated quantities:\n- Grilled steak, 1 piece (about 8 ounces)\n- Herb butter, 1 dollop (approximately 1 tablespoon)\n- Roasted potatoes, about 6 pieces (half a cup)\n- Steamed broccoli, 1 cup"
    else:
        base64_image = encode_image(upload_img)
        image_llm_response = get_llm_image_response(base64_image=base64_image)
        logging.info(f"get_llm_image_response returns: {image_llm_response}")

    col2.code(image_llm_response)
    return image_llm_response


def summarize_nutrition_table(description, default_image=False):
    col2.write("\n### Nutrition Summary")
    if default_image:
        nutrition_response = [{'name': 'Grilled steak', 'protein': '64g', 'carbohydrate': '0g', 'fat': '26g', 'calories': '500'}, {'name': 'Herb butter', 'protein': '0g', 'carbohydrate': '0g', 'fat': '11g', 'calories': '100'}, {'name': 'Roasted potatoes', 'protein': '5g', 'carbohydrate': '30g', 'fat': '2g', 'calories': '150'}, {'name': 'Steamed broccoli', 'protein': '4g', 'carbohydrate': '6g', 'fat': '0g', 'calories': '50'}, {'name': 'Total', 'protein': 73, 'carbohydrate': 36, 'fat': 39, 'calories': 800}]
    else:
        response = get_llm_nutrition_summary(user_description=description)
        logging.info(f"get_llm_nutrition_summary returns: {response}")
        res = json.loads(response)
        first_key = list(res.keys())[0]
        nutrition_response = res[first_key]

        total_protein = 0
        total_carbohydrate= 0
        total_fat = 0
        total_calories = 0
        for food in nutrition_response:
            total_protein += float(str(food['protein']).rstrip('g'))
            total_carbohydrate += float(str(food['carbohydrate']).rstrip('g'))
            total_fat += float(str(food['fat']).rstrip('g'))
            total_calories +=float(str(food['calories']).rstrip('g'))
        nutrition_response.append({"name": "Total", "protein": int(total_protein), "carbohydrate": int(total_carbohydrate), "fat": int(total_fat), "calories": int(total_calories)})
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