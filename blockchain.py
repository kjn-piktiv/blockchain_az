# Module 1 - Create a blockchain

import datetime as dt
import hashlib as hl
import json
from flask import Flask, jsonify


class Proof:
    def __init__(self, proof):
        self.value = proof

    def proof_of_work(self):
        new_proof = Proof(1)
        while not self.is_valid(new_proof):
            new_proof = Proof(new_proof.value + 1)
        return new_proof

    def is_valid(self, new_proof):
        hash = hl.sha256(
            str(new_proof.value ** 2 - self.value ** 2).encode()).hexdigest()
        return hash[:4] == '0000'

    def __str__(self):
        return str(self.value)


class Block:
    def __init__(self, index, proof, previous_hash):
        self.proof = proof
        self.index = index
        self.timestamp = dt.datetime.now()
        self.previous_hash = previous_hash

    def hash(self):
        encoded_block = json.dumps(self.to_json(), sort_keys=True).encode()
        return hl.sha256(encoded_block).hexdigest()

    def to_json(self):
        return {
            'index': self.index,
            'timestamp': str(self.timestamp),
            'proof': str(self.proof),
            'previous_hash': self.previous_hash
        }


class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_block(proof=Proof(1), previous_hash='0')

    def create_block(self, proof, previous_hash):
        block = Block(len(self.chain) + 1, proof, previous_hash)
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def is_valid(self):
        for previous_block, block in zip(self.chain, self.chain[1:]):
            if block.previous_hash != previous_block.hash():
                return False
            if not previous_block.proof.is_valid(block.proof):
                return False
        return True


app = Flask(__name__)


blockchain = Blockchain()

@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block.proof
    proof = previous_proof.proof_of_work()
    previous_hash = previous_block.hash()
    block = blockchain.create_block(proof, previous_hash)
    response = block.to_json()
    response['message'] = 'You just mined a block'
    return jsonify(response), 200

@app.route('/get_chain', methods = ['GET'])
def get_chain():
    chain = blockchain.chain
    response = {
        'chain': [ block.to_json() for block in chain ],
        'length': len(chain)
    }
    return jsonify(response), 200

@app.route('/is_valid', methods = ['GET'])
def is_valid():
    response = {
        'is_valid': blockchain.is_valid(),
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200
