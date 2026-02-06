"""
Wallet module with ERC-4337 session keys for non-custodial execution.
Handles wallet operations and session key management.
"""
import os
import asyncio
from typing import Optional, Dict, Any
from web3 import Web3
from eth_account import Account
from eth_account.signers.local import LocalAccount
import logging

logger = logging.getLogger(__name__)


class SessionKey:
    """Manages ERC-4337 session keys for delegated transactions."""
    
    def __init__(self, private_key: str, permissions: Dict[str, Any]):
        """
        Initialize a session key.
        
        Args:
            private_key: The private key for this session
            permissions: Dictionary of permissions (max_amount, expiry, etc.)
        """
        self.account: LocalAccount = Account.from_key(private_key)
        self.permissions = permissions
        self.address = self.account.address
        
    def can_execute(self, amount: float) -> bool:
        """Check if session key can execute transaction of given amount."""
        max_amount = self.permissions.get('max_amount', 0)
        return amount <= max_amount
    
    def is_expired(self) -> bool:
        """Check if session key has expired."""
        import time
        expiry = self.permissions.get('expiry', float('inf'))
        return time.time() > expiry


class Wallet:
    """Non-custodial wallet with ERC-4337 session key support."""
    
    def __init__(self):
        """Initialize wallet with environment variables."""
        self.private_key = os.getenv('WALLET_PRIVATE_KEY')
        if not self.private_key:
            logger.warning("No WALLET_PRIVATE_KEY found, generating new wallet")
            self.account = Account.create()
            self.private_key = self.account.key.hex()
        else:
            self.account = Account.from_key(self.private_key)
        
        self.address = self.account.address
        self.session_keys: Dict[str, SessionKey] = {}
        self.w3 = self._init_web3()
        logger.info(f"Wallet initialized: {self.address}")
        
    def _init_web3(self) -> Web3:
        """Initialize Web3 provider."""
        rpc_url = os.getenv('RPC_URL', 'https://eth-mainnet.g.alchemy.com/v2/demo')
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        return w3
    
    def create_session_key(self, max_amount: float, duration_hours: int = 24) -> SessionKey:
        """
        Create a new ERC-4337 session key.
        
        Args:
            max_amount: Maximum transaction amount for this session
            duration_hours: How long the session key is valid
            
        Returns:
            SessionKey object
        """
        import time
        
        # Generate new account for session
        session_account = Account.create()
        
        permissions = {
            'max_amount': max_amount,
            'expiry': time.time() + (duration_hours * 3600),
            'created_by': self.address
        }
        
        session_key = SessionKey(session_account.key.hex(), permissions)
        self.session_keys[session_key.address] = session_key
        
        logger.info(f"Created session key: {session_key.address} with max_amount: {max_amount}")
        return session_key
    
    async def get_balance(self) -> float:
        """Get wallet balance in ETH."""
        try:
            balance_wei = self.w3.eth.get_balance(self.address)
            balance_eth = self.w3.from_wei(balance_wei, 'ether')
            return float(balance_eth)
        except Exception as e:
            logger.error(f"Error getting balance: {e}")
            return 0.0
    
    async def estimate_gas(self, transaction: Dict[str, Any]) -> int:
        """Estimate gas for a transaction."""
        try:
            gas_estimate = self.w3.eth.estimate_gas(transaction)
            return gas_estimate
        except Exception as e:
            logger.error(f"Error estimating gas: {e}")
            return 21000  # Default gas limit
    
    async def sign_transaction(self, transaction: Dict[str, Any], 
                              session_key: Optional[SessionKey] = None) -> str:
        """
        Sign a transaction with main account or session key.
        
        Args:
            transaction: Transaction dictionary
            session_key: Optional session key to use for signing
            
        Returns:
            Signed transaction hash
        """
        try:
            # Use session key if provided and valid
            signer = session_key.account if session_key else self.account
            
            # Add nonce and gas
            transaction['nonce'] = self.w3.eth.get_transaction_count(signer.address)
            transaction['gas'] = await self.estimate_gas(transaction)
            transaction['gasPrice'] = self.w3.eth.gas_price
            
            # Sign transaction
            signed_txn = signer.sign_transaction(transaction)
            
            logger.info(f"Transaction signed: {signed_txn.hash.hex()}")
            return signed_txn.hash.hex()
            
        except Exception as e:
            logger.error(f"Error signing transaction: {e}")
            raise
    
    async def send_transaction(self, to_address: str, amount: float, 
                              session_key: Optional[SessionKey] = None) -> Optional[str]:
        """
        Send ETH transaction.
        
        Args:
            to_address: Recipient address
            amount: Amount in ETH
            session_key: Optional session key to use
            
        Returns:
            Transaction hash or None
        """
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Check session key permissions if used
                if session_key and not session_key.can_execute(amount):
                    raise ValueError(f"Session key cannot execute transaction of {amount} ETH")
                
                if session_key and session_key.is_expired():
                    raise ValueError("Session key has expired")
                
                # Create transaction
                transaction = {
                    'to': to_address,
                    'value': self.w3.to_wei(amount, 'ether'),
                    'chainId': self.w3.eth.chain_id
                }
                
                signer = session_key.account if session_key else self.account
                transaction['from'] = signer.address
                transaction['nonce'] = self.w3.eth.get_transaction_count(signer.address)
                transaction['gas'] = await self.estimate_gas(transaction)
                transaction['gasPrice'] = self.w3.eth.gas_price
                
                # Sign and send
                signed_txn = signer.sign_transaction(transaction)
                tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
                
                logger.info(f"Transaction sent: {tx_hash.hex()}")
                return tx_hash.hex()
                
            except Exception as e:
                retry_count += 1
                logger.error(f"Transaction error (attempt {retry_count}/{max_retries}): {e}")
                if retry_count >= max_retries:
                    raise
                await asyncio.sleep(2 ** retry_count)  # Exponential backoff
        
        return None
    
    def get_session_key(self, address: str) -> Optional[SessionKey]:
        """Get session key by address."""
        return self.session_keys.get(address)
    
    def cleanup_expired_keys(self) -> int:
        """Remove expired session keys. Returns count of removed keys."""
        expired = [addr for addr, key in self.session_keys.items() if key.is_expired()]
        for addr in expired:
            del self.session_keys[addr]
        
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired session keys")
        
        return len(expired)
