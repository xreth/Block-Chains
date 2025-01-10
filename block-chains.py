import hashlib
import time
import json
from typing import List

class Transaction:
    def __init__(self, sender, recipient, amount):
        
        self.sender = sender
        self.recipient = recipient
        self.amount = amount

class Block:
    def __init__(self, index, previous_hash, timestamp, transactions, proof, hash):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.transactions = transactions
        self.proof = proof
        self.hash = hash

def calculate_hash(index, previous_hash, timestamp, transactions, proof):
    value = str(index) + str(previous_hash) + str(timestamp) + str(transactions) + str(proof)
    return hashlib.sha256(value.encode()).hexdigest()

def create_genesis_block():
    return Block(0, "0", time.time(), [], 0, calculate_hash(0, "0", time.time(), [], 0))

def create_new_block(index, previous_hash, transactions, proof):
    timestamp = time.time()
    hash = calculate_hash(index, previous_hash, timestamp, transactions, proof)
    return Block(index, previous_hash, timestamp, transactions, proof, hash)

def proof_of_work(last_proof):
    proof = 0
    while not valid_proof(last_proof, proof):
        proof += 1
    return proof

def valid_proof(last_proof, proof):
    guess = f'{last_proof}{proof}'.encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    return guess_hash[:2] == "00"

class Blockchain:
    def __init__(self):
        self.chain = [create_genesis_block()]
        self.transactions = []
        self.nodes = set()

    def add_transaction(self, sender, recipient, amount):
        self.transactions.append(Transaction(sender, recipient, amount))
        return self.last_block.index + 1

    def add_node(self, address):
        self.nodes.add(address)

    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]

            if block['previous_hash'] != calculate_hash(last_block['index'], last_block['previous_hash'], last_block['timestamp'], last_block['transactions'], last_block['proof']):
                return False

            if not valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        neighbors = self.nodes
        new_chain = None

        max_length = len(self.chain)

        for node in neighbors:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

        return False

blockchain = Blockchain()

last_block = blockchain.chain[-1]
proof = proof_of_work(last_block.proof)
blockchain.add_transaction("Genesis", "Alice", 1)

blockchain.add_transaction("Genesis", "Tyler", 20)

blockchain.add_node("http://localhost:5001")

last_proof = last_block.proof
proof = proof_of_work(last_proof)

blockchain.add_transaction("Miner", "Recipient", 1)  # Example transaction
block = create_new_block(last_block.index + 1, last_block.hash, blockchain.transactions, proof)

blockchain.transactions = []

blockchain.chain.append(block)

for block in blockchain.chain:
    print(f"Block #{block.index} - Hash: {block.hash} - Proof: {block.proof} - Transactions: {len(block.transactions)}")
