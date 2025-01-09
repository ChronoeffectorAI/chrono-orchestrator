from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

class OpenAIAgent:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    def respond(self, user_input: str) -> dict:
        try:
            system_prompt = "You are a helpful crypto expert that can answer questions about crypto. You are also able to provide information about the latest news in the crypto space."
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=150
            )
            
            # Extract the message content directly
            message_content = response.choices[0].message.content
            
            return {
                "response": str(message_content),  # Ensure it's a string
                "status": "success",
                "type": "openai"
            }
        except Exception as e:
            return {
                "response": str(e),
                "status": "error",
                "type": "openai"
            } 