import hashlib
import time
from datetime import datetime
from typing import List, Dict, Any

class Block:
    def __init__(self, index: int, transactions: List[Dict], previous_hash: str, timestamp: float = None):
        self.index = index
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.timestamp = timestamp or time.time()
        self.nonce = 0
        self.hash = None
    
    def calculate_hash(self) -> str:
        block_string = f"{self.index}{self.timestamp}{self.transactions}{self.previous_hash}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty: int) -> None:
        target = '0' * difficulty
        print(f"Mining Block #{self.index}...")
        start_time = time.time()
        while True:
            self.hash = self.calculate_hash()
            if self.hash.startswith(target):
                elapsed_time = time.time() - start_time
                print(f"Block #{self.index} mined! Nonce: {self.nonce}, Time: {elapsed_time:.2f}s")
                break
            self.nonce += 1
    
    def to_dict(self) -> Dict:
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'nonce': self.nonce,
            'hash': self.hash,
            'previous_hash': self.previous_hash,
            'transactions': self.transactions,
            'formatted_timestamp': datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S')
        }

class Blockchain:
    def __init__(self, difficulty: int = 3):
        self.chain: List[Block] = []
        self.difficulty = difficulty
        self.pending_transactions: List[Dict] = []
        self.mining_reward = 10
        self.create_genesis_block()
    
    def create_genesis_block(self) -> None:
        print("Creating Genesis Block...")
        genesis_block = Block(0, [], "0")
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)
    
    def get_latest_block(self) -> Block:
        return self.chain[-1]
    
    def add_transaction(self, sender: str, recipient: str, amount: float) -> bool:
        if amount <= 0:
            return False
        transaction = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
            'timestamp': time.time()
        }
        self.pending_transactions.append(transaction)
        print(f"Transaction added: {sender} -> {recipient} ({amount} coins)")
        return True
    
    def mine_pending_transactions(self, miner_address: str) -> Block:
        if not self.pending_transactions:
            print("No pending transactions!")
            return None
        
        self.pending_transactions.append({
            'sender': 'SYSTEM',
            'recipient': miner_address,
            'amount': self.mining_reward,
            'timestamp': time.time()
        })
        
        new_block = Block(
            len(self.chain),
            self.pending_transactions,
            self.get_latest_block().hash
        )
        
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)
        self.pending_transactions = []
        return new_block
    
    def get_balance(self, address: str) -> float:
        balance = 0
        for block in self.chain:
            for transaction in block.transactions:
                if transaction['sender'] == address:
                    balance -= transaction['amount']
                if transaction['recipient'] == address:
                    balance += transaction['amount']
        return balance
    
    def is_chain_valid(self) -> bool:
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            if current_block.hash != current_block.calculate_hash():
                return False
            if not current_block.hash.startswith('0' * self.difficulty):
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        total_transactions = sum(len(block.transactions) for block in self.chain)
        total_volume = sum(tx['amount'] for block in self.chain for tx in block.transactions)
        return {
            'total_blocks': len(self.chain),
            'total_transactions': total_transactions,
            'total_volume': total_volume,
            'difficulty': self.difficulty,
            'is_valid': self.is_chain_valid()
        }
    
    def get_chain_data(self) -> List[Dict]:
        return [block.to_dict() for block in self.chain]
    
    def get_all_addresses(self) -> List[str]:
        addresses = set()
        for block in self.chain:
            for tx in block.transactions:
                addresses.add(tx['sender'])
                addresses.add(tx['recipient'])
        return sorted(list(addresses))
    
    def get_transaction_history(self, address: str) -> List[Dict]:
        history = []
        for block in self.chain:
            for tx in block.transactions:
                if tx['sender'] == address or tx['recipient'] == address:
                    tx_copy = tx.copy()
                    tx_copy['timestamp'] = datetime.fromtimestamp(tx['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                    history.append(tx_copy)
        return history