import requests
from typing import Dict, Any, Optional
from datetime import datetime
import logging
import os
from openai import OpenAI
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DexscreenerAgent:
    """
    DexscreenerAgent fetches comprehensive token information from the Dexscreener API.
    Includes market cap, volume, price changes, and liquidity data.
    """
    
    BASE_URL = "https://api.dexscreener.com/latest/dex"
    
    def __init__(self):
        self.session = requests.Session()
        logger.info("DexscreenerAgent initialized")
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    

    def get_token_identifiers(self, user_input: str) -> Optional[str]:
        try:
            system_prompt = "You are a helpful crypto expert that extracts token identifiers from user input. return only two things ticker: and contract_address: if a ticker is not present, return None for ticker. if a contract_address is not present, return None for contract_address."
            user_prompt = f"User input: {user_input}"
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                max_tokens=150
            )
            response_text = response.choices[0].message.content
            
            # Regular expressions to extract ticker and contract address
            ticker_match = re.search(r'ticker:\s*(\w+)', response_text)
            contract_match = re.search(r'contract_address:\s*(\w+)', response_text)
            
            ticker = ticker_match.group(1) if ticker_match else None
            contract = contract_match.group(1) if contract_match else None
            
            logger.info(f"Extracted - Ticker: {ticker}, Contract: {contract}")
            
            # Return the ticker if found, otherwise return None
            return ticker , contract if ticker and ticker.lower() != 'none' and contract and contract.lower() != 'none' else None

        except Exception as e:
            logger.error(f"Error getting token identifiers: {str(e)}")
            return None

    def format_currency(self, value: float) -> str:
        """Format currency values with appropriate suffixes (K, M, B)"""
        if value >= 1_000_000_000:
            return f"${value/1_000_000_000:.2f}B"
        elif value >= 1_000_000:
            return f"${value/1_000_000:.2f}M"
        elif value >= 1_000:
            return f"${value/1_000:.2f}K"
        return f"${value:.2f}"

    def format_percentage(self, value: Optional[float]) -> str:
        """Format percentage values"""
        if value is None:
            return "N/A"
        return f"{value:+.2f}%"

    def get_price_data(self, user_input: str) -> Dict[str, Any]:
        logger.info(f"Fetching price data for token: {user_input}")
        """
        Fetch detailed token information from Dexscreener.
        
        Args:
            token_address: Token contract address
            
        Returns:
            Dictionary containing formatted token information
        """
        data = self.get_token_identifiers(user_input)
        logger.info(f"Token identifiers: {data}")
        try:
            url = f"{self.BASE_URL}/search?q={data}"
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            #logger.info(f"Received data: {data}")
            if not data.get("pairs"):
                return {
                    "response": "No data found for this token",
                    "status": "error",
                    "type": "dexscreener"
                }

            # Get the most liquid pair
            pair = max(data["pairs"], key=lambda x: float(x.get("liquidity", {}).get("usd", 0)))
            
            # Extract and format data
            price_usd = float(pair.get("priceUsd", 0))
            price_change_5m = pair.get("priceChange", {}).get("m5")
            price_change_1h = pair.get("priceChange", {}).get("h1")
            price_change_24h = pair.get("priceChange", {}).get("h24")
            liquidity_usd = float(pair.get("liquidity", {}).get("usd", 0))
            volume_24h = float(pair.get("volume", {}).get("h24", 0))
            
            # Calculate market cap if available
            circulating_supply = pair.get("liquidity", {}).get("circulating")
            market_cap = price_usd * circulating_supply if circulating_supply else None
            
            # Format response
            token_info = {
                "name": pair.get("baseToken", {}).get("name", "Unknown"),
                "symbol": pair.get("baseToken", {}).get("symbol", "Unknown"),
                "price": self.format_currency(price_usd),
                "price_changes": {
                    "5m": self.format_percentage(price_change_5m),
                    "1h": self.format_percentage(price_change_1h),
                    "24h": self.format_percentage(price_change_24h)
                },
                "liquidity": self.format_currency(liquidity_usd),
                "volume_24h": self.format_currency(volume_24h),
                "market_cap": self.format_currency(market_cap) if market_cap else "N/A",
                "dex": pair.get("dexId", "Unknown"),
                "chain": pair.get("chainId", "Unknown"),
                "pair_address": pair.get("pairAddress", "Unknown"),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Create formatted message
            message = (
                f"📊 {token_info['name']} ({token_info['symbol']})\n\n"
                f"💰 Price: {token_info['price']}\n"
                f"📈 Price Changes:\n"
                f"   • 5m:  {token_info['price_changes']['5m']}\n"
                f"   • 1h:  {token_info['price_changes']['1h']}\n"
                f"   • 24h: {token_info['price_changes']['24h']}\n\n"
                f"💎 Market Cap: {token_info['market_cap']}\n"
                f"💧 Liquidity: {token_info['liquidity']}\n"
                f"📊 24h Volume: {token_info['volume_24h']}\n\n"
                f"🔗 Chain: {token_info['chain']}\n"
                f"🏢 DEX: {token_info['dex']}\n"
            )

            return {
                "response": message,
                "data": token_info,
                "status": "success",
                "type": "dexscreener"
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data from Dexscreener: {str(e)}")
            return {
                "response": f"Error fetching token data: {str(e)}",
                "status": "error",
                "type": "dexscreener"
            }
        except Exception as e:
            logger.error(f"Unexpected error in DexscreenerAgent: {str(e)}")
            return {
                "response": f"An unexpected error occurred: {str(e)}",
                "status": "error",
                "type": "dexscreener"
            }

    def get_pair_data(self, pair_address: str) -> Dict[str, Any]:
        logger.info(f"Fetching pair data for pair: {pair_address}")
        """
        Fetch detailed information about a specific trading pair.
        
        Args:
            pair_address: DEX pair contract address
            
        Returns:
            Dictionary containing pair information
        """
        try:
            url = f"{self.BASE_URL}/pairs/{pair_address}"
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            if not data.get("pairs"):
                return {
                    "response": "No data found for this pair",
                    "status": "error",
                    "type": "dexscreener"
                }

            pair = data["pairs"][0]
            
            # Format pair information
            pair_info = {
                "token0": pair.get("baseToken", {}).get("symbol", "Unknown"),
                "token1": pair.get("quoteToken", {}).get("symbol", "Unknown"),
                "price": self.format_currency(float(pair.get("priceUsd", 0))),
                "liquidity": self.format_currency(float(pair.get("liquidity", {}).get("usd", 0))),
                "volume_24h": self.format_currency(float(pair.get("volume", {}).get("h24", 0))),
                "dex": pair.get("dexId", "Unknown"),
                "chain": pair.get("chainId", "Unknown")
            }
            
            message = (
                f"⚖️ Pair: {pair_info['token0']}/{pair_info['token1']}\n\n"
                f"💰 Price: {pair_info['price']}\n"
                f"💧 Liquidity: {pair_info['liquidity']}\n"
                f"📊 24h Volume: {pair_info['volume_24h']}\n\n"
                f"🔗 Chain: {pair_info['chain']}\n"
                f"🏢 DEX: {pair_info['dex']}\n"
            )

            return {
                "response": message,
                "data": pair_info,
                "status": "success",
                "type": "dexscreener"
            }

        except Exception as e:
            logger.error(f"Error fetching pair data: {str(e)}")
            return {
                "response": f"Error fetching pair data: {str(e)}",
                "status": "error",
                "type": "dexscreener"
            }

  
    
    def search_tokens(self, query: str) -> Dict[str, Any]:
        logger.info(f"Searching for tokens matching: {query}")
        """
        Search for tokens by name or symbol.
        
        Args:
            query: Search query string
            
        Returns:
            Dictionary containing search results
        """
        try:
            ticker , contract = self.get_token_identifiers(query)
            query = None
            if contract:
                query = contract
            else:
                query = ticker
            logger.info(f"seraching for : {query}")
            url = f"{self.BASE_URL}/search?q={query}"
            logger.info(f"Fetching data from: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            if not data.get("pairs"):
                return {
                    "response": f"No tokens found matching '{query}'",
                    "status": "error",
                    "type": "dexscreener"
                }

            # Get top 5 results
            top_pairs = sorted(
                data["pairs"],
                key=lambda x: float(x.get("liquidity", {}).get("usd", 0)),
                reverse=True
            )[:1]

            results = []
            for pair in top_pairs:
                token_info = {
                    "name": pair.get("baseToken", {}).get("name", "Unknown"),
                    "symbol": pair.get("baseToken", {}).get("symbol", "Unknown"),
                    "price": self.format_currency(float(pair.get("priceUsd", 0))),
                    "liquidity": self.format_currency(float(pair.get("liquidity", {}).get("usd", 0))),
                    "chain": pair.get("chainId", "Unknown"),
                    "dex": pair.get("dexId", "Unknown")
                }
                results.append(token_info)

            # Format message
            message = f"🔍 Search Results for '{query}':\n\n"
            for idx, result in enumerate(results, 1):
                message += (
                    f"{idx}. {result['name']} ({result['symbol']})\n"
                    f"   💰 Price: {result['price']}\n"
                    f"   💧 Liquidity: {result['liquidity']}\n"
                    f"   🔗 {result['chain']} - {result['dex']}\n\n"
                )

            return {
                "response": message,
                "data": results,
                "status": "success",
                "type": "dexscreener"
            }

        except Exception as e:
            logger.error(f"Error searching tokens: {str(e)}")
            return {
                "response": f"Error searching tokens: {str(e)}",
                "status": "error",
                "type": "dexscreener"
            } 