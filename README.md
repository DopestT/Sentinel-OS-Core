# Sentinel-OS-Core
Multi-Agent Arbitrage System

A Python-based multi-agent arbitrage system using LangGraph & Skyfire SDK for automated trading opportunities across GPU rentals and Real-World Assets (RWA).

## 🚀 Features

- **Multi-Agent Architecture**: Three specialized agents working concurrently
  - **GPU Sniper**: Detects VRAM arbitrage opportunities across GPU rental markets
  - **RWA Flipper**: Monitors property news for tokenized real estate arbitrage
  - **Auditor**: Tracks net profit and system performance

- **Security & Risk Management**
  - ERC-4337 session keys for non-custodial execution
  - $50 transaction cap enforced by risk manager
  - Telegram 2FA for transactions over $20
  - Bulletproof error handling with exponential backoff

- **Concurrent Execution**: Asyncio-based orchestrator runs all agents in parallel

- **Production Ready**: Configured for Railway.app deployment

## 📁 Project Structure

```
Sentinel-OS-Core/
├── core/
│   ├── __init__.py
│   ├── wallet.py          # ERC-4337 session key wallet
│   ├── risk.py            # Risk management with Telegram 2FA
│   └── orchestrator.py    # Asyncio agent orchestration
├── agents/
│   ├── __init__.py
│   ├── gpu_sniper.py      # GPU VRAM arbitrage agent
│   ├── rwa_flipper.py     # Real estate arbitrage agent
│   └── auditor.py         # Net profit tracking agent
├── requirements.txt       # Python dependencies
├── Procfile              # Railway.app configuration
├── .env.example          # Environment variables template
└── README.md
```

## 🔧 Installation

1. Clone the repository:
```bash
git clone https://github.com/DopestT/Sentinel-OS-Core.git
cd Sentinel-OS-Core
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

## ⚙️ Configuration

Create a `.env` file with the following variables:

```env
# Wallet Configuration
WALLET_PRIVATE_KEY=your_private_key_here
RPC_URL=https://eth-mainnet.g.alchemy.com/v2/your_api_key

# Telegram 2FA Configuration (required for transactions >$20)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# Optional: LangGraph API Key
LANGCHAIN_API_KEY=your_langchain_api_key

# Optional: Skyfire SDK Configuration
SKYFIRE_API_KEY=your_skyfire_api_key
```

### Setting up Telegram 2FA

1. Create a Telegram bot via [@BotFather](https://t.me/botfather)
2. Get your bot token
3. Start a chat with your bot
4. Get your chat ID using [@userinfobot](https://t.me/userinfobot)

## 🚀 Usage

### Running Locally

```bash
python -m core.orchestrator
```

### Running the optional SolanaAlpha strategy

`strategies/SolanaAlpha.py` is a standalone Freqtrade strategy and is not
loaded by the Sentinel orchestrator. Install Freqtrade using its supported
installation method, then copy the strategy into your Freqtrade user-data
directory:

```bash
pip install -r requirements-freqtrade.txt
cp strategies/SolanaAlpha.py /path/to/freqtrade/user_data/strategies/
freqtrade backtesting --strategy SolanaAlpha --timeframe 5m
```

Backtest and dry-run the strategy before enabling live trading. Its configured
hard stop is 10%, and it uses a trailing stop after reaching the configured
profit offset.

The same RSI/Bollinger entry and exit rules are integrated into the existing
`CryptoSniperAgent` as the `solana_alpha` score. The native agent calculates
its indicators from simulated close-price history, exposes the current signal
in each logged market snapshot, and remains paper-trading only. The logic is
symbol-agnostic and runs against whichever asset the orchestrator configures.

### Deploying to Railway.app

1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy - the Procfile will handle startup

The system will:
- Initialize wallet with ERC-4337 session keys
- Start risk manager with Telegram 2FA
- Launch three agents concurrently
- Run continuous arbitrage cycles every 60 seconds

## 🏗️ Architecture

### Core Components

#### Wallet (`core/wallet.py`)
- ERC-4337 session key management for non-custodial execution
- Automated transaction signing and sending
- Session key permissions and expiration handling
- Bulletproof retry logic with exponential backoff

#### Risk Manager (`core/risk.py`)
- Enforces $50 maximum transaction limit
- Requires Telegram 2FA for transactions over $20
- Rate limiting (max 10 transactions per hour)
- Transaction validation and approval workflow

#### Orchestrator (`core/orchestrator.py`)
- Asyncio-based concurrent agent execution
- Bulletproof error handling for all agents
- Automatic retry with exponential backoff
- Continuous monitoring and cleanup

### Agents

#### GPU Sniper Agent (`agents/gpu_sniper.py`)
- Monitors GPU rental markets (RunPod, VastAI, LambdaLabs)
- Detects VRAM pricing inefficiencies
- Executes arbitrage trades with 15%+ profit margin
- Bulletproof error handling in all API calls

#### RWA Flipper Agent (`agents/rwa_flipper.py`)
- Fetches property news from multiple sources
- Monitors tokenized real estate listings
- Matches news catalysts with undervalued properties
- Executes trades with 10%+ profit margin

#### Auditor Agent (`agents/auditor.py`)
- Tracks all system transactions
- Calculates net profit/loss metrics
- Monitors risk thresholds
- Generates comprehensive audit reports

## 🔒 Security Features

- **Non-custodial**: ERC-4337 session keys ensure you maintain custody
- **Transaction Limits**: Hard cap at $50 per transaction
- **2FA Authentication**: Telegram-based approval for large transactions
- **Rate Limiting**: Prevents excessive trading
- **Bulletproof Loops**: All loops have timeout and retry logic
- **Error Recovery**: Exponential backoff on failures

## 📊 Risk Management

The system implements multiple layers of risk control:

1. **Transaction Caps**: Maximum $50 per transaction
2. **2FA Threshold**: Transactions over $20 require manual approval
3. **Rate Limiting**: Maximum 10 transactions per hour
4. **Profit Margins**: Minimum 10-15% profit margin required
5. **Continuous Monitoring**: Auditor tracks all activity

## 🔄 How It Works

1. **Orchestrator** starts and registers all agents
2. Agents run **concurrently** every 60 seconds:
   - **GPU Sniper** scans for VRAM price gaps
   - **RWA Flipper** analyzes property news
   - **Auditor** tracks performance
3. Each agent finds opportunities and validates with **Risk Manager**
4. Transactions over $20 trigger **Telegram 2FA**
5. **Wallet** executes approved trades using **session keys**
6. **Auditor** reports cumulative profit/loss

## 🛠️ Development

### Running Tests

```bash
pytest
```

### Adding New Agents

1. Create a new agent in `agents/` directory
2. Implement `async def execute(self, wallet, risk_manager)` method
3. Register in `core/orchestrator.py`

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.

## ⚠️ Disclaimer

This software is for educational purposes. Use at your own risk. Always test with small amounts first.
