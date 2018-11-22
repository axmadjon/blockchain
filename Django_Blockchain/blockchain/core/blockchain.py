import json
import os
import sys
import time
from hashlib import sha256
from threading import Thread

import requests as http

from Django_Blockchain import NODES, DATABASE_DIRS, BLOCK_TRANSACTION, BLOCK_DIFFICULTY, BLOCK_SECOND
from blockchain.core.transaction import Transaction, QueueTransaction
from blockchain.util import print_exception


class Block:
    @staticmethod
    def parse(json):
        block = Block(index=json['index'], previous_hash=json['previous_hash'])
        block.difficulty = json['difficulty']
        block.timestamp = json['timestamp']
        block.block_hash = json['block_hash']
        block.nonce = json['nonce']

        for item in json['transactions']:
            transaction = Transaction.parse(item)
            if transaction:
                block.__transaction.append(transaction)

        return block

    def to_json(self):
        transactions = [json.loads(item.to_json()) for item in self.__transaction]
        return json.dumps({
            'index': self.index,
            'previous_hash': self.previous_hash,
            'difficulty': self.difficulty,
            'timestamp': self.timestamp,
            'block_hash': self.block_hash,
            'nonce': self.nonce,
            'transactions': transactions
        })

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

    def pow(self):
        try:
            transaction_list = [tx.hash_tx() for tx in self.__transaction]
            data_block = json.dumps([self.index,
                                     self.previous_hash,
                                     self.difficulty,
                                     transaction_list,
                                     self.timestamp,
                                     self.nonce])

            block_hash = sha256(data_block.encode('utf-8')).hexdigest()
            return block_hash.startswith('0' * self.difficulty)
        except:
            return False

    def is_valid(self):
        return self.block_hash.startswith('0' * self.difficulty)

    def start_find_pow(self, load_last_block=None):
        transaction_list = [tx.hash_tx() for tx in self.__transaction]

        start = time.time()

        for nonce in range(sys.maxsize):
            self.nonce = nonce
            self.timestamp = int(time.time() * 1000.0)

            if nonce % 100000 == 0:
                last_block = load_last_block()
                if last_block.index != self.index - 1:
                    print('last block has change')
                    return False

            data_block = json.dumps([self.index,
                                     self.previous_hash,
                                     self.difficulty,
                                     transaction_list,
                                     self.timestamp,
                                     self.nonce])

            self.block_hash = sha256(data_block.encode('utf-8')).hexdigest()

            if self.is_valid():
                print('block {} mined in {} second => {}'
                      .format(self.index, (time.time() - start), self.block_hash))
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

    def load_database(self, callback):
        print('load all blocks in database')
        try:
            files = [v for v in os.listdir(DATABASE_DIRS) if v.endswith('.json')]
            files.sort()

            for file in files:
                with open('{}/{}'.format(DATABASE_DIRS, file), 'r') as file_json:
                    block_json = json.load(file_json)
                    block = Block.parse(block_json)
                    self.add_block(block)

            print('success load in database')

            print('load database in server')

            self.synchronization()

            print('success load database in server')

        except:
            print_exception('Blockchain.load_database')

        callback()

    @classmethod
    def save_block_database(cls, block):
        try:
            block_json = json.loads(block.to_json())
            file_name = ('0' * 10) + str(block.index)
            file_name = file_name[len(file_name) - 10:] + '.json'

            if not os.path.exists(DATABASE_DIRS):
                os.makedirs(DATABASE_DIRS)

            with open('{}/{}'.format(DATABASE_DIRS, file_name), 'w') as file_json:
                json.dump(block_json, file_json)
        except:
            print_exception('Blockchain.save_block_database')

    def add_block(self, block):
        if not isinstance(block, Block):
            return False

        last_block = self.last_chain()
        if last_block.index == block.index and last_block.block_hash == block.block_hash:
            return True

        if last_block.index != 0 and BLOCK_SECOND > int(time.time()) - int(last_block.timestamp / 1000.0):
            return False

        if self.last_chain().index == (block.index - 1) \
                and block.is_valid() and block.pow():
            self.chains.append(block)
            self.save_block_database(block)
            return True

        return False

    def add_transaction(self, transaction):
        self.unconfirmed_transaction.append(transaction)
        return True

    def last_chain(self):
        return self.chains[-1]

    def mine(self):
        all_txs = self.unconfirmed_transaction.copy()
        last_block = self.last_chain()

        new_block = Block(index=last_block.index + 1, previous_hash=last_block.block_hash)
        removing_txs = list()

        for index, tx in enumerate(all_txs):
            if new_block.add_transaction(tx):
                removing_txs.append(tx)
            else:
                break

        if new_block.start_find_pow(lambda: self.last_chain()):
            if BLOCK_SECOND <= int(time.time()) - int(last_block.timestamp / 1000.0):
                self.synchronization()
                if self.add_block(new_block):

                    if not self.send_block_all_nodes(new_block):
                        print("######### ERROR NODE NOT ADDED BLOCK #########")

                    for index in removing_txs:
                        self.unconfirmed_transaction.pop(index)
                else:
                    print('cannot add block in chain')
        else:
            print('not find block hash')

        Thread(target=self.mine).start()

    def synchronization(self):
        last_block = self.last_chain()
        for nod in NODES:
            try:
                response = http.get('{}/{}'.format(nod, 'node&load_last_block'))
                if response.ok:
                    node_last_block = Block.parse(json.loads(response.text))

                    if node_last_block.index > last_block.index:
                        self.load_all_blocks(nod)
            except:
                print_exception('Blockchain.synchronization')

    def load_all_blocks(self, node):
        try:
            resp = http.post('{}/{}'.format(node, 'node&load_blocks'), json={'start_index': self.last_chain().index})
            if resp.ok:
                blocks = [Block.parse(item) for item in json.loads(resp.text)]
                for b in blocks:
                    if not self.add_block(b):
                        print('node block not added in blockchain, block have problem')
                        return
        except:
            print('error load_all_blocks')

    def send_block_all_nodes(self, block):
        block_json = json.loads(block.to_json())
        for nod in NODES:
            try:
                resp = http.post('{}/{}'.format(nod, 'node&add_new_block'), json=block_json)
                if resp.ok:
                    return 'S' == resp.text
                else:
                    self.synchronization()
            except:
                print('error send_block_all_nodes')

        return True
