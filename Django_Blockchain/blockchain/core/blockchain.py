import json
import time
from hashlib import sha256
from threading import Thread
import sys

from blockchain.core.transaction import QueueTransaction

BLOCK_TRANSACTION = 5
BLOCK_DIFFICULTY = 5
DEBUG = True


class Block:
    def __init__(self, index, previous_hash):
        self.index = index
        self.previous_hash = previous_hash
        self.difficulty = BLOCK_DIFFICULTY

        self.__transaction = list()
        self.timestamp = time.time() * 1000.0
        self.block_hash = ""
        self.nonce = 0

        if not isinstance(index, int):
            raise Exception('index is not integer')

        if not isinstance(previous_hash, str):
            raise Exception('previous_hash is not string')

    def add_transaction(self, transaction):
        if not isinstance(transaction, QueueTransaction):
            raise Exception("transaction is not QueueTransaction")

        if len(self.__transaction) < BLOCK_TRANSACTION:
            self.__transaction.append(transaction)
            return True

        return False

    def is_valid(self):
        return self.block_hash.startswith('0' * self.difficulty)

    def proof_of_work(self):
        txs = json.dumps([tx.hash_tx() for tx in self.__transaction])
        for nonce in range(sys.maxsize):
            self.nonce = nonce
            data_block = json.dumps([self.index, self.previous_hash, self.difficulty, txs, self.timestamp, self.nonce])
            self.block_hash = sha256(data_block.encode('utf-8')).hexdigest()

            if self.is_valid():

                if DEBUG:
                    print('block {} => {}'.format(self.index, self.block_hash))

                return True

        return False


class Blockchain:
    def __init__(self):
        self.unconfirmed_transaction = list()
        self.chains = list()
        self.chains.append(self.genesis_block())

    def genesis_block(self):
        new_block = Block(index=0, previous_hash='0')
        new_block.difficulty = 0
        new_block.timestamp = 0
        new_block.block_hash = '0'
        new_block.nonce = 0
        return new_block

    def add_transaction(self, transaction):
        self.unconfirmed_transaction.append(transaction)

    def last_chain(self):
        return self.chains[-1]

    def mine(self):
        all_txs = self.unconfirmed_transaction.copy()
        last_block = self.last_chain()

        new_block = Block(index=last_block.index + 1, previous_hash=last_block.block_hash)

        for index, tx in enumerate(all_txs):
            if not new_block.add_transaction(tx):
                break
            else:
                self.unconfirmed_transaction.pop(index)

        print('new mine {}'.format(new_block.index))

        if new_block.proof_of_work():
            print('block id {} mined'.format(new_block.index))
            self.chains.append(new_block)
        else:
            print('not find block hash')

        Thread(target=self.mine).start()
