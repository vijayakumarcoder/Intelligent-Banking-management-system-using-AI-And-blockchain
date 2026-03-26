import hashlib
import json
import time
from datetime import datetime
from sklearn.ensemble import IsolationForest
import numpy as np

class Blockchain:
    """
    Core Blockchain Class
    - Block create pannum
    - Hash calculate pannum
    - Chain maintain pannum
    """
    
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.mining_reward = 10  # Mining reward amount
        self.difficulty = 2  # Proof of work difficulty (2 means hash must start with '00')
        self.balance_cache = {}  # Cache for balances to improve performance
        self.transaction_cache = {}  # Cache for transactions per address
        self.fraud_model = IsolationForest(contamination=0.1, random_state=42)  # AI for fraud detection
        self.transaction_features = []  # Features for training: [amount, hour]

        # Genesis block create panrom (first block)
        self.create_genesis_block()
    
    def create_genesis_block(self):
        """
        First block ah create pannum (Genesis Block)
        Intha block ku previous hash illa
        """
        genesis_block = {
            'index': 0,
            'timestamp': str(datetime.now()),
            'transactions': [],
            'proof': 0,
            'previous_hash': '0'
        }
        genesis_block['hash'] = self.calculate_hash(genesis_block)
        self.chain.append(genesis_block)
    
    def calculate_hash(self, block):
        """
        Block oda hash calculate pannum using SHA-256
        Block data ah string ah convert panni hash create panrom
        """
        block_string = json.dumps({
            'index': block['index'],
            'timestamp': block['timestamp'],
            'transactions': block['transactions'],
            'proof': block['proof'],
            'previous_hash': block['previous_hash']
        }, sort_keys=True)
        
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def get_latest_block(self):
        """
        Chain la last block ah return pannum
        """
        return self.chain[-1]
    
    def add_transaction(self, sender, receiver, amount, signature, fee=0.1):
        """
        New transaction ah pending list la add pannum
        Mining apram thaan intha transaction block la add aagum
        Fee is collected for network maintenance
        """
        transaction = {
            'sender': sender,
            'receiver': receiver,
            'amount': amount,
            'fee': fee,
            'signature': signature,
            'timestamp': str(datetime.now())
        }

        self.pending_transactions.append(transaction)
        return self.get_latest_block()['index'] + 1
    
    def mine_pending_transactions(self, mining_reward_address):
        """
        Pending transactions ellam eduthu new block create pannum
        Proof of work solve panni block ah chain la add pannum
        """
        if len(self.pending_transactions) == 0:
            return False
        
        block = {
            'index': len(self.chain),
            'timestamp': str(datetime.now()),
            'transactions': self.pending_transactions,
            'proof': 0,
            'previous_hash': self.get_latest_block()['hash']
        }
        
        # Proof of work - difficulty based hash find pannum
        block['proof'] = self.proof_of_work(block)
        block['hash'] = self.calculate_hash(block)
        
        self.chain.append(block)

        # Clear caches since new transactions added
        self.balance_cache = {}
        self.transaction_cache = {}

        # Calculate total fees from mined transactions
        total_fees = sum(tx.get('fee', 0) for tx in block['transactions'] if tx['sender'] != 'SYSTEM')

        # Mining reward transaction add pannum (includes fees)
        self.pending_transactions = [{
            'sender': 'SYSTEM',
            'receiver': mining_reward_address,
            'amount': self.mining_reward + total_fees,
            'signature': 'MINING_REWARD',
            'timestamp': str(datetime.now())
        }]
        
        return True
    
    def proof_of_work(self, block):
        """
        Proof of Work algorithm
        Oru specific pattern la hash vara proof number find pannum
        Example: hash '00' la start aaganum (difficulty = 2)
        """
        proof = 0
        while True:
            block['proof'] = proof
            hash_value = self.calculate_hash(block)
            
            # Check if hash meets difficulty requirement
            if hash_value[:self.difficulty] == '0' * self.difficulty:
                return proof
            
            proof += 1
    
    def is_chain_valid(self):
        """
        Blockchain valid-ah iruka check pannum
        Each block oda hash correct-ah iruka verify pannum
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            # Current block hash correct-ah iruka check pannum
            if current_block['hash'] != self.calculate_hash(current_block):
                return False
            
            # Previous hash link correct-ah iruka check pannum
            if current_block['previous_hash'] != previous_block['hash']:
                return False
        
        return True
    
    def get_balance(self, address):
        """
        Oru wallet address oda balance calculate pannum
        All transactions scan panni balance return pannum
        Uses cache for performance
        """
        if address in self.balance_cache:
            return self.balance_cache[address]

        balance = 0

        for block in self.chain:
            for transaction in block['transactions']:
                if transaction['sender'] == address:
                    balance -= transaction['amount'] + transaction.get('fee', 0)

                if transaction['receiver'] == address:
                    balance += transaction['amount']

        self.balance_cache[address] = balance
        return balance
    
    def get_transactions_for_address(self, address):
        """
        Oru address related ah all transactions return pannum
        Uses cache for performance
        """
        if address in self.transaction_cache:
            return self.transaction_cache[address]

        transactions = []

        for block in self.chain:
            for transaction in block['transactions']:
                if transaction['sender'] == address or transaction['receiver'] == address:
                    transactions.append({
                        'block': block['index'],
                        'sender': transaction['sender'],
                        'receiver': transaction['receiver'],
                        'amount': transaction['amount'],
                        'timestamp': transaction['timestamp']
                    })

        self.transaction_cache[address] = transactions
        return transactions

    def check_fraud(self, amount, sender_balance):
        """
        AI-based fraud detection using Isolation Forest
        Returns True if suspicious
        """
        if len(self.transaction_features) < 10:
            # Not enough data, allow
            return False

        # Retrain model with current data
        self.fraud_model.fit(self.transaction_features)

        # Predict for new transaction
        hour = datetime.now().hour
        features = np.array([[amount, hour]])
        prediction = self.fraud_model.predict(features)

        return prediction[0] == -1  # -1 is anomaly

    def deposit(self, address, amount):
        """
        Deposit money to address (simulated external deposit)
        """
        transaction = {
            'sender': 'BANK',
            'receiver': address,
            'amount': amount,
            'fee': 0,
            'signature': 'DEPOSIT',
            'timestamp': str(datetime.now())
        }

        self.pending_transactions.append(transaction)
        # Immediately mine for deposit
        self.mine_pending_transactions('SYSTEM')
        return True