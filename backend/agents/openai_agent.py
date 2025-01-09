from .base_agent import BaseAgent
from openai import OpenAI
from dotenv import load_dotenv
import os
from typing import Dict, Any, List, Optional

load_dotenv()

class OpenAIAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    def update_shared_context(self, interaction: Dict[str, Any]) -> None:
        """
        Update shared context with OpenAI-specific information
        """
        super().update_shared_context(interaction)
        
        # Add any OpenAI-specific context
        self.shared_context.update({
            'last_ai_response': interaction['response'].get('response'),
            'last_topic': self.extract_topic(interaction['query'])  # You could implement this
        })

    def process_query(self, query: str, shared_context: Optional[Dict] = None) -> Dict[str, Any]:
        try:
            # Enhance prompt with shared context if available
            enhanced_prompt = query
            if shared_context:
                context_info = []
                if 'last_token_symbol' in shared_context:
                    context_info.append(f"Last discussed token: {shared_context['last_token_symbol']}")
                if 'last_token_price' in shared_context:
                    context_info.append(f"Price: {shared_context['last_token_price']}")
                
                if context_info:
                    enhanced_prompt = f"Context: {'. '.join(context_info)}\n\nQuery: {query}"

            system_prompt = "You are a helpful crypto expert that can answer questions about crypto. You are also able to provide information about the latest news in the crypto space."
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": enhanced_prompt}
                ],
                max_tokens=150
            )
            
            message_content = response.choices[0].message.content
            return self.format_response(str(message_content))
            
        except Exception as e:
            return self.handle_error(e, "while processing OpenAI query") 