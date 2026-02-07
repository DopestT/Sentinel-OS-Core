import os
from skyfire_sdk import SkyfireClient

class ProfitLock:
    def __init__(self, bot, user_id):
        self.skyfire = SkyfireClient(api_key=os.getenv("SKYFIRE_API_KEY"))
        self.bot = bot
        self.user_id = user_id
        self.initial_capital = 10.0  # Your starting $10
        self.vault_address = "YourPrimaryCoinbaseAddress" # Your 'Safe' spot

    async def secure_gains(self):
        """Sweeps everything above $10 to your vault."""
        current_balance = self.skyfire.get_balance()
        
        if current_balance > self.initial_capital:
            profit = current_balance - self.initial_capital
            print(f"💰 Profit Lock: Moving ${profit:.2f} to Vault...")
            
            # Transfer via Skyfire to your secure Coinbase address
            self.skyfire.withdraw(amount=profit, recipient=self.vault_address, chain="solana")
            self.bot.send_message(self.user_id, f"🔒 *Profit Locked:* ${profit:.2f} sent to Vault.")

    async def run(self):
        while True:
            await self.secure_gains()
            await asyncio.sleep(43200) # Check twice a day
