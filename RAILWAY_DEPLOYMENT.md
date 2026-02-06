# Railway.app Deployment Guide

This guide walks you through deploying Sentinel OS to Railway.app.

## Prerequisites

- A Railway.app account (free tier available)
- GitHub repository connected to Railway
- Telegram bot token and chat ID (for 2FA)
- Ethereum wallet private key

## Steps

### 1. Connect GitHub Repository

1. Go to [Railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Authorize Railway to access your repository
5. Select `DopestT/Sentinel-OS-Core`

### 2. Configure Environment Variables

In the Railway dashboard, add the following environment variables:

**Required:**
```
WALLET_PRIVATE_KEY=<your_ethereum_private_key>
RPC_URL=https://eth-mainnet.g.alchemy.com/v2/<your_alchemy_key>
```

**Optional (for Telegram 2FA):**
```
TELEGRAM_BOT_TOKEN=<your_bot_token>
TELEGRAM_CHAT_ID=<your_chat_id>
```

**Optional (for LangGraph):**
```
LANGCHAIN_API_KEY=<your_langchain_key>
```

### 3. Deploy

Railway will automatically:
1. Detect the `Procfile`
2. Install dependencies from `requirements.txt`
3. Start the application with `python -m core.orchestrator`

### 4. Monitor Logs

View logs in the Railway dashboard to monitor:
- Agent execution cycles
- Arbitrage opportunities found
- Transaction approvals
- Risk management alerts

## Environment Variable Details

### WALLET_PRIVATE_KEY
Your Ethereum wallet private key (without 0x prefix). This wallet will be used for all transactions.

**Security:** Keep this secret! Never commit it to Git.

### RPC_URL
Ethereum RPC endpoint. Recommended providers:
- Alchemy: `https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY`
- Infura: `https://mainnet.infura.io/v3/YOUR_KEY`
- QuickNode: Your custom endpoint

### TELEGRAM_BOT_TOKEN
Create a bot via [@BotFather](https://t.me/botfather) on Telegram:
1. Start chat with @BotFather
2. Send `/newbot`
3. Follow instructions
4. Copy the token

### TELEGRAM_CHAT_ID
Your Telegram user ID:
1. Start chat with your bot
2. Message [@userinfobot](https://t.me/userinfobot)
3. Copy your user ID

## Scaling

Railway auto-scales based on traffic. For this application:
- **CPU**: 1 vCPU is sufficient for 3 agents
- **Memory**: 512MB recommended
- **Cost**: ~$5-10/month on Hobby plan

## Monitoring

Check these logs for system health:
```
✓ Orchestrator initialized
✓ Registered 3 agents
✓ Starting agent cycle with 3 agents
✓ Agent GPUSniperAgent completed successfully
✓ Cycle complete: 3 succeeded, 0 failed
```

## Troubleshooting

### "ModuleNotFoundError"
- Ensure `requirements.txt` is in the repository root
- Check Railway build logs for pip installation errors

### "No WALLET_PRIVATE_KEY found"
- Add environment variable in Railway dashboard
- Restart the deployment

### "Telegram 2FA disabled"
- This is normal if Telegram credentials aren't set
- System will still work but won't have 2FA

### "Transaction rejected by risk manager"
- Check transaction amount (must be ≤$50)
- For amounts >$20, approve via Telegram
- Check rate limits (max 10 tx/hour)

## Security Best Practices

1. **Never commit secrets** - Use Railway environment variables
2. **Use a dedicated wallet** - Don't use your main wallet
3. **Start with small amounts** - Test with minimal funds first
4. **Enable 2FA** - Set up Telegram bot for transactions >$20
5. **Monitor regularly** - Check logs daily for anomalies

## Updates

To update the deployment:
1. Push changes to GitHub
2. Railway auto-deploys on push to main branch
3. Monitor logs to ensure successful deployment

## Support

For issues:
- Check Railway logs for errors
- Review GitHub issues
- Verify environment variables
