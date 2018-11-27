import base64
import json
from datetime import datetime
from hashlib import sha256

import pytz
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

from Django_Blockchain import TIMESTAMP_TZ
from blockchain.util import print_exception

TRANSACTION_QUEUE = "Q"


class Transaction:
    @staticmethod
    def parse(json):
        if json['tx_type'] == TRANSACTION_QUEUE:
            return QueueTransaction.parse(json)

        return None

    def __init__(self, tx_type):
        self.tx_type = tx_type

    def verify(self):
        return True

    def hash_tx(self):
        return sha256(self.tx_type).hexdigest()

    def to_json(self):
        return json.dumps({'tx_type': self.tx_type})


class QueueTransaction(Transaction):
    @staticmethod
    def parse(json):
        transaction = QueueTransaction(
            passport_serial=json['passport_serial'],
            queue_number=json['queue_number'],
            public_key_b64=json['public_key_b64'],
            signature_b64=json['signature_b64'])
        transaction.timestamp = json.get('timestamp', str(datetime.now(pytz.timezone(TIMESTAMP_TZ))))
        return transaction

    def to_json(self):
        return json.dumps({
            'tx_type': self.tx_type,
            'timestamp': self.timestamp,
            'passport_serial': self.passport_serial,
            'queue_number': self.queue_number,

            'public_key_b64': self.public_key_b64,
            'public_key_hash': self.public_key_hash,
            'signature_b64': self.signature_b64,
        })

    def __init__(self, passport_serial, queue_number, public_key_b64, signature_b64):
        super().__init__(TRANSACTION_QUEUE)

        self.timestamp = str(datetime.now(pytz.timezone(TIMESTAMP_TZ)))
        self.passport_serial = passport_serial
        self.queue_number = queue_number

        self.public_key_b64 = public_key_b64
        self.public_key_hash = sha256(public_key_b64.encode('utf-8')).hexdigest()
        self.signature_b64 = signature_b64

    def verify(self):
        try:
            transaction_hash = self.hash_tx()

            hash = SHA256.new()
            hash.update(transaction_hash.encode('utf-8'))

            signature = base64.standard_b64decode(self.signature_b64.encode('utf-8'))
            public_key = RSA.import_key(base64.standard_b64decode(self.public_key_b64.encode('utf-8')), 'PEM')
            pkcs1_15.new(public_key).verify(hash, signature)
            return True
        except:
            print_exception('QueueTransaction.verify')
            return False

    def hash_tx(self):
        text = '{}:{}:{}:{}' \
            .format(self.tx_type,
                    self.timestamp,
                    self.passport_serial,
                    self.queue_number)
        return sha256(text.encode('utf-8')).hexdigest()
