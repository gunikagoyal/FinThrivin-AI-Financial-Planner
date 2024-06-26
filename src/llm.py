from langchain_community.llms import HuggingFaceHub
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv, find_dotenv
import warnings
import os
warnings.filterwarnings("ignore")


class LlmRepo:
    """This class is used to load all the necessary LLMs across the application"""

    def __init__(self):
        pass

    def llm_chatbot_inference(self,template, 
                              question, 
                              question_mapping,
                              user_input, 
                              context,
                              hf_repo_id = "mistralai/Mistral-7B-Instruct-v0.2",
                              temperature = 0.1,
                              max_length = 128):
        """"""
        load_dotenv(find_dotenv())
        prompt_template = PromptTemplate(input_variables=["question","question_mapping","context"], 
                                         template=template)
        llm = HuggingFaceHub(repo_id=hf_repo_id, 
                     model_kwargs={"temperature": temperature, "max_length": max_length}
                     )
        llm_chain = LLMChain(prompt=prompt_template, llm=llm)
        response = llm_chain.run(context=user_input, 
                                 question=question, 
                                 user_text=user_input, 
                                 question_mapping=question_mapping
                                 )
        response_start_index = response.find("Response:")
        response_output = response[response_start_index + len("Response;"):].strip()
        return response_output

if __name__=='__main__':
    llmrepo = LlmRepo()
    #Define initial context
    context = ""

    # Define initial question
    question = ""

    # Define dictionary of questions based on user responses
    question_mapping = {
        "hello": "I would like to as you some security questions to identify who you are and better assist you. Can you please give me your first Name?",
        "first name": ["what is your last name?"],
        "last name":['what is your date of birth?,please provide date of birth in mm/dd/yyyy format'],
        "date of birth":['Looks like you are existing user'],
        "new user": ["Welcome. To give you better advice and insights, it is important to get some financial information from you. This will take about 10 minutes. If you don't have 10 minutes, you can also do this in parts. Do some right now and come back and finish later. Are you ready to start?"],
        "existing user": ['can you provide your more details about your financial details'],
        "ready to start": ["What's your profession?"],
        "profession": ["Enter your profession-specific question here."],
        "collect other questions": ["Enter other relevant questions here."],
        # Add more response-question pairs as needed
    }
    # Start interaction loop

    template = """INSTRUCTIONS: 

            Context: {context}

            As a financial analyst, your task is to ask the appropriate question based on the current context.

            Ask the following question by understanding the current context:
            {question}

            The available questions for each context are defined as follows:
            {question_mapping}

            Provide a response based on the user_text and the context.

            Do not add any extra information other than the question picked up from question_mapping

            Response:
            """
    while True:
        # Get user input
        user_input = input("User: ")

        # Run LLMChain with user input
        # response = llm_chain.run(
        #     context=user_input,
        #     question=question,
        #     user_text=user_input,
        #     question_mapping=question_mapping,
        # )
        response = llmrepo.llm_chatbot_inference(template=template,
                                                 question=question,
                                                 question_mapping=question_mapping,
                                                 user_input=user_input,
                                                 context=context)

        # Print chatbot response
        print("AI Assistant:", response)
        # Update context and question based on chatbot response
        for key, value in question_mapping.items():
            if key.lower() in response.lower():
                context = key
                question = value[0] if value else ""
                break

        # Exit loop if user says goodbye
        if "goodbye" in response.lower():
            break

        

    



