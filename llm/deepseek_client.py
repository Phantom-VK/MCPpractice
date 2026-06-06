import os

from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv(verbose=True)

deepseek_model = OpenAIChatCompletionsModel(
                    model="deepseek-v4-pro",
                    openai_client= AsyncOpenAI(
                        api_key=os.environ.get("DEEPSEEK_API_KEY"),
                        base_url="https://api.deepseek.com/v1"
                    )
                )