import os
import asyncio
import telebot
from web3 import Web3

class GasSentinel:
    def __init__(self):
        # Base Network RPC (Coinbase's Layer 2)
        self.w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))
        self.bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN"))
        self.user_id = os.getenv("MY_USER_ID")
        self.max_gwei = 0.05  # Our "Red Alert" threshold for Base

    async def run(self):
        print("⛽ Gas Sentinel: Monitoring Base Network traffic...")
        while True:
            try:
                # Get current gas price in Gwei
                gas_price_wei = self.w3.eth.gas_price
                gas_price_gwei = self.w3.from_wei(gas_price_wei, 'gwei')

                if gas_price_gwei > self.max_gwei:
                    self.bot.send_message(
                        self.user_id, 
                        f"⚠️ GAS ALERT: Base fees are high ({gas_price_gwei:.4f} Gwei). Consider pausing the Sniper."
                    )
                
            except Exception as e:
                print(f"Gas Monitor Error: {e}")
            
            await asyncio.sleep(300) # Check every 5 minutes
