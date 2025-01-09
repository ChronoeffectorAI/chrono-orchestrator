from typing import Dict, List, Optional
import logging
from openai import OpenAI
import os
from dotenv import load_dotenv
from agents.base_agent import BaseAgent

load_dotenv()
logger = logging.getLogger(__name__)

class AgentRouter:
    """
    Routes user queries to appropriate agents using OpenAI for decision making.
    """
    
    def __init__(self, registered_agents: Dict[str, BaseAgent]):
        """
        Initialize the router with OpenAI client and registered agents
        
        Args:
            registered_agents (Dict[str, BaseAgent]): Dictionary of agent_id -> agent instance
        """
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.registered_agents = registered_agents
        self.VALID_AGENTS = set(registered_agents.keys())
        logger.info(f"AgentRouter initialized with agents: {self.VALID_AGENTS}")

    def _generate_system_prompt(self) -> str:
        """
        Generate system prompt dynamically based on registered agents
        """
        prompt_parts = [
            "You are an AI tasked with routing user queries to the appropriate agent.",
            "Based on the user's input, determine which agent should handle the request.",
            "\nRules for agent selection:"
        ]

        # Add each agent's description
        for agent_id, agent in self.registered_agents.items():
            prompt_parts.append(f"\n{agent_id}:\n{agent.description()}")

        prompt_parts.append(
            f"\nRespond ONLY with one of these exact strings: {', '.join(f'"{aid}"' for aid in self.VALID_AGENTS)}"
        )

        return "\n".join(prompt_parts)

    def determine_agent(self, query: str, context: Optional[List[Dict]] = None) -> str:
        """
        Use OpenAI to determine which agent should handle the query.
        """
        try:
            # Generate dynamic system prompt
            system_prompt = self._generate_system_prompt()
            
            # Prepare the user prompt with context
            user_prompt = f"Route this query: {query}"
            if context and len(context) > 0:
                last_interaction = context[-1]
                if isinstance(last_interaction, dict):
                    agent_type = (
                        last_interaction.get('response', {}).get('type') or 
                        last_interaction.get('agent_id') or 
                        'none'
                    )
                    user_prompt += f"\nPrevious interaction type: {agent_type}"

            # Get routing decision from OpenAI
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=10,
                temperature=0
            )

            # Extract and validate the agent type
            agent_type = response.choices[0].message.content.strip().lower()
            logger.info(f"Router selected agent '{agent_type}' for query: '{query}'")

            # Validate response
            if agent_type not in self.VALID_AGENTS:
                logger.warning(f"Invalid agent type '{agent_type}' returned, defaulting to 'openai'")
                return "openai"

            return agent_type

        except Exception as e:
            logger.error(f"Error in determine_agent: {str(e)}")
            logger.exception("Full traceback:")
            return "openai"  # Default to OpenAI on error

    def _extract_context_type(self, context_item: Dict) -> str:
        """
        Helper method to extract agent type from context item.
        
        Args:
            context_item (Dict): A single context interaction
            
        Returns:
            str: The agent type or 'none' if not found
        """
        try:
            if 'response' in context_item and isinstance(context_item['response'], dict):
                return context_item['response'].get('type', 'none')
            elif 'agent_id' in context_item:
                return context_item['agent_id']
            return 'none'
        except Exception:
            return 'none' 