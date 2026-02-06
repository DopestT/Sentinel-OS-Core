"""
Risk management module with transaction limits and Telegram 2FA.
Enforces $50 cap and requires 2FA for transactions over $20.
"""
import os
import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import hashlib
import random

logger = logging.getLogger(__name__)

# Try to import telegram, but make it optional
try:
    from telegram import Bot
    from telegram.error import TelegramError
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    logger.warning("python-telegram-bot not installed. Telegram 2FA will be disabled.")


class RiskManager:
    """Risk management with transaction limits and Telegram 2FA."""
    
    # Transaction limits
    MAX_TRANSACTION_USD = 50.0  # Maximum transaction in USD
    TWO_FA_THRESHOLD_USD = 20.0  # Require 2FA above this amount
    
    def __init__(self):
        """Initialize risk manager."""
        self.telegram_bot: Optional[Bot] = None
        self.telegram_chat_id: Optional[str] = None
        self.pending_approvals: Dict[str, Dict[str, Any]] = {}
        self.approved_transactions: set = set()
        
        # Initialize Telegram bot if credentials available
        self._init_telegram()
        
        # Track transaction history for rate limiting
        self.transaction_history = []
        
    def _init_telegram(self):
        """Initialize Telegram bot for 2FA."""
        if not TELEGRAM_AVAILABLE:
            logger.warning("Telegram bot unavailable - 2FA disabled")
            return
            
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        if bot_token and chat_id:
            try:
                self.telegram_bot = Bot(token=bot_token)
                self.telegram_chat_id = chat_id
                logger.info("Telegram 2FA initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Telegram bot: {e}")
        else:
            logger.warning("TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set - 2FA disabled")
    
    async def validate_transaction(self, amount_usd: float, 
                                   description: str = "") -> tuple[bool, str]:
        """
        Validate a transaction against risk limits.
        
        Args:
            amount_usd: Transaction amount in USD
            description: Transaction description
            
        Returns:
            Tuple of (is_valid, reason)
        """
        # Check maximum transaction limit
        if amount_usd > self.MAX_TRANSACTION_USD:
            reason = f"Transaction ${amount_usd:.2f} exceeds maximum limit of ${self.MAX_TRANSACTION_USD:.2f}"
            logger.warning(reason)
            return False, reason
        
        # Check if amount is reasonable
        if amount_usd <= 0:
            reason = "Transaction amount must be positive"
            logger.warning(reason)
            return False, reason
        
        # Check 2FA requirement
        if amount_usd > self.TWO_FA_THRESHOLD_USD:
            if not await self._requires_2fa_approval(amount_usd, description):
                reason = f"Transaction ${amount_usd:.2f} requires 2FA approval"
                logger.warning(reason)
                return False, reason
        
        # Check rate limiting (max 10 transactions per hour)
        if not self._check_rate_limit():
            reason = "Rate limit exceeded - too many transactions"
            logger.warning(reason)
            return False, reason
        
        # All checks passed
        self._record_transaction(amount_usd)
        return True, "Transaction approved"
    
    async def request_2fa_approval(self, amount_usd: float, 
                                   description: str = "") -> str:
        """
        Request 2FA approval via Telegram.
        
        Args:
            amount_usd: Transaction amount in USD
            description: Transaction description
            
        Returns:
            Approval code to be confirmed
        """
        # Generate approval code
        code = self._generate_approval_code()
        
        # Store pending approval
        tx_id = hashlib.sha256(f"{amount_usd}{description}{datetime.now().timestamp()}".encode()).hexdigest()[:16]
        self.pending_approvals[code] = {
            'tx_id': tx_id,
            'amount_usd': amount_usd,
            'description': description,
            'timestamp': datetime.now(),
            'expires': datetime.now() + timedelta(minutes=5)
        }
        
        # Send Telegram message
        if self.telegram_bot and self.telegram_chat_id:
            try:
                message = (
                    f"🔐 Transaction Approval Required\n\n"
                    f"Amount: ${amount_usd:.2f}\n"
                    f"Description: {description}\n"
                    f"TX ID: {tx_id}\n\n"
                    f"Approval Code: {code}\n"
                    f"Expires in 5 minutes"
                )
                await self.telegram_bot.send_message(
                    chat_id=self.telegram_chat_id,
                    text=message
                )
                logger.info(f"2FA request sent via Telegram for ${amount_usd:.2f}")
            except Exception as e:
                logger.error(f"Failed to send Telegram message: {e}")
        else:
            logger.warning(f"2FA code generated but Telegram not configured: {code}")
        
        return code
    
    async def approve_transaction(self, code: str) -> bool:
        """
        Approve a transaction with 2FA code.
        
        Args:
            code: Approval code from Telegram
            
        Returns:
            True if approved, False otherwise
        """
        if code not in self.pending_approvals:
            logger.warning(f"Invalid approval code: {code}")
            return False
        
        approval = self.pending_approvals[code]
        
        # Check expiration
        if datetime.now() > approval['expires']:
            logger.warning(f"Approval code expired: {code}")
            del self.pending_approvals[code]
            return False
        
        # Mark as approved
        self.approved_transactions.add(approval['tx_id'])
        del self.pending_approvals[code]
        
        logger.info(f"Transaction approved: {approval['tx_id']} for ${approval['amount_usd']:.2f}")
        return True
    
    async def _requires_2fa_approval(self, amount_usd: float, description: str) -> bool:
        """Check if transaction already has 2FA approval."""
        tx_id = hashlib.sha256(f"{amount_usd}{description}".encode()).hexdigest()[:16]
        return tx_id in self.approved_transactions
    
    def _generate_approval_code(self) -> str:
        """Generate a random 6-digit approval code."""
        return f"{random.randint(100000, 999999)}"
    
    def _check_rate_limit(self) -> bool:
        """Check if rate limit is exceeded."""
        cutoff_time = datetime.now() - timedelta(hours=1)
        # Remove old transactions
        self.transaction_history = [
            tx for tx in self.transaction_history 
            if tx['timestamp'] > cutoff_time
        ]
        
        # Check limit (max 10 per hour)
        return len(self.transaction_history) < 10
    
    def _record_transaction(self, amount_usd: float):
        """Record a transaction for rate limiting."""
        self.transaction_history.append({
            'amount_usd': amount_usd,
            'timestamp': datetime.now()
        })
    
    def cleanup_expired_approvals(self) -> int:
        """Remove expired approval requests. Returns count removed."""
        now = datetime.now()
        expired_codes = []
        
        for code, approval in list(self.pending_approvals.items()):
            if now > approval['expires']:
                expired_codes.append(code)
        
        for code in expired_codes:
            del self.pending_approvals[code]
        
        if expired_codes:
            logger.info(f"Cleaned up {len(expired_codes)} expired approval requests")
        
        return len(expired_codes)
    
    async def get_risk_status(self) -> Dict[str, Any]:
        """Get current risk management status."""
        cutoff_time = datetime.now() - timedelta(hours=1)
        recent_txs = [tx for tx in self.transaction_history if tx['timestamp'] > cutoff_time]
        
        total_volume = sum(tx['amount_usd'] for tx in recent_txs)
        
        return {
            'max_transaction_usd': self.MAX_TRANSACTION_USD,
            '2fa_threshold_usd': self.TWO_FA_THRESHOLD_USD,
            'transactions_last_hour': len(recent_txs),
            'volume_last_hour_usd': total_volume,
            'pending_approvals': len(self.pending_approvals),
            'telegram_enabled': self.telegram_bot is not None
        }
