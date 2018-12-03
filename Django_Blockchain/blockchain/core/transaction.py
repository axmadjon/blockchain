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

TRANSACTION_QUEUE = 'Q'


class Transaction:
    @staticmethod
    def parse(tx_json):
        if tx_json['tx_type'] == TRANSACTION_QUEUE:
            return QueueTransaction.parse(tx_json)

        return None

    def __init__(self, tx_type):
        self.tx_type = tx_type
        self.tx_hash = '0'

    def verify(self):
        return True

    def to_json(self, with_dumps):
        tx_json = {'tx_type': self.tx_type}
        if bool(with_dumps):
            return json.dumps(tx_json)
        return tx_json


class QueueTransaction(Transaction):
    @staticmethod
    def parse(tx_json):
        queue_transaction = QueueTransaction(
            passport_serial=tx_json['passport_serial'],
            queue_number=tx_json['queue_number'],
            public_key_b64=tx_json['public_key_b64'],
            signature_b64=tx_json['signature_b64'],
            tx_timestamp_tz=str(tx_json['timestamp']))

        return queue_transaction

    def to_json(self, with_dumps):
        tx_json = super().to_json(with_dumps=False)

        tx_json['tx_type'] = self.tx_type

        tx_json['timestamp'] = self.tx_timestamp_tz
        tx_json['passport_serial'] = self.passport_serial
        tx_json['queue_number'] = self.queue_number

        tx_json['public_key_b64'] = self.__public_key_b64
        tx_json['public_key_hash'] = self.public_key_hash
        tx_json['signature_b64'] = self.__signature_b64

        if bool(with_dumps):
            return json.dumps(tx_json)
        return tx_json

    def __init__(self, passport_serial, queue_number, public_key_b64, signature_b64, tx_timestamp_tz):
        super().__init__(TRANSACTION_QUEUE)

        self.tx_timestamp_tz = tx_timestamp_tz
        self.passport_serial = passport_serial
        self.queue_number = queue_number

        self.__public_key_b64 = public_key_b64
        self.public_key_hash = sha256(public_key_b64.encode('utf-8')).hexdigest()
        self.__signature_b64 = signature_b64

        self.tx_hash = self.calc_hash()

    def verify(self):
        try:
            hash_sha256 = SHA256.new()
            hash_sha256.update(self.tx_hash.encode('utf-8'))

            signature = base64.standard_b64decode(self.__signature_b64.encode('utf-8'))
            public_key = RSA.import_key(base64.standard_b64decode(self.__public_key_b64.encode('utf-8')), 'PEM')
            pkcs1_15.new(public_key).verify(hash_sha256, signature)
            return True
        except:
            print_exception('QueueTransaction.verify')
            return False

    def calc_hash(self):
        data_to_hash = '{}:{}:{}:{}'.format(self.tx_type, self.tx_timestamp_tz, self.passport_serial, self.queue_number)
        return sha256(data_to_hash.encode('utf-8')).hexdigest()
