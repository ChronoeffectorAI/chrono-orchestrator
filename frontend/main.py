import chainlit as cl
import requests
from typing import Dict, Any
import json

BACKEND_URL = "http://127.0.0.1:5000/api/query"

@cl.on_chat_start
async def start():
    await cl.Message(content="Welcome to the AI Chat Interface! How can I help you today?").send()

@cl.on_message
async def main(message: str):
    try:
        response = requests.post(
            BACKEND_URL,
            json={"input": message.content},
            headers={"Content-Type": "application/json"}
        )
        print(response)
        if response.status_code == 200:
            try:
                data = response.json()
                content = data.get('response', '')
                if not content:
                    content = "No response content received from the server."
                await cl.Message(content=content).send()
            except json.JSONDecodeError:
                await cl.Message(content="Error: Invalid response format from server").send()
        else:
            error_message = f"Error: Server returned status code {response.status_code}"
            try:
                error_data = response.json()
                if isinstance(error_data, dict) and 'error' in error_data:
                    error_message = error_data['error']
            except:
                pass
            await cl.Message(content=error_message).send()
            
    except requests.exceptions.ConnectionError:
        await cl.Message(
            content="Error: Could not connect to backend server. Please ensure it's running on http://localhost:5000"
        ).send()
    except Exception as e:
        await cl.Message(
            content=f"Error: An unexpected error occurred. Details: {str(e)}"
        ).send()

if __name__ == "__main__":
    cl.run() 