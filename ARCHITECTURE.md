# System Architecture

## Overview

Sentinel OS is a multi-agent arbitrage system built with Python, using asyncio for concurrent execution. The system consists of three specialized agents coordinated by an orchestrator, with built-in risk management and non-custodial wallet support.

## Component Diagram

```
┌─────────────────────────────────────────────────────────┐
│                     ORCHESTRATOR                        │
│  - Asyncio event loop                                   │
│  - Concurrent agent execution                           │
│  - Bulletproof error handling                           │
│  - Exponential backoff retry logic                      │
└───────────────┬─────────────────────────────────────────┘
                │
        ┌───────┴────────┬───────────────┬───────────────┐
        │                │               │               │
        ▼                ▼               ▼               ▼
┌──────────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│  GPU SNIPER  │  │   RWA    │  │ AUDITOR  │  │  WALLET  │
│              │  │ FLIPPER  │  │          │  │          │
│ VRAM gaps    │  │ Property │  │ Net      │  │ ERC-4337 │
│ 15% margin   │  │ news     │  │ profit   │  │ session  │
│              │  │ 10% margin  │ tracking │  │ keys     │
└──────────────┘  └──────────┘  └──────────┘  └──────────┘
        │                │               │               │
        └────────────────┴───────────────┴───────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │   RISK MANAGER         │
                    │  - $50 cap             │
                    │  - 2FA for >$20        │
                    │  - Rate limiting       │
                    │  - Telegram bot        │
                    └────────────────────────┘
```

## Core Components

### 1. Wallet (`core/wallet.py`)

**Purpose:** Non-custodial wallet with ERC-4337 session keys

**Key Features:**
- Account management via eth-account
- Session key creation with permissions
- Transaction signing and sending
- Automatic expiration handling

**Session Keys:**
```python
session_key = wallet.create_session_key(
    max_amount=10.0,      # Max $10 per transaction
    duration_hours=24     # Valid for 24 hours
)
```

**Security:**
- Private keys never leave the server
- Session keys have limited permissions
- Automatic cleanup of expired keys

### 2. Risk Manager (`core/risk.py`)

**Purpose:** Transaction validation and Telegram 2FA

**Limits:**
- Maximum transaction: $50 USD
- 2FA threshold: $20 USD
- Rate limit: 10 transactions/hour

**Workflow:**
```
Transaction Request
        ↓
    Amount ≤ $50? ──No──→ REJECT
        ↓ Yes
    Amount > $20? ──Yes──→ Request Telegram 2FA ──→ Wait for approval
        ↓ No                                              ↓
    Check rate limit ──→ Within limits? ──Yes──→ APPROVE
        ↓ No
    REJECT
```

### 3. Orchestrator (`core/orchestrator.py`)

**Purpose:** Coordinate multiple agents concurrently

**Features:**
- Asyncio-based concurrent execution
- Bulletproof error handling (3 retries per agent)
- Exponential backoff on failures
- Automatic cleanup of expired resources

**Execution Flow:**
```python
while running:
    # Run all agents concurrently
    results = await asyncio.gather(*[
        run_agent_safe(agent1),
        run_agent_safe(agent2),
        run_agent_safe(agent3)
    ])
    
    # Cleanup
    wallet.cleanup_expired_keys()
    risk_manager.cleanup_expired_approvals()
    
    # Wait before next cycle
    await asyncio.sleep(60)
```

## Agent Architecture

### Base Agent Interface

All agents implement:
```python
async def execute(self, wallet, risk_manager) -> Dict[str, Any]:
    """
    Main execution method.
    
    Returns:
        {
            'success': bool,
            'opportunities': List[...],
            'trades': List[...],
            ...
        }
    """
```

### 1. GPU Sniper Agent (`agents/gpu_sniper.py`)

**Target:** GPU rental market inefficiencies

**Strategy:**
1. Fetch prices from multiple providers (RunPod, VastAI, LambdaLabs)
2. Group by GPU type and VRAM
3. Find price gaps ≥15%
4. Execute arbitrage trades

**Example Opportunity:**
```python
{
    'gpu_type': 'RTX 4090',
    'vram_gb': 24,
    'buy_from': 'VastAI',
    'buy_price': 0.65,
    'sell_to': 'RunPod',
    'sell_price': 0.79,
    'profit_margin': 0.215  # 21.5%
}
```

### 2. RWA Flipper Agent (`agents/rwa_flipper.py`)

**Target:** Tokenized real estate arbitrage

**Strategy:**
1. Fetch property news (development approvals, tech hubs, etc.)
2. Fetch RWA listings (RealT, Lofty, Slice)
3. Match positive news with undervalued properties
4. Execute trades with ≥10% margin

**Example Opportunity:**
```python
{
    'property': 'Miami Beach Condo #42',
    'platform': 'RealT',
    'current_price': 50.0,
    'estimated_value': 57.5,
    'profit_margin': 0.15,  # 15%
    'news_catalyst': 'Downtown development approval'
}
```

### 3. Auditor Agent (`agents/auditor.py`)

**Purpose:** System monitoring and profit tracking

**Responsibilities:**
1. Fetch transaction history
2. Calculate net profit/loss
3. Monitor risk thresholds
4. Generate audit reports

**Metrics Tracked:**
- Total profit/loss (USD)
- Win rate (%)
- Transaction count
- Risk warnings

## Error Handling

### Bulletproof Loops

Every agent and operation uses:

```python
max_retries = 3
retry_count = 0

while retry_count < max_retries:
    try:
        # Operation
        return success
    except Exception as e:
        retry_count += 1
        if retry_count >= max_retries:
            return failure
        await asyncio.sleep(2 ** retry_count)  # Exponential backoff
```

### Timeout Protection

```python
result = await asyncio.wait_for(
    agent.execute(wallet, risk_manager),
    timeout=300  # 5 minutes
)
```

### Exception Isolation

Each agent runs independently. If one fails, others continue:

```python
results = await asyncio.gather(*tasks, return_exceptions=False)
# Each task has internal try/except
# Orchestrator sees AgentResult with success/failure
```

## Data Flow

```
1. Orchestrator starts cycle
   ↓
2. Agents execute concurrently
   ↓
3. Agents fetch market data
   ↓
4. Agents analyze opportunities
   ↓
5. Agents request validation from Risk Manager
   ↓
6. Risk Manager checks limits & 2FA
   ↓
7. Approved trades execute via Wallet
   ↓
8. Auditor tracks results
   ↓
9. Orchestrator waits 60s
   ↓
10. Repeat
```

## Security Layers

1. **ERC-4337 Session Keys** - Limited permissions per session
2. **Transaction Caps** - Hard $50 limit
3. **2FA** - Telegram approval for >$20
4. **Rate Limiting** - Max 10 tx/hour
5. **Profit Margins** - Only trade with sufficient margin
6. **Error Recovery** - Automatic retry with backoff

## Performance

- **Cycle Time:** ~3-5 seconds per cycle
- **Agent Concurrency:** All 3 agents run in parallel
- **Retry Delay:** Exponential backoff (2s, 4s, 8s)
- **Timeout:** 5 minutes per agent
- **Interval:** 60 seconds between cycles

## Dependencies

**Core:**
- `web3` - Ethereum interaction
- `eth-account` - Account management
- `asyncio` - Concurrent execution

**Optional:**
- `python-telegram-bot` - 2FA
- `langgraph` - Agent framework
- `skyfire` - SDK integration

**Testing:**
- `pytest` - Test framework
- `pytest-asyncio` - Async tests
