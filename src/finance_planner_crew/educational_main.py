#!/usr/bin/env python
# from finagent.crew import finagent
from main import run_agent
from dotenv import load_dotenv
import os
from pathlib import Path
import json
from langchain.chains import ConversationChain
import requests
from time import sleep
from transformers import pipeline
from langchain.llms import HuggingFaceEndpoint

# Load environment variables from .env file
load_dotenv()
# HUGGING_FACE_API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
# HUGGINGFACEHUB_API_TOKEN  = os.getenv("HUGGING_FACE_API_KEY")
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
output_path = os.path.join(ROOT_DIR,'data','output','educational_articles.json')

with open(output_path, 'r') as file:
            data = json.load(file)
            
# Define the labels for classification
labels = ["Finance", "Non-Finance"]      

class Chatbot:
    def __init__(self):
        self.memory = {}
        # self.agent = finagent()
        # self.llm = HuggingFaceEndpoint(
        #     repo_id="mistralai/Mistral-7B-Instruct-v0.2",
        #     max_new_tokens=200,
        #     temperature=0.3,
        #     repetition_penalty=1.1,
        #     huggingfacehub_api_token=HUGGINGFACEHUB_API_TOKEN
        # )


    def run_finagent(self, user_input, context=None):
        # Use generate_response for predefined contexts

        result = run_agent('education',user_input=user_input)
        
        # Store user input and response in memory
        with open(output_path, 'w') as file:
            json.dump(self.memory, file, indent=4)
        return result
    
