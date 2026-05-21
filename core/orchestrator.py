import asyncio
from dotenv import load_dotenv

from core.risk import RiskManager
from agents.crypto_sniper import CryptoSniperAgent
from agents.gas_monitor import GasSentinel

load_dotenv()


class SentinelOrchestrator:
    def __init__(self):
        self.risk_manager = RiskManager()
        self.crypto_sniper = CryptoSniperAgent(symbol="LUNC")
        self.gas_watcher = GasSentinel()

    async def crypto_loop(self):
        print("🧠 Crypto Sniper: Multi-signal LUNC watcher online...")

        while True:
            try:
                result = await self.crypto_sniper.execute()

                snapshot = result["snapshot"]
                decision = result["decision"]

                print("-----------------------------------------")
                print(f"📈 {snapshot['symbol']} | Price: {snapshot['price']:.8f}")
                print(f"🧠 Best Strategy: {result['best_strategy_now']}")
                print(f"🎯 Strategy Score: {result['best_strategy_score']}")
                print(f"⚡ Decision: {decision['decision']}")
                print(f"📄 Paper Trades Logged: {result['paper_trade_count']}")
                print("-----------------------------------------")

            except Exception as e:
                print(f"Crypto Sniper Error: {e}")

            await asyncio.sleep(60)

    async def start(self):
        print("--- 🎻 Sentinel-OS: Crypto Intelligence Online ---")
        print("💰 Paper trading mode only")
        print("🧠 Multi-signal strategy scoring enabled")
        print("📡 LUNC monitoring + Base gas monitoring active")
        print("------------------------------------------------")

        try:
            await asyncio.gather(
                self.crypto_loop(),
                self.gas_watcher.run(),
            )
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested. Closing loops safely...")
        except Exception as e:
            print(f"❌ CRITICAL CLUSTER ERROR: {e}")


if __name__ == "__main__":
    orchestrator = SentinelOrchestrator()
    asyncio.run(orchestrator.start())
