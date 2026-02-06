#!/usr/bin/env python3
"""
Main entry point for Sentinel OS Multi-Agent Arbitrage System.
"""
import asyncio
import logging
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('sentinel.log')
    ]
)

logger = logging.getLogger(__name__)


async def main():
    """Main execution function."""
    logger.info("=" * 60)
    logger.info("Sentinel OS Multi-Agent Arbitrage System")
    logger.info("=" * 60)
    
    try:
        # Import core modules
        from core.orchestrator import Orchestrator
        from agents.gpu_sniper import GPUSniperAgent
        from agents.rwa_flipper import RWAFlipperAgent
        from agents.auditor import AuditorAgent
        
        # Create orchestrator
        orchestrator = Orchestrator()
        logger.info("Orchestrator created")
        
        # Register agents
        orchestrator.register_agent(GPUSniperAgent())
        orchestrator.register_agent(RWAFlipperAgent())
        orchestrator.register_agent(AuditorAgent())
        
        logger.info(f"Registered {len(orchestrator.agents)} agents")
        logger.info("Starting continuous execution...")
        
        # Run continuous loop
        await orchestrator.run_continuous(interval_seconds=60)
        
    except KeyboardInterrupt:
        logger.info("\nReceived keyboard interrupt - shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Sentinel OS shutdown complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nShutdown complete")
