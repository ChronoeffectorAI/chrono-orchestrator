# ChronoEffector AI Agent Orchestrator Framework 🌟

<p align="center">
  <img src="docs/logo.png" alt="ChronoEffector Logo" width="200"/>
</p>

## 🚀 Overview

ChronoEffector is a cutting-edge AI Agent Orchestrator Framework designed for building sophisticated, context-aware AI applications. It excels at managing multiple AI agents, maintaining conversation context across agent switches, and providing seamless integration with various AI models and data sources.

### 🌟 Key Features
- 🧠 Multi-Model AI Support (OpenAI, Anthropic, Custom Models)
- 🔄 Intelligent Agent Orchestration
- 💾 Persistent Context Management
- 📈 Real-time Crypto Market Data Integration
- 🎯 Extensible Plugin Architecture
- 💻 Modern Chat Interface
- 🔗 Cross-Agent Context Preservation

## 🧠 Intelligent Agent Orchestration

### Core Components

#### 1. Agent Router
The AgentRouter is the brain of the system, making intelligent decisions about which agent should handle each query:

```python
router = AgentRouter()
agent_type = router.determine_agent(query, context)
```

**Features:**
- **Keyword-Based Analysis**: Maintains sets of keywords for different query types:
  ```python
  MARKET_KEYWORDS = {
      'price', 'token', 'pair', 'liquidity', 'volume',
      'market cap', 'crypto', 'dex', 'swap', 'trading'
  }
  
  ANALYSIS_KEYWORDS = {
      'analyze', 'explain', 'why', 'how', 'what',
      'strategy', 'opinion', 'recommend'
  }
  ```

- **Confidence Scoring**: Calculates confidence scores for each agent type:
  - Market Data Confidence: Based on token addresses, market keywords
  - Analysis Confidence: Based on analytical keywords, context
  - Historical Context: Uses recent interactions to maintain conversation flow

- **Smart Routing Logic**: 
  ```python
  if market_confidence > CONFIDENCE_THRESHOLD:
      return 'dexscreener'
  elif analysis_confidence > CONFIDENCE_THRESHOLD:
      return 'openai'
  else:
      # Fall back to context or default
  ```

#### 2. Context Manager
Maintains conversation state and cross-agent context:

```python
context_manager = ContextManager(max_context=10)
```

**Capabilities:**
- **Interaction Tracking**:
  ```python
  {
      'timestamp': '2024-01-20T14:30:00Z',
      'query': 'What's the price of ETH?',
      'response': {...},
      'agent_type': 'dexscreener'
  }
  ```

- **Metadata Management**:
  ```python
  metadata = {
      'last_token': 'ETH',
      'last_price': '$2,500',
      'last_chain': 'ethereum'
  }
  ```

- **Context Window**: Maintains last N interactions for context-aware responses

#### 3. Main Orchestrator
Coordinates all components and manages the flow of information:

```python
class Orchestrator:
    def __init__(self):
        self.openai_agent = OpenAIAgent()
        self.dexscreener_agent = DexscreenerAgent()
        self.router = AgentRouter()
        self.context_manager = ContextManager()
```

**Key Functions:**
- **Input Processing**:
  ```python
  response = orchestrator.handle_input("What's the price of ETH?")
  ```

- **Context-Enhanced Prompts**:
  ```python
  enhanced_input = f"""
  Context: Last token discussed was {metadata['last_token']} 
  at price {metadata['last_price']} 
  on {metadata['last_chain']}.

  Query: {user_input}
  """
  ```

### Example Flows

1. **Market Data Query**:
```python
Input: "Show me the price of ETH"
-> Router identifies market keywords
-> Confidence: Market (0.8) > Analysis (0.2)
-> Routes to DexscreenerAgent
-> Updates context with price data
```

2. **Analysis Query with Context**:
```python
Input: "Why did it drop so much?"
-> Router checks context (previous ETH discussion)
-> Enhances prompt with price context
-> Routes to OpenAI for analysis
```

3. **Mixed Query Handling**:
```python
Input: "Should I buy ETH at current price?"
-> Router detects both market and analysis keywords
-> Fetches price data from Dexscreener
-> Enhances OpenAI prompt with current market data
-> Provides analysis with market context
```

