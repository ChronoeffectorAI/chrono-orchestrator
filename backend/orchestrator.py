from typing import Dict, Any, List, Optional
from agents.openai_agent import OpenAIAgent
from agents.dexscreener_agent import DexscreenerAgent
from collections import deque
import re
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentRouter:
    """
    Intelligent router that determines which agent should handle a query based on
    context, keywords, and historical interactions.
    """
    
    def __init__(self):
        # Keywords that indicate which agent to use
        self.MARKET_KEYWORDS = {
            'price', 'token', 'pair', 'liquidity', 'volume', 'market cap',
            'crypto', 'dex', 'swap', 'trading', 'chart', 'eth', 'btc'
        }
        
        self.ANALYSIS_KEYWORDS = {
            'analyze', 'explain', 'why', 'how', 'what', 'when', 'strategy',
            'opinion', 'think', 'should', 'recommend', 'forecast'
        }
        
        # Confidence thresholds for routing
        self.CONFIDENCE_THRESHOLD = 0.6
        
    def calculate_market_confidence(self, query: str, context: List[Dict]) -> float:
        """Calculate confidence score for market data queries"""
        query_words = set(query.lower().split())
        
        # Check for token addresses
        if re.search(r'0x[a-fA-F0-9]{40}', query):
            return 0.9
            
        # Check for market keywords
        keyword_matches = query_words.intersection(self.MARKET_KEYWORDS)
        if keyword_matches:
            return len(keyword_matches) / len(query_words)
            
        # Check context for market-related discussion
        if context:
            recent_market_queries = sum(
                1 for msg in context[-3:] 
                if msg.get('agent_type') == 'dexscreener'
            )
            if recent_market_queries >= 2:
                return 0.7
                
        return 0.0
        
    def calculate_analysis_confidence(self, query: str, context: List[Dict]) -> float:
        """Calculate confidence score for analysis queries"""
        query_words = set(query.lower().split())
        
        # Check for analysis keywords
        keyword_matches = query_words.intersection(self.ANALYSIS_KEYWORDS)
        if keyword_matches:
            return len(keyword_matches) / len(query_words)
            
        # Check context for analysis discussion
        if context:
            recent_analysis = sum(
                1 for msg in context[-3:] 
                if msg.get('agent_type') == 'openai'
            )
            if recent_analysis >= 2:
                return 0.7
                
        return 0.3  # Default to analysis if no strong market indicators
        
    def determine_agent(self, query: str, context: List[Dict]) -> str:
        """
        Determine which agent should handle the query based on confidence scores
        """
        market_confidence = self.calculate_market_confidence(query, context)
        analysis_confidence = self.calculate_analysis_confidence(query, context)
        
        logger.info(f"Confidence scores - Market: {market_confidence:.2f}, Analysis: {analysis_confidence:.2f}")
        
        if market_confidence > self.CONFIDENCE_THRESHOLD:
            return 'dexscreener'
        elif analysis_confidence > self.CONFIDENCE_THRESHOLD:
            return 'openai'
        else:
            # If no strong confidence, use context to decide
            if context and context[-1].get('agent_type'):
                return context[-1]['agent_type']
            return 'openai'  # Default to OpenAI for general queries

class ContextManager:
    """
    Manages conversation context and metadata across different agents
    """
    
    def __init__(self, max_context: int = 10):
        self.context = deque(maxlen=max_context)
        self.metadata = {}
        
    def add_interaction(self, query: str, response: Dict[str, Any], agent_type: str):
        """Add an interaction to the context"""
        self.context.append({
            'timestamp': datetime.utcnow().isoformat(),
            'query': query,
            'response': response,
            'agent_type': agent_type
        })
        
        # Update metadata based on response type
        if agent_type == 'dexscreener':
            if 'data' in response:
                self.metadata.update({
                    'last_token': response['data'].get('symbol'),
                    'last_price': response['data'].get('price'),
                    'last_chain': response['data'].get('chain')
                })
                
    def get_context(self) -> List[Dict]:
        """Get the current context"""
        return list(self.context)
        
    def get_metadata(self) -> Dict[str, Any]:
        """Get the current metadata"""
        return self.metadata
        
    def clear_context(self):
        """Clear the context and metadata"""
        self.context.clear()
        self.metadata.clear()

class Orchestrator:
    """
    Main orchestrator that manages agents and routes queries
    """
    
    def __init__(self):
        self.openai_agent = OpenAIAgent()
        self.dexscreener_agent = DexscreenerAgent()
        self.router = AgentRouter()
        self.context_manager = ContextManager()
        
    def handle_input(self, user_input: str) -> Dict[str, Any]:
        """
        Handle user input by routing to appropriate agent and managing context
        """
        try:
            # Get current context
            context = self.context_manager.get_context()
            
            # Determine which agent should handle the query
            agent_type = self.router.determine_agent(user_input, context)
            logger.info(f"Selected agent: {agent_type}")
            
            # Get response from appropriate agent
            if agent_type == 'dexscreener':
                # Check if input contains token address
                if re.search(r'0x[a-fA-F0-9]{40}', user_input):
                    response = self.dexscreener_agent.get_price_data(
                        re.search(r'0x[a-fA-F0-9]{40}', user_input).group()
                    )
                else:
                    # Try token search
                    response = self.dexscreener_agent.search_tokens(user_input)
            else:
                # Enhance OpenAI prompt with context if available
                metadata = self.context_manager.get_metadata()
                if metadata:
                    enhanced_input = (
                        f"Context: Last token discussed was {metadata.get('last_token', 'N/A')} "
                        f"at price {metadata.get('last_price', 'N/A')} "
                        f"on {metadata.get('last_chain', 'N/A')}.\n\n"
                        f"Query: {user_input}"
                    )
                else:
                    enhanced_input = user_input
                response = self.openai_agent.respond(enhanced_input)
            
            # Update context with new interaction
            self.context_manager.add_interaction(user_input, response, agent_type)
            
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