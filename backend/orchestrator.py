from typing import Dict, Any, List, Optional
import logging
from collections import deque
from datetime import datetime
from agents.base_agent import BaseAgent
from agents.openai_agent import OpenAIAgent
from agents.dexscreener_agent import DexscreenerAgent
from agents.swap_agent import SwapAgent
from router import AgentRouter  # Import the new router

logger = logging.getLogger(__name__)

class Orchestrator:
    """
    Orchestrates communication between different agents and manages context.
    """
    
    def __init__(self):
        """Initialize the orchestrator with available agents"""
        self.agents = {}  # Dictionary to store agent instances
        self.context_manager = ContextManager()
        
        # Initialize agents first
        self._register_agents([
            OpenAIAgent(),
            DexscreenerAgent(),
            SwapAgent()
        ])
        
        # Initialize router with registered agents
        self.router = AgentRouter(self.agents)
        
        logger.info(f"Orchestrator initialized with agents: {list(self.agents.keys())}")

    def _register_agents(self, agent_list: List[BaseAgent]) -> None:
        """Register agents with the orchestrator"""
        for agent in agent_list:
            self.agents[agent.agent_id] = agent
            logger.info(f"Registered agent: {agent.agent_id}")

    def handle_input(self, user_input: str) -> Dict[str, Any]:
        """
        Handle user input by routing to appropriate agent and managing context
        """
        try:
            # Get current context
            context = self.context_manager.get_context()
            
            # Determine which agent should handle the query
            agent_id = self.router.determine_agent(user_input, context)
            logger.info(f"Selected agent: {agent_id}")
            
            # Verify agent exists
            if agent_id not in self.agents:
                logger.error(f"Agent {agent_id} not found")
                return {
                    "response": f"Error: Agent {agent_id} not available",
                    "status": "error",
                    "type": "orchestrator"
                }
            
            # Get the appropriate agent
            agent = self.agents[agent_id]
            
            # Get shared context from context manager
            shared_context = self.context_manager.get_metadata()
            
            # Process query with the selected agent
            response = agent.process_query(user_input, shared_context)
            
            # Update context with new interaction
            self.context_manager.add_interaction(
                query=user_input,
                response=response,
                agent_id=agent_id
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error in orchestrator: {str(e)}")
            return {
                "response": f"Error processing request: {str(e)}",
                "status": "error",
                "type": "orchestrator"
            }

    def clear_context(self):
        """Clear the conversation context"""
        self.context_manager.clear_context()
        for agent in self.agents.values():
            agent.clear_context()

class ContextManager:
    """Manages conversation context and metadata across different agents"""
    
    def __init__(self, max_context: int = 10):
        self.context = deque(maxlen=max_context)
        self.metadata = {}
        
    def add_interaction(self, query: str, response: Dict[str, Any], agent_id: str):
        """Add an interaction to the context"""
        interaction = {
            'timestamp': datetime.utcnow().isoformat(),
            'query': query,
            'response': response,
            'agent_id': agent_id
        }
        
        self.context.append(interaction)
        self._update_metadata(interaction)
        
    def _update_metadata(self, interaction: Dict[str, Any]):
        """Update metadata based on the interaction"""
        # Base metadata
        self.metadata.update({
            'last_query': interaction['query'],
            'last_agent': interaction['agent_id'],
            'last_timestamp': interaction['timestamp']
        })
        
        # Agent-specific metadata from response
        if 'data' in interaction['response']:
            data = interaction['response']['data']
            if isinstance(data, dict):
                for key, value in data.items():
                    self.metadata[f'last_{key}'] = value
        
    def get_context(self, n: int = None) -> List[Dict]:
        """Get the last n interactions from context"""
        context_list = list(self.context)
        return context_list[-n:] if n else context_list
        
    def get_metadata(self) -> Dict[str, Any]:
        """Get the current metadata"""
        return self.metadata.copy()
        
    def clear_context(self):
        """Clear the context and metadata"""
        self.context.clear()
        self.metadata.clear() 