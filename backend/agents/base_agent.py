from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from collections import deque

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Abstract base class for all agents with context management.
    """
    
    def __init__(self, max_context: int = 10):
        """
        Initialize the agent with context management.
        
        Args:
            max_context (int): Maximum number of interactions to keep in context
        """
        self.agent_id = self.__class__.__name__.lower().replace('agent', '')
        self.name = self.__class__.__name__
        self.context = deque(maxlen=max_context)
        self.shared_context = {}  # Shared context accessible by other agents
        logger.info(f"Initializing {self.name} with ID: {self.agent_id}")

    @abstractmethod
    def process_query(self, query: str, shared_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process a user query and return a response.
        
        Args:
            query (str): The user's input query
            shared_context (Dict, optional): Context shared from other agents
            
        Returns:
            Dict[str, Any]: Response dictionary
        """
        pass

    def add_to_context(self, query: str, response: Dict[str, Any]) -> None:
        """
        Add an interaction to the agent's context.
        
        Args:
            query (str): The user's query
            response (Dict[str, Any]): The agent's response
        """
        interaction = {
            'timestamp': datetime.utcnow().isoformat(),
            'query': query,
            'response': response,
            'agent': self.name
        }
        self.context.append(interaction)
        self.update_shared_context(interaction)

    def update_shared_context(self, interaction: Dict[str, Any]) -> None:
        """
        Update the shared context based on the interaction.
        Override this in specific agents to extract relevant information.
        
        Args:
            interaction (Dict[str, Any]): The interaction to process
        """
        # Base implementation just stores last interaction
        self.shared_context.update({
            'last_query': interaction['query'],
            'last_response': interaction['response'],
            'last_agent': self.name,
            'last_timestamp': interaction['timestamp']
        })

    def get_context(self, n: int = None) -> List[Dict[str, Any]]:
        """
        Get the last n interactions from context.
        
        Args:
            n (int, optional): Number of interactions to return. If None, returns all.
            
        Returns:
            List[Dict[str, Any]]: List of interactions
        """
        context_list = list(self.context)
        return context_list[-n:] if n else context_list

    def get_shared_context(self) -> Dict[str, Any]:
        """
        Get the current shared context.
        
        Returns:
            Dict[str, Any]: The shared context
        """
        return self.shared_context

    def clear_context(self) -> None:
        """Clear both local and shared context"""
        self.context.clear()
        self.shared_context.clear()

    def format_response(self, message: str, data: Any = None, status: str = "success") -> Dict[str, Any]:
        """Format response with consistent structure"""
        response = {
            "response": message,
            "status": status,
            "type": self.name.lower().replace('agent', '')
        }
        
        if data is not None:
            response["data"] = data
            
        return response

    def handle_error(self, error: Exception, context: str = "") -> Dict[str, Any]:
        """Handle errors consistently"""
        error_message = f"Error in {self.name}"
        if context:
            error_message += f" ({context})"
        error_message += f": {str(error)}"
        
        logger.error(error_message)
        return self.format_response(error_message, status="error") 

    @abstractmethod
    def description(self) -> str:
        """
        Returns a description of the agent's capabilities.
        This description will be used by the router to determine if the agent
        should handle a specific query.
        
        Returns:
            str: Description of what queries this agent can handle
        """
        pass 