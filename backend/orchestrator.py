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
    Routes queries to appropriate agents and maintains conversation context
    """
    
    def __init__(self):
        self.dexscreener_agent = DexscreenerAgent()
        self.openai_agent = OpenAIAgent()
        self.CONFIDENCE_THRESHOLD = 0.4
        
        # Cryptocurrency-related keywords with weights
        self.crypto_keywords = {
            # High confidence tokens (1.0)
            'bitcoin': 1.0, 'btc': 1.0, 'eth': 1.0, 'ethereum': 1.0,
            'solana': 1.0, 'sol': 1.0, 'usdt': 1.0, 'usdc': 1.0,
            
            # Price-related keywords (0.8)
            'price': 0.8, 'worth': 0.8, 'cost': 0.8, 'value': 0.8,
            
            # Market-related keywords (0.6)
            'market': 0.6, 'trading': 0.6, 'volume': 0.6, 'liquidity': 0.6,
            'token': 0.6, 'coin': 0.6, 'crypto': 0.6, 'cryptocurrency': 0.6,
            
            # General crypto terms (0.4)
            'blockchain': 0.4, 'wallet': 0.4, 'defi': 0.4, 'exchange': 0.4,
            'pair': 0.4, 'pool': 0.4, 'yield': 0.4, 'staking': 0.4
        }

    def calculate_market_confidence(self, query: str, context: List[Dict]) -> float:
        """
        Calculate confidence score for market-related queries with weighted keywords
        """
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        # Initialize confidence
        confidence = 0.0
        
        # Check for direct token mentions with price-related words
        if any(token in query_lower for token in ['bitcoin', 'btc', 'eth', 'ethereum', 'sol', 'solana']):
            if any(price_word in query_lower for price_word in ['price', 'worth', 'cost', 'value']):
                return 1.0  # Maximum confidence for direct price queries
        
        # Calculate weighted confidence based on keyword matches
        matched_weights = [
            self.crypto_keywords[word] 
            for word in query_words 
            if word in self.crypto_keywords
        ]
        
        if matched_weights:
            # Use the highest weight found as base confidence
            confidence = max(matched_weights)
            
            # Boost confidence if multiple keywords are found
            if len(matched_weights) > 1:
                confidence += 0.2
        
        # Boost confidence if previous context was market-related
        if context and context[-1].get('type') == 'dexscreener':
            confidence += 0.2
        
        return min(confidence, 1.0)  # Cap at 1.0

    def determine_agent(self, query: str, context: List[Dict]) -> str:
        """
        Use OpenAI to determine which agent should handle the query
        """
        try:
            system_prompt = """
            You are an AI tasked with routing user queries to the appropriate agent.
            Based on the user's input, determine which agent should handle the request.
            
            Rules for agent selection:
            1. "dexscreener" - For queries about:
               - Token prices
               - Market capitalization
               - Price changes/trends
               - Trading volume
               - Token liquidity
               - Market data
               - Token pairs information
               - Token contract information
            
            2. "swap" - For queries about:
               - Buying tokens
               - Selling tokens
               - Token swaps
               - Trading execution
               - Best routes for trades
               - Slippage calculations
               - Gas fees for trades
            
            3. "openai" - For all other queries, including:
               - General crypto questions
               - Market analysis
               - News and updates
               - Technical explanations
               - Blockchain concepts
               - Project information
            
            Respond ONLY with one of these exact strings: "dexscreener", "swap", or "openai"
            """

            user_prompt = f"Route this query: {query}"
            
            if context:
                last_interaction = context[-1]
                user_prompt += f"\nPrevious interaction type: {last_interaction.get('type', 'none')}"

            response = self.openai_agent.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=10,
                temperature=0
            )

            agent_type = response.choices[0].message.content.strip().lower()
            logger.info(f"OpenAI selected agent '{agent_type}' for query: '{query}'")

            # Validate response
            if agent_type not in ["dexscreener", "swap", "openai"]:
                logger.warning(f"Invalid agent type '{agent_type}' returned, defaulting to 'openai'")
                return "openai"

            return agent_type

        except Exception as e:
            logger.error(f"Error in determine_agent: {str(e)}")
            return "openai"  # Default to OpenAI on error

    def process_query(self, query: str, context: List[Dict]) -> Dict[str, Any]:
        """
        Process the query using the appropriate agent while maintaining context
        """
        try:
            agent_type = self.determine_agent(query, context)
            logger.info(f"Selected agent: {agent_type}")

            # Process query based on agent type
            if agent_type == 'dexscreener':
                # Clean and prepare the query
                clean_query = query.lower().strip()
                
                # Extract token symbol
                token = self.extract_token_from_query(clean_query)
                logger.info(f"Extracted token: {token}")
                
                if token:
                    # Search for the token
                    search_response = self.dexscreener_agent.search_tokens(token)
                    
                    if search_response.get('status') == 'success' and search_response.get('data'):
                        # Use the first result's data
                        response = {
                            "response": search_response['response'],
                            "data": search_response['data'][0] if isinstance(search_response['data'], list) else search_response['data'],
                            "status": "success",
                            "type": "dexscreener"
                        }
                    else:
                        response = search_response
                else:
                    # If no specific token found, use the whole query for search
                    response = self.dexscreener_agent.search_tokens(clean_query)
                
                logger.info(f"DexScreener response status: {response.get('status')}")
                return response
            else:
                # Prepare context for OpenAI
                context_prompt = self.prepare_context_for_openai(context)
                full_prompt = f"{context_prompt}\nUser: {query}"
                response = self.openai_agent.respond(full_prompt)
                return response

        except Exception as e:
            logger.error(f"Error in orchestrator: {str(e)}")
            return {
                "response": f"Error processing request: {str(e)}",
                "status": "error",
                "type": "error"
            }

    def extract_token_from_query(self, query: str) -> str:
        """
        Extract token name or symbol from natural language query
        """
        query_lower = query.lower()
        
        # Token mapping for common cryptocurrencies
        token_map = {
            'bitcoin': 'BTC',
            'btc': 'BTC',
            'ethereum': 'ETH',
            'eth': 'ETH',
            'solana': 'SOL',
            'sol': 'SOL',
            'usdt': 'USDT',
            'usdc': 'USDC'
        }
        
        # Check for known tokens in query
        for token_name, symbol in token_map.items():
            if token_name in query_lower:
                return symbol
                
        return ""

    def prepare_context_for_openai(self, context: List[Dict]) -> str:
        """
        Prepare conversation context for OpenAI
        """
        if not context:
            return ""
            
        context_messages = []
        for msg in context[-3:]:  # Use last 3 messages for context
            if msg.get('response'):
                context_messages.append(f"Assistant: {msg['response']}")
            if msg.get('query'):
                context_messages.append(f"User: {msg['query']}")
                
        return "\n".join(context_messages)

class ContextManager:
    """
    Manages conversation context and metadata across different agents
    """
    
    def __init__(self, max_context: int = 10):
        self.context = deque(maxlen=max_context)
        self.metadata = {}
        
    def add_interaction(self, query: str, response: Dict[str, Any], agent_type: str):
        """Add an interaction to the context"""
        logger.debug(f"Adding interaction: {query} - {response} - {agent_type}")
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
                    'last_name': response['data'].get('name'),
                    'last_symbol': response['data'].get('symbol'),
                    'last_price': response['data'].get('price'),
                    'last_chain': response['data'].get('chain'),
                    'last_ca': response['data'].get('contract_address'),
                    'last_market_cap': response['data'].get('market_cap'),
                    'last_liquidity': response['data'].get('liquidity'),
                    'last_volume_24h': response['data'].get('volume_24h')
                })
            else:
                logger.info(f"No data in response: {response}")
                
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
                # Try token search
                logger.debug(f"selected dexscreener agent with input: {user_input}")
                response = self.dexscreener_agent.process_query(user_input)
                logger.debug(f"DexScreener response status: {response.get('status')}")
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
                response = self.openai_agent.process_query(enhanced_input)
            
            # Update context with new interaction
            self.context_manager.add_interaction(user_input, response, agent_type)
            logger.info(f"Context: {self.context_manager.get_context()}")
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