### Extending the Router

Add custom routing logic by extending the AgentRouter:

```python
class CustomRouter(AgentRouter):
    def __init__(self):
        super().__init__()
        self.TECHNICAL_KEYWORDS = {
            'RSI', 'MACD', 'moving average',
            'support', 'resistance'
        }

    def calculate_technical_confidence(self, query: str) -> float:
        # Custom confidence calculation
        pass

    def determine_agent(self, query: str, context: List[Dict]) -> str:
        if self.calculate_technical_confidence(query) > 0.8:
            return 'technical_analysis'
        return super().determine_agent(query, context)
```

### Context Preservation

The system maintains context across different agents:

1. **Short-term Memory**:
   - Last N interactions
   - Recent agent selections
   - Query patterns

2. **Metadata Storage**:
   - Token information
   - Price data
   - Chain context

3. **Cross-Agent Context**:
   - Market data enriches analysis
   - Analysis history influences market queries
   - Seamless context switching

### Performance Optimization

The orchestrator includes several optimization features:

1. **Confidence Thresholds**:
   - Adjustable confidence levels
   - Prevents unnecessary agent switching
   - Optimizes response time

2. **Context Window Management**:
   - Fixed-size deque for memory efficiency
   - Automatic pruning of old context
   - Relevant metadata preservation

3. **Error Handling**:
   - Graceful fallback mechanisms
   - Detailed error logging
   - Recovery strategies

## 🏗️ Architecture

### Core Components

1. **Agent Orchestrator**
   - Dynamic agent routing based on query context
   - Intelligent load balancing between models
   - Context preservation across agent switches
   - Real-time agent performance monitoring

2. **AI Agents**
   - **Language Model Agents**:
     - OpenAI (GPT-4, GPT-3.5)
     - Anthropic (Claude)
     - Custom LLM Integration Support
   - **Market Data Agents**:
     - DexscreenerAgent (Comprehensive DEX Data)
     - Custom Data Source Integration
   - **Specialized Agents**:
     - Technical Analysis
     - Market Sentiment
     - Risk Assessment

### DexscreenerAgent Capabilities

The DexscreenerAgent provides comprehensive cryptocurrency market data with three main functions:

1. **Token Information** (`get_price_data`):
   ```python
   response = agent.get_price_data("0x123...")  # Token address
   ```
   Returns:
   - Current price with USD formatting
   - Price changes (5m, 1h, 24h)
   - Market capitalization
   - Liquidity metrics
   - 24h trading volume
   - Chain and DEX information

2. **Pair Analysis** (`get_pair_data`):
   ```python
   response = agent.get_pair_data("0x456...")  # Pair address
   ```
   Returns:
   - Trading pair details
   - Liquidity information
   - Volume metrics
   - Exchange and chain data

3. **Token Search** (`search_tokens`):
   ```python
   response = agent.search_tokens("ethereum")  # Search query
   ```
   Returns:
   - Top 5 results by liquidity
   - Token names and symbols
   - Current prices
   - Liquidity information
   - Chain and DEX details

Example Response Format:
```python
{
    "response": "Formatted message for display",
    "data": {
        "name": "Ethereum",
        "symbol": "ETH",
        "price": "$1,234.56",
        "price_changes": {
            "5m": "+0.5%",
            "1h": "-1.2%",
            "24h": "+3.4%"
        },
        "market_cap": "$150.5B",
        "liquidity": "$25.6M",
        "volume_24h": "$1.2B"
    },
    "status": "success",
    "type": "dexscreener"
}
```

