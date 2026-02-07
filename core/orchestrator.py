import asyncio
import os
import sys
from dotenv import load_dotenv

# Import your specialized agents
from core.risk import RiskManager
from agents.gpu_sniper import GPUSniper
from agents.gas_monitor import GasSentinel

# Load your .env secrets from Coinbase/Skyfire/Telegram
load_dotenv()

class SentinelOrchestrator:
    def __init__(self):
        # Initialize the global safety net with your $2.00/day limit
        self.risk_manager = RiskManager(daily_limit=2.0)
        
        # Initialize the worker agents
        self.sniper = GPUSniper(self.risk_manager)
        self.gas_watcher = GasSentinel()

    async def start(self):
        print("--- 🎻 Sentinel-OS: Symphony Started ---")
        print(f"💰 Budget Gauge: $10.00 | Safety Cap: $2.00/day")
        print("📡 Network: Base (Layer 2) | Payment: Skyfire SDK")
        print("-----------------------------------------")

        try:
            # This is the 'Conductor' - it runs all loops in parallel
            await asyncio.gather(
                self.sniper.run_forever(),    # Loop 1: Hunting VRAM gaps
                self.gas_watcher.run(),       # Loop 2: Monitoring Base fees
            )
        except KeyboardInterrupt:
            print("\n🛑 Conductor signaled shutdown. Closing loops safely...")
        except Exception as e:
            print(f"❌ CRITICAL CLUSTER ERROR: {e}")
            # In 2026, an unhandled error triggers an emergency Telegram ping
            self.risk_manager.alert(f"Cluster Crash: {e}")

if __name__ == "__main__":
    orchestrator = SentinelOrchestrator()
    asyncio.run(orchestrator.start())
