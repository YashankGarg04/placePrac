import hashlib
import json


class Block:
    def __init__(self, index, timestamp, transactions, previous_hash, nonce=0, miner_id="genesis", block_hash=None):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.miner_id = miner_id
        self.hash = block_hash if block_hash is not None else self.calculate_hash()

    def calculate_hash(self):
        # Deterministic string representation: index || timestamp || transactions || previous_hash || nonce || miner_id
        tx_str = json.dumps(self.transactions, sort_keys=True, separators=(',', ':'))
        payload = f"{self.index}|{self.timestamp}|{tx_str}|{self.previous_hash}|{self.nonce}|{self.miner_id}"
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()

    def mine(self, difficulty=3):
        target = "0" * difficulty
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.calculate_hash()
        return self.hash

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": list(self.transactions),
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "miner_id": self.miner_id,
            "hash": self.hash
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            index=data["index"],
            timestamp=data["timestamp"],
            transactions=list(data["transactions"]),
            previous_hash=data["previous_hash"],
            nonce=data["nonce"],
            miner_id=data["miner_id"],
            block_hash=data["hash"]
        )


class Blockchain:
    def __init__(self, difficulty=3):
        self.difficulty = difficulty
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis = Block(
            index=0,
            timestamp="0",
            transactions=["GENESIS"],
            previous_hash="0" * 64,
            nonce=0,
            miner_id="system"
        )
        genesis.mine(self.difficulty)
        self.chain = [genesis]
        return genesis

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, block):
        if self.validate_new_block(block, self.get_latest_block()):
            self.chain.append(block)
            return True
        return False

    def validate_new_block(self, block, previous_block):
        if block.index != previous_block.index + 1:
            return False
        if block.previous_hash != previous_block.hash:
            return False
        if block.calculate_hash() != block.hash:
            return False
        if not block.hash.startswith("0" * self.difficulty):
            return False
        return True

    def is_valid(self):
        return Blockchain.validate_chain_list(self.chain, self.difficulty)

    @staticmethod
    def validate_chain_list(chain_list, difficulty=3):
        if not chain_list:
            return False

        expected_genesis = Block(0, "0", ["GENESIS"], "0" * 64, 0, "system")
        expected_genesis.mine(difficulty)
        g = chain_list[0]
        if (g.index != 0 or g.previous_hash != "0" * 64 or
                g.calculate_hash() != g.hash or g.hash != expected_genesis.hash):
            return False

        for i in range(1, len(chain_list)):
            current = chain_list[i]
            prev = chain_list[i - 1]
            if current.index != prev.index + 1:
                return False
            if current.previous_hash != prev.hash:
                return False
            if current.calculate_hash() != current.hash:
                return False
            if not current.hash.startswith("0" * difficulty):
                return False
        return True

    def to_list(self):
        return [b.to_dict() for b in self.chain]

    @classmethod
    def from_list(cls, data_list):
        return [Block.from_dict(item) for item in data_list]