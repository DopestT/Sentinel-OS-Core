"""
Auditor Agent - Tracks net profit and overall system performance.
Monitors all trades and calculates cumulative profit/loss.
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)


class AuditorAgent:
    """
    Agent that audits all system activity and tracks net profit.
    Provides performance metrics and risk analysis.
    """
    
    def __init__(self):
        """Initialize Auditor agent."""
        self.name = "AuditorAgent"
        self.trade_history: List[Dict[str, Any]] = []
        self.performance_metrics = {
            'total_profit_usd': 0.0,
            'total_loss_usd': 0.0,
            'net_profit_usd': 0.0,
            'total_trades': 0,
            'successful_trades': 0,
            'failed_trades': 0,
            'win_rate': 0.0
        }
        
        logger.info(f"{self.name} initialized")
    
    async def fetch_recent_transactions(self, wallet) -> List[Dict[str, Any]]:
        """
        Fetch recent transactions from wallet.
        
        Args:
            wallet: Wallet instance
            
        Returns:
            List of recent transactions
        """
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # In production, this would fetch actual blockchain transactions
                # For now, return mock data
                await asyncio.sleep(0.3)
                
                # Simulate fetching transaction history
                transactions = [
                    {
                        'hash': '0xabc123...',
                        'from': wallet.address,
                        'to': '0xdef456...',
                        'value_usd': 25.50,
                        'type': 'gpu_arbitrage',
                        'status': 'success',
                        'profit_usd': 3.82,
                        'timestamp': (datetime.now() - timedelta(hours=1)).isoformat()
                    },
                    {
                        'hash': '0xghi789...',
                        'from': wallet.address,
                        'to': '0xjkl012...',
                        'value_usd': 18.00,
                        'type': 'rwa_arbitrage',
                        'status': 'success',
                        'profit_usd': 1.80,
                        'timestamp': (datetime.now() - timedelta(hours=3)).isoformat()
                    },
                ]
                
                logger.info(f"Fetched {len(transactions)} recent transactions")
                return transactions
                
            except Exception as e:
                retry_count += 1
                logger.error(f"Error fetching transactions (attempt {retry_count}/{max_retries}): {e}")
                
                if retry_count >= max_retries:
                    logger.error("Max retries reached, returning empty list")
                    return []
                
                await asyncio.sleep(2 ** retry_count)
        
        return []
    
    async def analyze_performance(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze performance metrics from transactions.
        
        Args:
            transactions: List of transactions
            
        Returns:
            Performance analysis
        """
        try:
            # Calculate metrics
            total_profit = sum(t.get('profit_usd', 0) for t in transactions if t.get('status') == 'success' and t.get('profit_usd', 0) > 0)
            total_loss = abs(sum(t.get('profit_usd', 0) for t in transactions if t.get('status') == 'success' and t.get('profit_usd', 0) < 0))
            net_profit = total_profit - total_loss
            
            total_trades = len(transactions)
            successful = sum(1 for t in transactions if t.get('status') == 'success')
            failed = total_trades - successful
            win_rate = (successful / total_trades * 100) if total_trades > 0 else 0
            
            # Update cumulative metrics
            self.performance_metrics['total_profit_usd'] += total_profit
            self.performance_metrics['total_loss_usd'] += total_loss
            self.performance_metrics['net_profit_usd'] = (
                self.performance_metrics['total_profit_usd'] - 
                self.performance_metrics['total_loss_usd']
            )
            self.performance_metrics['total_trades'] += total_trades
            self.performance_metrics['successful_trades'] += successful
            self.performance_metrics['failed_trades'] += failed
            
            if self.performance_metrics['total_trades'] > 0:
                self.performance_metrics['win_rate'] = (
                    self.performance_metrics['successful_trades'] / 
                    self.performance_metrics['total_trades'] * 100
                )
            
            analysis = {
                'current_cycle': {
                    'total_profit_usd': total_profit,
                    'total_loss_usd': total_loss,
                    'net_profit_usd': net_profit,
                    'trades': total_trades,
                    'win_rate': win_rate
                },
                'cumulative': dict(self.performance_metrics),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Performance analysis: Net profit ${net_profit:.2f} ({total_trades} trades)")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing performance: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def check_risk_thresholds(self, risk_manager) -> Dict[str, Any]:
        """
        Check current risk levels against thresholds.
        
        Args:
            risk_manager: Risk manager instance
            
        Returns:
            Risk assessment
        """
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                risk_status = await risk_manager.get_risk_status()
                
                warnings = []
                
                # Check transaction volume
                if risk_status['volume_last_hour_usd'] > 40:
                    warnings.append({
                        'level': 'warning',
                        'message': f"High volume: ${risk_status['volume_last_hour_usd']:.2f} in last hour"
                    })
                
                # Check transaction rate
                if risk_status['transactions_last_hour'] >= 8:
                    warnings.append({
                        'level': 'warning',
                        'message': f"High frequency: {risk_status['transactions_last_hour']} transactions in last hour"
                    })
                
                # Check pending approvals
                if risk_status['pending_approvals'] > 2:
                    warnings.append({
                        'level': 'info',
                        'message': f"{risk_status['pending_approvals']} pending 2FA approvals"
                    })
                
                assessment = {
                    'status': 'healthy' if not warnings else 'warning',
                    'risk_status': risk_status,
                    'warnings': warnings,
                    'timestamp': datetime.now().isoformat()
                }
                
                if warnings:
                    logger.warning(f"Risk warnings detected: {len(warnings)}")
                else:
                    logger.info("Risk levels within normal parameters")
                
                return assessment
                
            except Exception as e:
                retry_count += 1
                logger.error(f"Error checking risk thresholds (attempt {retry_count}/{max_retries}): {e}")
                
                if retry_count >= max_retries:
                    return {
                        'status': 'error',
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    }
                
                await asyncio.sleep(2 ** retry_count)
        
        return {
            'status': 'error',
            'error': 'Max retries exceeded',
            'timestamp': datetime.now().isoformat()
        }
    
    async def generate_report(self, wallet, risk_manager) -> Dict[str, Any]:
        """
        Generate comprehensive audit report.
        
        Args:
            wallet: Wallet instance
            risk_manager: Risk manager instance
            
        Returns:
            Audit report
        """
        try:
            # Fetch data concurrently
            transactions, wallet_balance, risk_assessment = await asyncio.gather(
                self.fetch_recent_transactions(wallet),
                wallet.get_balance(),
                self.check_risk_thresholds(risk_manager),
                return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(transactions, Exception):
                transactions = []
            if isinstance(wallet_balance, Exception):
                wallet_balance = 0.0
            if isinstance(risk_assessment, Exception):
                risk_assessment = {'status': 'error', 'error': str(risk_assessment)}
            
            # Analyze performance
            performance = await self.analyze_performance(transactions)
            
            report = {
                'wallet': {
                    'address': wallet.address,
                    'balance_eth': wallet_balance,
                    'session_keys': len(wallet.session_keys)
                },
                'performance': performance,
                'risk_assessment': risk_assessment,
                'transactions_analyzed': len(transactions),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Audit report generated: {len(transactions)} transactions analyzed")
            return report
            
        except Exception as e:
            logger.error(f"Error generating audit report: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def execute(self, wallet, risk_manager) -> Dict[str, Any]:
        """
        Main execution method called by orchestrator.
        
        Args:
            wallet: Wallet instance
            risk_manager: Risk manager instance
            
        Returns:
            Audit results
        """
        logger.info(f"{self.name} starting execution")
        
        try:
            # Generate comprehensive audit report
            report = await self.generate_report(wallet, risk_manager)
            
            # Store in history
            self.trade_history.append(report)
            
            # Keep only last 100 reports
            if len(self.trade_history) > 100:
                self.trade_history = self.trade_history[-100:]
            
            logger.info(f"{self.name} completed: Report generated successfully")
            
            return {
                'success': True,
                'report': report
            }
            
        except Exception as e:
            logger.error(f"{self.name} execution error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
