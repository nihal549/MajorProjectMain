import os
import json
import numpy as np
from tensorflow import keras
from fastapi import FastAPI, UploadFile, File
import argparse
from fastapi.middleware.cors import CORSMiddleware
import io

app = FastAPI()

## Chatbot

import openai
import os
import os
from getpass import getpass
from fastapi import FastAPI
from langchain.agents import load_tools
from langchain.agents import initialize_agent
from langchain.agents import AgentType
from langchain.llms import OpenAI
from langchain.utilities.wolfram_alpha import WolframAlphaAPIWrapper
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI

app = FastAPI()

@app.get("/crop-info/{prediction_result}")
def get_crop_info(prediction_result: str):
    # Set the OpenAI and Wolfram Alpha API keys
    os.environ['OPENAI_API_KEY'] = ""
    os.environ["WOLFRAM_ALPHA_APPID"] = ""

    # Create the prompt strings
    about = f"Please tell me about {prediction_result} crop, it's diseases and how to prevent them."

    # Use Langchain for the query engine
    # llm = ChatOpenAI(temperature=0)


    # # Define tools for the agent
    # tools = load_tools(['wikipedia', 'wolfram-alpha'], llm=llm)

    # # Set up conversation memory
    # memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    # # Initialize the agent
    # agent = initialize_agent(tools, llm, agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    #                          verbose=True, memory=memory, max_iterations=6)

    # # Get LLM response for crop information

    # info = agent.run(input=about)
    # # Print the observation page apple and summary
    # return {
    #     "crop_info": info
    # }

    # format the prompt
    llm1 = OpenAI(model_name="text-ada-001", n=2, best_of=2)

    result = llm1(about)

    return {
        "crop_info": result
    }

def load_categories(file_path):
    with open(file_path) as file:
        data = json.load(file)

    # Swap keys and values
    data = dict([(value, key) for key, value in data.items()])

    return data


def load_model(model_path):
    model = keras.models.load_model(model_path)

    return model


def get_prediction_info(cats, class_id):
    name, disease = cats[class_id].split("___")
    name, disease = name.replace("_", " "), disease.replace("_", " ")

    return name, disease


def get_prediction(model, categories, img):
    # Preprocess image
    img = img.reshape((1, 224, 224, 3))
    img = img.astype("float32") / 255.0

    # Get prediction
    prediction = model.predict(img)
    class_id = prediction.argmax()

    return get_prediction_info(categories, class_id)


def handle_invalid_path(filepath):
    if not os.path.exists(filepath):
        raise argparse.ArgumentTypeError(f"{filepath} does not exist")

    return os.path.expanduser(filepath)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/predict")
async def predict_disease(image: UploadFile = File(...)):
    # Save the uploaded file
    model_path = r"plant_disease_detection.h5"
    categories_path = r"categories.json"

    # Load categories
    categories = load_categories(categories_path)

    # Load model
    model = load_model(model_path)

    # Read the image file
    contents = await image.read()

    # Convert the image to numpy array
    img = keras.preprocessing.image.img_to_array(
        keras.preprocessing.image.load_img(
            io.BytesIO(contents), target_size=(224, 224)
        )
    )

    # Get prediction
    name, disease = get_prediction(model, categories, img)

    # Return prediction
    return {"disease": disease, "name": name}