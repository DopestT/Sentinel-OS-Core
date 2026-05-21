import asyncio
from dotenv import load_dotenv

from core.risk import RiskManager
from agents.gpu_sniper import GPUSniperAgent
from agents.gas_monitor import GasSentinel

# Load .env secrets before initializing agents
load_dotenv()


class SentinelOrchestrator:
    def __init__(self):
        # Global safety net. Keep limits inside RiskManager for now.
        self.risk_manager = RiskManager()
        self.sniper = GPUSniperAgent()
        self.gas_watcher = GasSentinel()

    async def sniper_loop(self):
        """Run the GPU sniper continuously without crashing the whole bot."""
        print("🎯 GPU Sniper: Starting opportunity scan loop...")
        while True:
            try:
                result = await self.sniper.execute(wallet=None, risk_manager=self.risk_manager)
                print(f"🎯 GPU Sniper result: {result}")
            except Exception as e:
                print(f"GPU Sniper Error: {e}")

            await asyncio.sleep(60)

    async def start(self):
        print("--- 🎻 Sentinel-OS: Symphony Started ---")
        print("💰 Safety: RiskManager transaction caps enabled")
        print("📡 Network: Base monitoring enabled | GPU sniper loop enabled")
        print("-----------------------------------------")

        try:
            await asyncio.gather(
                self.sniper_loop(),
                self.gas_watcher.run(),
            )
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested. Closing loops safely...")
        except Exception as e:
            print(f"❌ CRITICAL CLUSTER ERROR: {e}")


if __name__ == "__main__":
    orchestrator = SentinelOrchestrator()
    asyncio.run(orchestrator.start())