## 🛠️ Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd chronoeffector
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   pip install -r frontend/requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp backend/.env.example backend/.env
   ```
   Add your API keys:
   ```plaintext
   OPENAI_API_KEY=your-openai-key
   ANTHROPIC_API_KEY=your-anthropic-key
   CUSTOM_MODEL_ENDPOINT=your-endpoint
   ```
5. Optional : You can use run.sh to start the backend and frontend and have all the environment variables set up for you
```bash
./run.sh
```
## 🚀 Running the Framework

1. Start the backend:
   ```bash
   cd backend
   python app.py
   ```

2. Launch the frontend:
   ```bash
   cd frontend
   chainlit run main.py
   ```

Access the interface at http://localhost:8000

## 🔧 Extending the Framework

### Adding Custom Agents

1. Create a new agent class:
```python
class CustomAgent:
    def __init__(self, model_adapter: BaseModel):
        self.model = model_adapter
        self.context_manager = ContextManager()

    async def process(self, input_data: str) -> Dict[str, Any]:
        context = self.context_manager.get_context()
        response = await self.model.generate_response(input_data, context)
        self.context_manager.update_context(response)
        return {
            "response": response,
            "status": "success",
            "type": "custom_agent"
        }
```

### Context Management

```python
class ContextManager:
    def __init__(self):
        self.context_window = deque(maxlen=10)
        self.metadata = {}

    def update_context(self, new_data: Dict[str, Any]):
        self.context_window.append(new_data)
        self.metadata.update(new_data.get("metadata", {}))
```

## 🔍 Advanced Features

### Model Switching
- Query complexity-based routing
- Performance optimization
- Cost management
- Specialized capability routing

### Context Preservation
- Cross-agent state management
- Conversation history
- Metadata persistence
- Smart context pruning

### Market Data Integration
- Real-time price feeds
- Liquidity tracking
- Volume analysis
- Market trend detection

## 🛣️ Roadmap

### Q1 2025
- [ ] Market Analysis Agents
  - [ ] Sentiment Analysis Agent
    - Social media sentiment tracking (Twitter, Reddit, Telegram)
    - News sentiment aggregation
    - Community mood analysis
  - [ ] KOL Analysis Agent
    - Crypto influencer tracking
    - Trading signal monitoring
    - Wallet movement analysis
  - [ ] Trend Detection Agent
    - Token trending metrics
    - Volume spike detection
    - Social mention tracking

### Q2 2025
- [ ] Technical Analysis Suite
  - [ ] Pattern Recognition Agent
    - Chart pattern identification
    - Support/Resistance levels
    - Trend line analysis
    - More complex chart indicators
  - [ ] Indicator Agent
    - Custom indicator calculations
    - Multi-timeframe analysis
    - Signal generation
  - [ ] Correlation Agent
    - Cross-chain correlations
    - Market sector analysis
    - Beta calculation

### Q3 2025
- [ ] Advanced Data Integration
  - [ ] On-Chain Analysis Agent
    - Whale wallet tracking
    - Smart money flow analysis
    - Contract interaction monitoring
  - [ ] DEX Analytics Agent
    - Liquidity flow tracking
    - Swap volume analysis
    - Price impact calculation
  - [ ] Vector Database Integration
    - Historical pattern matching
    - Similar market conditions
    - Pattern-based predictions

### Q4 2025
- [ ] AI Enhancement
  - [ ] Multi-Modal Support
    - Chart image analysis
    - Video content processing
    - Voice command integration
  - [ ] Custom Model Training
    - Market-specific fine-tuning
    - Pattern recognition models
    - Prediction model development
  - [ ] Advanced Context Management
    - Long-term market memory
    - Cross-chain context
    - Market cycle awareness


### Research & Development
- [ ] Novel Agent Types
  - [ ] Market Psychology Agent
    - Fear/Greed analysis
    - Market manipulation detection
    - FUD/FOMO signal analysis
    - Crowd behavior modeling
    - Bundled token analysis

Each phase builds upon previous developments, creating an increasingly sophisticated and capable trading analysis system. The roadmap emphasizes:
- Market-specific AI capabilities
- Real-time data processing
- Advanced analysis techniques
- Community engagement

Progress will be tracked in our public GitHub repository, and community feedback will help prioritize features.

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🌟 Why ChronoEffector?

Perfect for building:
- Crypto Trading Systems
- Market Analysis Platforms
- Portfolio Management Tools

Features:
- Advanced context management
- Multi-model support
- Real-time market data
- Extensible architecture
- Production-ready design 

## 🔧 Creating New Agents

### Agent Architecture

The framework uses an abstract base agent class that all agents must inherit from. Each agent must implement certain required methods and can optionally override others for custom behavior.

### 1. Create a New Agent Class

Create a new file in `backend/agents/` (e.g., `custom_agent.py`):

```python
from .base_agent import BaseAgent
from typing import Dict, Any, Optional

class CustomAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        # Initialize any agent-specific resources
        self.some_client = SomeClient()

    def description(self) -> str:
        """
        Define the agent's capabilities for the router.
        This description is used to determine if this agent 
        should handle specific queries.
        """
        return """
        Handles queries about:
        - Specific capability 1
        - Specific capability 2
        - Type of queries it handles
        - Specific data it can process
        - Special features it provides
        """

    def process_query(self, query: str, shared_context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process user queries and return responses.
        """
        try:
            # Use shared context if relevant
            if shared_context:
                # Enhance query with context
                pass

            # Process the query
            result = self._process_query_logic(query)
            
            # Format the response
            response = self.format_response(
                message=result['message'],
                data=result['data']
            )
            
            # Add to agent's context
            self.add_to_context(query, response)
            
            return response
            
        except Exception as e:
            return self.handle_error(e, "while processing custom query")

    def update_shared_context(self, interaction: Dict[str, Any]) -> None:
        """
        Update shared context with agent-specific information
        """
        super().update_shared_context(interaction)
        
        # Add agent-specific context
        if interaction['response'].get('data'):
            data = interaction['response']['data']
            self.shared_context.update({
                'custom_key_1': data.get('some_value'),
                'custom_key_2': data.get('other_value')
            })
```

### 2. Required Methods

Every agent must implement these methods:

1. `description()` -> str
   - Returns a detailed description of the agent's capabilities
   - Used by the router to determine which agent should handle a query
   - Should be specific and comprehensive

2. `process_query(query: str, shared_context: Optional[Dict] = None) -> Dict[str, Any]`
   - Main method for processing user queries
   - Must return a dictionary with at least:
     ```python
     {
         "response": str,  # The formatted response text
         "status": str,    # 'success' or 'error'
         "type": str       # The agent type identifier
     }
     ```

### 3. Optional Methods to Override

1. `update_shared_context(interaction: Dict[str, Any]) -> None`
   - Customize how the agent updates shared context
   - Called automatically after each interaction

2. `format_response(message: str, data: Any = None, status: str = "success") -> Dict[str, Any]`
   - Customize response formatting if needed
   - Base implementation usually sufficient

### 4. Register the Agent

Add the new agent to the Orchestrator in `backend/orchestrator.py`:

```python
from agents.custom_agent import CustomAgent

class Orchestrator:
    def __init__(self):
        self.agents = {}
        self.context_manager = ContextManager()
        
        # Register all agents
        self._register_agents([
            OpenAIAgent(),
            DexscreenerAgent(),
            SwapAgent(),
            CustomAgent()  # Add your new agent here
        ])
        
        # Initialize router with registered agents
        self.router = AgentRouter(self.agents)
```

### 5. Agent Features

Your agent automatically gets these features:

- **Context Management**: 
  - Maintains conversation history
  - Shares context with other agents
  - Automatic context window management

- **Error Handling**:
  - Consistent error formatting
  - Automatic logging
  - Error context preservation

- **Response Formatting**:
  - Standardized response structure
  - Data payload support
  - Status tracking

### 6. Best Practices

1. **Description Writing**:
   - Be specific about capabilities
   - List all query types handled
   - Include relevant keywords
   - Make it easy for the router to understand

2. **Context Usage**:
   - Use shared context when relevant
   - Update context with useful information
   - Keep context data clean and relevant

3. **Error Handling**:
   - Use the provided `handle_error` method
   - Include meaningful error contexts
   - Log appropriate information

4. **Response Formatting**:
   - Use `format_response` for consistency
   - Include relevant data payloads
   - Maintain response structure

### Example Agents

See existing agents for implementation examples:
- `OpenAIAgent`: General query handling
- `DexscreenerAgent`: Market data processing
- `SwapAgent`: Transaction handling

Each demonstrates different aspects of agent implementation and specialization. 