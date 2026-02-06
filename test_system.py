"""
Basic tests for Sentinel OS Multi-Agent Arbitrage System.
"""
import pytest
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.mark.asyncio
async def test_wallet_initialization():
    """Test wallet initialization."""
    from core.wallet import Wallet
    
    wallet = Wallet()
    assert wallet.address is not None
    assert wallet.private_key is not None
    assert len(wallet.session_keys) == 0


@pytest.mark.asyncio
async def test_session_key_creation():
    """Test session key creation."""
    from core.wallet import Wallet
    
    wallet = Wallet()
    session_key = wallet.create_session_key(max_amount=10.0, duration_hours=1)
    
    assert session_key is not None
    assert session_key.address is not None
    assert session_key.can_execute(5.0)
    assert not session_key.can_execute(15.0)
    assert not session_key.is_expired()


@pytest.mark.asyncio
async def test_risk_manager_validation():
    """Test risk manager transaction validation."""
    from core.risk import RiskManager
    
    risk_manager = RiskManager()
    
    # Test valid transaction under limit
    is_valid, reason = await risk_manager.validate_transaction(25.0, "Test transaction")
    assert is_valid
    
    # Test invalid transaction over limit
    is_valid, reason = await risk_manager.validate_transaction(60.0, "Too large")
    assert not is_valid
    assert "$50" in reason


@pytest.mark.asyncio
async def test_orchestrator_initialization():
    """Test orchestrator initialization."""
    from core.orchestrator import Orchestrator
    
    orchestrator = Orchestrator()
    assert orchestrator.wallet is not None
    assert orchestrator.risk_manager is not None
    assert len(orchestrator.agents) == 0
    assert not orchestrator.running


@pytest.mark.asyncio
async def test_agent_registration():
    """Test agent registration with orchestrator."""
    from core.orchestrator import Orchestrator
    from agents.gpu_sniper import GPUSniperAgent
    from agents.rwa_flipper import RWAFlipperAgent
    from agents.auditor import AuditorAgent
    
    orchestrator = Orchestrator()
    
    orchestrator.register_agent(GPUSniperAgent())
    orchestrator.register_agent(RWAFlipperAgent())
    orchestrator.register_agent(AuditorAgent())
    
    assert len(orchestrator.agents) == 3


@pytest.mark.asyncio
async def test_gpu_sniper_agent():
    """Test GPU Sniper agent execution."""
    from core.wallet import Wallet
    from core.risk import RiskManager
    from agents.gpu_sniper import GPUSniperAgent
    
    wallet = Wallet()
    risk_manager = RiskManager()
    agent = GPUSniperAgent()
    
    result = await agent.execute(wallet, risk_manager)
    
    assert result is not None
    assert 'success' in result


@pytest.mark.asyncio
async def test_rwa_flipper_agent():
    """Test RWA Flipper agent execution."""
    from core.wallet import Wallet
    from core.risk import RiskManager
    from agents.rwa_flipper import RWAFlipperAgent
    
    wallet = Wallet()
    risk_manager = RiskManager()
    agent = RWAFlipperAgent()
    
    result = await agent.execute(wallet, risk_manager)
    
    assert result is not None
    assert 'success' in result


@pytest.mark.asyncio
async def test_auditor_agent():
    """Test Auditor agent execution."""
    from core.wallet import Wallet
    from core.risk import RiskManager
    from agents.auditor import AuditorAgent
    
    wallet = Wallet()
    risk_manager = RiskManager()
    agent = AuditorAgent()
    
    result = await agent.execute(wallet, risk_manager)
    
    assert result is not None
    assert 'success' in result
    assert 'report' in result


@pytest.mark.asyncio
async def test_concurrent_agent_execution():
    """Test concurrent execution of multiple agents."""
    from core.orchestrator import Orchestrator
    from agents.gpu_sniper import GPUSniperAgent
    from agents.rwa_flipper import RWAFlipperAgent
    from agents.auditor import AuditorAgent
    
    orchestrator = Orchestrator()
    orchestrator.register_agent(GPUSniperAgent())
    orchestrator.register_agent(RWAFlipperAgent())
    orchestrator.register_agent(AuditorAgent())
    
    results = await orchestrator.run_cycle()
    
    assert len(results) == 3
    assert all(hasattr(r, 'agent_name') for r in results)
    assert all(hasattr(r, 'success') for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
