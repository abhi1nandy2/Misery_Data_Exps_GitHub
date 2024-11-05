from openai import OpenAI
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import os
import time

from langchain.chat_models import AzureChatOpenAI
from langchain.schema import HumanMessage#, SystemMessage
# from langchain.callbacks import get_openai_callback
# from langchain.llms import OpenAI        

os.environ["OPENAI_API_KEY"] = "<API_KEY>"

gemini_safety_settings = {
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE, 
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE, 
        # HarmCategory.HARM_CATEGORY_CIVIC_INTEGRITY: HarmBlockThreshold.BLOCK_NONE
    }

def get_completion(input_prompt, model_name, seed, max_out_tokens = 500):
    if "adobe" in model_name:
        pass        
    elif ("gpt-" in model_name) or ("o1" in model_name):
        client = OpenAI()
        completion = client.chat.completions.create(
            model=model_name,
            max_completion_tokens=max_out_tokens,
            seed=seed,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": input_prompt
                }
            ]
        )

        response = completion.choices[0].message.content
    elif "gemini" in model_name:
        genai.configure(api_key="<GEMINI_API_KEY>")
        model = genai.GenerativeModel(model_name)
        config = genai.GenerationConfig(max_output_tokens=max_out_tokens)
        response = model.generate_content(input_prompt, generation_config=config, safety_settings = gemini_safety_settings)
        response = response.text
        time.sleep(10)
    else:
        print("MODEL NAME SAHI SE LIKHO!")
        print(1/0)

    return response.replace("You:", "").split("Host:")[0].strip()

def extract_answer(response):
    try:
        answer = response.split("{{{")[1].split("}}}")[0].strip()
    except:
        try:
            answer = response.split("{{")[1].split("}}")[0].strip()
        except:
            try:
                answer = response.split("{")[1].split("}")[0].strip()
            except Exception as E:
                print(E)
                print(response)
                print(1/0)
    
    if "-" in answer:
        answer_lower = answer.split("-")[0].strip()
        answer_upper = answer.split("-")[1].strip()
        if answer_lower=='':
            answer_lower=0
        if answer_upper=='':
            answer_upper=100
        return int(answer_lower), int(answer_upper)
    return answer

def get_correct_or_wrong(condition):
    if condition:
        return "You are CORRECT!"
    else:
        return "Sorry, you are WRONG!"