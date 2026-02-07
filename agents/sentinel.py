import os, asyncio, telebot
from skyfire_sdk import SkyfireClient
from solana.rpc.async_api import AsyncClient
from telebot import types # Added for keyboard types

# --- 1. CONFIGURATION ---
API_KEY = "7153803e-6d47-4adb-b496-193abb75e731"
TELE_TOKEN = "8270273234:AAHU5aDnkOdNQvCuq2JZg1S3e2fv2Aa8jYg"
MY_ID = "7238309847"
WALLET = "8cVkzCeMpn7Lg67yr5GgRQWpSJvbXTRBoaLvQtYoCL9m"

# --- 2. THE ENGINE ---
class Sentinel:
    def __init__(self):
        self.skyfire = SkyfireClient(api_key=API_KEY)
        self.bot = telebot.TeleBot(TELE_TOKEN)
        self.sol_client = AsyncClient("https://api.mainnet-beta.solana.com")
        self.gas_threshold = 0.02
        
        # Register the /start command handler here
        self.setup_handlers()

    def setup_handlers(self):
        """Forces the menu to appear when you type /start on iPhone."""
        @self.bot.message_handler(commands=['start', 'menu'])
        def send_welcome(message):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
            markup.row(types.KeyboardButton("💰 Check Balance"), types.KeyboardButton("🛰️ Status"))
            markup.row(types.KeyboardButton("🔒 Lock Profits"), types.KeyboardButton("⛽ Refuel Gas"))
            
            self.bot.send_message(
                message.chat.id, 
                "🎮 *Sentinel Dashboard Active*\nTap a button below to control your $10 cluster.", 
                reply_markup=markup,
                parse_mode="Markdown"
            )

        @self.bot.message_handler(func=lambda message: True)
        def handle_buttons(message):
            """Handles the button taps."""
            if message.text == "💰 Check Balance":
                balance = self.skyfire.get_balance()
                self.bot.reply_to(message, f"💰 *Current Balance:* ${balance:.2f} USDC")
            elif message.text == "🛰️ Status":
                self.bot.reply_to(message, "✅ Sentinel Engine: Online\n📡 Network: Solana")

    async def run_bot(self):
        """Starts the Telegram listener."""
        print("📡 Telegram Bot: Listening for commands...")
        self.bot.infinity_polling()

    async def run_sniper(self):
        """Main loop hunting for deals."""
        while True:
            print("Targeting VRAM gaps on Solana...")
            await asyncio.sleep(600) 

    async def start(self):
        # Notify you that the script is running
        self.bot.send_message(MY_ID, "🚀 Sentinel OS: System Initialized. Type /start to see the menu.")
        # Run everything together
        await asyncio.gather(self.run_sniper(), self.run_bot())

if __name__ == "__main__":
    asyncio.run(Sentinel().start())
