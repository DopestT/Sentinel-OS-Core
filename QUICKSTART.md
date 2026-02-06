# Quick Start Guide

Get started with Sentinel OS Multi-Agent Arbitrage System in 5 minutes.

## Installation

```bash
# Clone repository
git clone https://github.com/DopestT/Sentinel-OS-Core.git
cd Sentinel-OS-Core

# Install dependencies
pip install -r requirements.txt
```

## Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` with your credentials:
```bash
# Required
WALLET_PRIVATE_KEY=your_private_key
RPC_URL=https://eth-mainnet.g.alchemy.com/v2/your_key

# Optional (for Telegram 2FA)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

## Run

### Demo Mode
Run the demo to see all features:
```bash
python demo.py
```

### Production Mode
Start the full system:
```bash
python main.py
```

### Using Orchestrator Directly
```bash
python -m core.orchestrator
```

## What Happens

1. **Orchestrator** starts with 3 agents
2. Every 60 seconds, agents run concurrently:
   - **GPU Sniper** finds VRAM arbitrage (15%+ margin)
   - **RWA Flipper** finds property arbitrage (10%+ margin)
   - **Auditor** tracks net profit
3. Risk manager validates all transactions:
   - Max $50 per transaction
   - 2FA required for >$20
   - Rate limit: 10 tx/hour

## Quick Test

```bash
# Run tests
pytest test_system.py -v

# Should see:
# ✓ 9 tests passed
```

## Expected Output

```
Orchestrator initialized
✓ Registered 3 agents
Starting agent cycle with 3 agents

GPUSniperAgent starting execution
  Found VRAM gap opportunity: RTX 4090 21.2% margin
  Executing GPU arbitrage trade for $3.38
  ✓ GPUSniperAgent completed: 2/2 trades successful

RWAFlipperAgent starting execution
  Found RWA opportunity: Miami Beach Condo #42 20.2% margin
  ⚠ Trade rejected by risk manager: Transaction requires 2FA
  ✓ RWAFlipperAgent completed: 0/2 trades successful

AuditorAgent starting execution
  Performance analysis: Net profit $5.62 (2 trades)
  ✓ AuditorAgent completed: Report generated

Cycle complete: 3 succeeded, 0 failed
Waiting 60s before next cycle...
```

## Telegram 2FA Setup

For transactions over $20, set up Telegram 2FA:

1. Create bot with [@BotFather](https://t.me/botfather)
2. Get your chat ID from [@userinfobot](https://t.me/userinfobot)
3. Add to `.env`:
   ```
   TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
   TELEGRAM_CHAT_ID=123456789
   ```
4. When a transaction >$20 occurs, you'll receive:
   ```
   🔐 Transaction Approval Required
   Amount: $25.00
   Approval Code: 123456
   ```

## Deploy to Railway.app

1. Push to GitHub
2. Connect repository to Railway
3. Add environment variables in Railway dashboard
4. Deploy automatically with Procfile

See [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) for details.

## Troubleshooting

### "No WALLET_PRIVATE_KEY found"
- Add to `.env` file
- Or let it generate a test wallet automatically

### "Telegram 2FA disabled"
- Normal if TELEGRAM_BOT_TOKEN not set
- System works without it, just no 2FA

### "Transaction requires 2FA approval"
- Set up Telegram bot
- Or reduce transaction amounts to <$20

### "Rate limit exceeded"
- Wait 1 hour
- Max 10 transactions per hour

## Security

⚠️ **Important:**
- Never commit `.env` to Git
- Start with test amounts (<$10)
- Use a dedicated wallet, not your main one
- Enable Telegram 2FA for production

## Next Steps

- Read [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- See [README.md](README.md) for full documentation
- Check [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) for deployment

## Support

- **Issues:** [GitHub Issues](https://github.com/DopestT/Sentinel-OS-Core/issues)
- **Documentation:** See README.md
- **Examples:** Run `python demo.py`
