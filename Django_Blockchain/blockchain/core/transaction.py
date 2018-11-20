import json
from hashlib import sha256
from time import time

TRANSACTION_QUEUE = "Q"


class Transaction:
    @staticmethod
    def parse(json):
        if json['tx_type'] == TRANSACTION_QUEUE:
            return QueueTransaction.parse(json)

        return None

    def __init__(self, tx_type):
        self.tx_type = tx_type

    def hash_tx(self):
        return sha256(self.tx_type).hexdigest()

    def to_json(self):
        return json.dumps({'tx_type': self.tx_type})


class QueueTransaction(Transaction):
    @staticmethod
    def parse(json):
        transaction = QueueTransaction(passport_serial=json['passport_serial'],
                                       queue_number=json['queue_number'])
        transaction.timestamp = json['timestamp']
        return transaction

    def to_json(self):
        return json.dumps({
            'tx_type': self.tx_type,
            'timestamp': self.timestamp,
            'passport_serial': self.passport_serial,
            'queue_number': self.queue_number,
        })

    def __init__(self, passport_serial, queue_number):
        super().__init__(TRANSACTION_QUEUE)

        self.timestamp = time() * 1000.0
        self.passport_serial = passport_serial
        self.queue_number = queue_number

    def hash_tx(self):
        text = '{}:{}:{}:{}' \
            .format(self.tx_type,
                    self.timestamp,
                    self.passport_serial,
                    self.queue_number)
        return sha256(text.encode('utf-8')).hexdigest()
