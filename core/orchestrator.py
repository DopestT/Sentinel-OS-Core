"""
Orchestrator for managing multi-agent execution with LangGraph.
Uses asyncio for concurrent agent execution with bulletproof error handling.
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import traceback

from core.wallet import Wallet
from core.risk import RiskManager

logger = logging.getLogger(__name__)


class AgentResult:
    """Container for agent execution results."""
    
    def __init__(self, agent_name: str, success: bool, 
                 data: Optional[Dict[str, Any]] = None, 
                 error: Optional[str] = None):
        self.agent_name = agent_name
        self.success = success
        self.data = data or {}
        self.error = error
        self.timestamp = datetime.now()


class Orchestrator:
    """Orchestrates multi-agent arbitrage system with concurrent execution."""
    
    def __init__(self):
        """Initialize orchestrator with wallet and risk manager."""
        self.wallet = Wallet()
        self.risk_manager = RiskManager()
        self.agents = []
        self.running = False
        self.results_history = []
        
        logger.info("Orchestrator initialized")
    
    def register_agent(self, agent):
        """
        Register an agent with the orchestrator.
        
        Args:
            agent: Agent instance with async execute() method
        """
        self.agents.append(agent)
        logger.info(f"Registered agent: {agent.__class__.__name__}")
    
    async def run_agent_safe(self, agent) -> AgentResult:
        """
        Run a single agent with bulletproof error handling.
        
        Args:
            agent: Agent instance to run
            
        Returns:
            AgentResult with execution outcome
        """
        agent_name = agent.__class__.__name__
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                logger.info(f"Starting agent: {agent_name} (attempt {retry_count + 1}/{max_retries})")
                
                # Execute agent with timeout
                result = await asyncio.wait_for(
                    agent.execute(self.wallet, self.risk_manager),
                    timeout=300  # 5 minute timeout per agent
                )
                
                logger.info(f"Agent {agent_name} completed successfully")
                return AgentResult(
                    agent_name=agent_name,
                    success=True,
                    data=result
                )
                
            except asyncio.TimeoutError:
                retry_count += 1
                error_msg = f"Agent {agent_name} timed out"
                logger.error(error_msg)
                
                if retry_count >= max_retries:
                    return AgentResult(
                        agent_name=agent_name,
                        success=False,
                        error=error_msg
                    )
                
                # Exponential backoff
                await asyncio.sleep(2 ** retry_count)
                
            except Exception as e:
                retry_count += 1
                error_msg = f"Agent {agent_name} error: {str(e)}"
                logger.error(f"{error_msg}\n{traceback.format_exc()}")
                
                if retry_count >= max_retries:
                    return AgentResult(
                        agent_name=agent_name,
                        success=False,
                        error=error_msg
                    )
                
                # Exponential backoff
                await asyncio.sleep(2 ** retry_count)
        
        # Should not reach here, but return failure just in case
        return AgentResult(
            agent_name=agent_name,
            success=False,
            error="Maximum retries exceeded"
        )
    
    async def run_cycle(self) -> List[AgentResult]:
        """
        Run one cycle of all agents concurrently.
        
        Returns:
            List of AgentResult objects
        """
        if not self.agents:
            logger.warning("No agents registered")
            return []
        
        logger.info(f"Starting agent cycle with {len(self.agents)} agents")
        
        # Run all agents concurrently with bulletproof error handling
        tasks = []
        for agent in self.agents:
            task = asyncio.create_task(self.run_agent_safe(agent))
            tasks.append(task)
        
        # Wait for all agents to complete
        results = await asyncio.gather(*tasks, return_exceptions=False)
        
        # Store results
        self.results_history.extend(results)
        
        # Log summary
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        logger.info(f"Cycle complete: {successful} succeeded, {failed} failed")
        
        return results
    
    async def run_continuous(self, interval_seconds: int = 60):
        """
        Run agents continuously in a loop with bulletproof error handling.
        
        Args:
            interval_seconds: Time to wait between cycles
        """
        self.running = True
        cycle_count = 0
        consecutive_failures = 0
        
        logger.info(f"Starting continuous execution (interval: {interval_seconds}s)")
        
        while self.running:
            try:
                cycle_count += 1
                logger.info(f"=== Cycle {cycle_count} ===")
                
                # Run agent cycle
                results = await self.run_cycle()
                
                # Check if all agents failed
                if results and all(not r.success for r in results):
                    consecutive_failures += 1
                    logger.warning(f"All agents failed (consecutive failures: {consecutive_failures})")
                    
                    # If too many consecutive failures, increase wait time
                    if consecutive_failures >= 3:
                        wait_time = min(interval_seconds * 2, 300)  # Max 5 minutes
                        logger.warning(f"Multiple failures detected, waiting {wait_time}s before retry")
                        await asyncio.sleep(wait_time)
                        continue
                else:
                    consecutive_failures = 0
                
                # Cleanup expired session keys and approvals
                self.wallet.cleanup_expired_keys()
                self.risk_manager.cleanup_expired_approvals()
                
                # Wait before next cycle
                logger.info(f"Waiting {interval_seconds}s before next cycle...")
                await asyncio.sleep(interval_seconds)
                
            except asyncio.CancelledError:
                logger.info("Orchestrator cancelled")
                self.running = False
                break
                
            except Exception as e:
                logger.error(f"Unexpected error in orchestrator loop: {e}\n{traceback.format_exc()}")
                consecutive_failures += 1
                
                # Wait before retry with exponential backoff
                wait_time = min(interval_seconds * (2 ** min(consecutive_failures, 5)), 300)
                logger.info(f"Waiting {wait_time}s before retry...")
                await asyncio.sleep(wait_time)
        
        logger.info("Orchestrator stopped")
    
    def stop(self):
        """Stop the orchestrator."""
        logger.info("Stopping orchestrator...")
        self.running = False
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current orchestrator status."""
        # Get recent results (last 10)
        recent_results = self.results_history[-10:] if self.results_history else []
        
        return {
            'running': self.running,
            'agents_registered': len(self.agents),
            'total_cycles': len(self.results_history) // max(len(self.agents), 1),
            'wallet_address': self.wallet.address,
            'recent_results': [
                {
                    'agent': r.agent_name,
                    'success': r.success,
                    'timestamp': r.timestamp.isoformat(),
                    'error': r.error
                }
                for r in recent_results
            ],
            'risk_status': await self.risk_manager.get_risk_status()
        }


async def main():
    """Main entry point for orchestrator."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Import agents
    try:
        from agents.gpu_sniper import GPUSniperAgent
        from agents.rwa_flipper import RWAFlipperAgent
        from agents.auditor import AuditorAgent
    except ImportError as e:
        logger.error(f"Failed to import agents: {e}")
        return
    
    # Create orchestrator
    orchestrator = Orchestrator()
    
    # Register agents
    orchestrator.register_agent(GPUSniperAgent())
    orchestrator.register_agent(RWAFlipperAgent())
    orchestrator.register_agent(AuditorAgent())
    
    # Run continuous loop
    try:
        await orchestrator.run_continuous(interval_seconds=60)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
        orchestrator.stop()


if __name__ == "__main__":
    asyncio.run(main())
