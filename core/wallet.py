import os
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from skyfire_sdk import SkyfireClient

class SolanaWallet:
    def __init__(self):
        self.rpc_url = os.getenv("SOLANA_RPC_URL")
        self.client = AsyncClient(self.rpc_url)
        # Load your identity for the $10 budget
        self.keypair = Keypair.from_base58_string(os.getenv("SOLANA_PRIVATE_KEY"))
        # Skyfire handles the KYA (Know Your Agent) on Solana
        self.skyfire = SkyfireClient(api_key=os.getenv("SKYFIRE_API_KEY"))

    async def get_balance(self):
        # Fetch SOL balance for gas (pennies) and USDC for trades
        resp = await self.client.get_balance(self.keypair.pubkey())
        return resp.value / 10**9 # Convert lamports to SOL

    async def pay_agent(self, recipient_pubkey, amount_usdc):
        """Executes a high-speed Solana payment via Skyfire SDK."""
        print(f"💸 Sending {amount_usdc} USDC on Solana...")
        # Skyfire automates the complex Solana token instructions
        tx = self.skyfire.pay(
            amount=amount_usdc,
            recipient=recipient_pubkey,
            chain="solana"
        )
        return tx
