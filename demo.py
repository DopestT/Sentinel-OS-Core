#!/usr/bin/env python3
"""
Example usage of Sentinel OS Multi-Agent Arbitrage System.
Demonstrates all key features including session keys, risk management, and agents.
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def demo_session_keys():
    """Demonstrate ERC-4337 session key functionality."""
    print("\n" + "="*60)
    print("DEMO: ERC-4337 Session Keys")
    print("="*60)
    
    from core.wallet import Wallet
    
    # Create wallet
    wallet = Wallet()
    print(f"✓ Wallet created: {wallet.address}")
    
    # Create session key with limited permissions
    session_key = wallet.create_session_key(max_amount=10.0, duration_hours=24)
    print(f"✓ Session key created: {session_key.address}")
    print(f"  - Max amount: ${session_key.permissions['max_amount']}")
    print(f"  - Expires in: 24 hours")
    
    # Test permissions
    print(f"\n  Can execute $5 transaction: {session_key.can_execute(5.0)}")
    print(f"  Can execute $15 transaction: {session_key.can_execute(15.0)}")
    print(f"  Is expired: {session_key.is_expired()}")


async def demo_risk_management():
    """Demonstrate risk management and transaction limits."""
    print("\n" + "="*60)
    print("DEMO: Risk Management ($50 cap, 2FA for >$20)")
    print("="*60)
    
    from core.risk import RiskManager
    
    risk_manager = RiskManager()
    
    # Test various transaction amounts
    test_amounts = [15.0, 25.0, 35.0, 55.0]
    
    for amount in test_amounts:
        is_valid, reason = await risk_manager.validate_transaction(
            amount_usd=amount,
            description=f"Test transaction ${amount}"
        )
        
        status = "✓" if is_valid else "✗"
        print(f"{status} ${amount:.2f}: {reason}")
    
    # Get risk status
    status = await risk_manager.get_risk_status()
    print(f"\nRisk Status:")
    print(f"  - Max transaction limit: ${status['max_transaction_usd']}")
    print(f"  - 2FA threshold: ${status['2fa_threshold_usd']}")
    print(f"  - Transactions (last hour): {status['transactions_last_hour']}")
    print(f"  - Telegram enabled: {status['telegram_enabled']}")


async def demo_agents():
    """Demonstrate individual agent execution."""
    print("\n" + "="*60)
    print("DEMO: Individual Agents")
    print("="*60)
    
    from core.wallet import Wallet
    from core.risk import RiskManager
    from agents.gpu_sniper import GPUSniperAgent
    from agents.rwa_flipper import RWAFlipperAgent
    from agents.auditor import AuditorAgent
    
    wallet = Wallet()
    risk_manager = RiskManager()
    
    # GPU Sniper Agent
    print("\n1. GPU Sniper Agent (VRAM arbitrage)")
    gpu_agent = GPUSniperAgent()
    result = await gpu_agent.execute(wallet, risk_manager)
    print(f"   Opportunities found: {len(result.get('opportunities', []))}")
    print(f"   Trades executed: {result.get('successful_trades', 0)}")
    
    # RWA Flipper Agent
    print("\n2. RWA Flipper Agent (Property news arbitrage)")
    rwa_agent = RWAFlipperAgent()
    result = await rwa_agent.execute(wallet, risk_manager)
    print(f"   Opportunities found: {len(result.get('opportunities', []))}")
    print(f"   Trades executed: {result.get('successful_trades', 0)}")
    
    # Auditor Agent
    print("\n3. Auditor Agent (Net profit tracking)")
    auditor = AuditorAgent()
    result = await auditor.execute(wallet, risk_manager)
    if result.get('success'):
        report = result['report']
        print(f"   Wallet balance: {report['wallet']['balance_eth']:.4f} ETH")
        print(f"   Transactions analyzed: {report['transactions_analyzed']}")


async def demo_orchestrator():
    """Demonstrate orchestrator with concurrent agent execution."""
    print("\n" + "="*60)
    print("DEMO: Orchestrator (Concurrent Execution)")
    print("="*60)
    
    from core.orchestrator import Orchestrator
    from agents.gpu_sniper import GPUSniperAgent
    from agents.rwa_flipper import RWAFlipperAgent
    from agents.auditor import AuditorAgent
    
    # Create orchestrator
    orchestrator = Orchestrator()
    print(f"✓ Orchestrator initialized")
    print(f"  Wallet: {orchestrator.wallet.address}")
    
    # Register agents
    orchestrator.register_agent(GPUSniperAgent())
    orchestrator.register_agent(RWAFlipperAgent())
    orchestrator.register_agent(AuditorAgent())
    print(f"✓ Registered {len(orchestrator.agents)} agents")
    
    # Run one cycle
    print("\nRunning concurrent agent cycle...")
    results = await orchestrator.run_cycle()
    
    print(f"\nResults:")
    for result in results:
        status = "✓" if result.success else "✗"
        print(f"  {status} {result.agent_name}")
    
    # Get status
    status = await orchestrator.get_status()
    print(f"\nOrchestrator Status:")
    print(f"  - Total cycles: {status['total_cycles']}")
    print(f"  - Agents registered: {status['agents_registered']}")
    print(f"  - Running: {status['running']}")


async def main():
    """Run all demos."""
    print("\n" + "="*60)
    print("Sentinel OS Multi-Agent Arbitrage System - Demo")
    print("="*60)
    
    try:
        await demo_session_keys()
        await demo_risk_management()
        await demo_agents()
        await demo_orchestrator()
        
        print("\n" + "="*60)
        print("✓ All demos completed successfully!")
        print("="*60)
        
        print("\nNext steps:")
        print("  1. Configure .env file with your credentials")
        print("  2. Set up Telegram bot for 2FA (optional)")
        print("  3. Run 'python main.py' to start the system")
        print("  4. Deploy to Railway.app using the Procfile")
        
    except Exception as e:
        logger.error(f"Demo error: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
