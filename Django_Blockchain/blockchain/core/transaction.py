from hashlib import sha256
from time import time

TRANSACTION_QUEUE = "Q"


class Transaction:
    def __init__(self, tx_type):
        self.tx_type = tx_type

    def hash_tx(self):
        return sha256(self.tx_type).hexdigest()


class QueueTransaction(Transaction):
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
