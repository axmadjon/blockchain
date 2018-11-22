from threading import Thread

from django.apps import AppConfig

from blockchain.core.blockchain import Blockchain

blockchain = None


class BlockchainConfig(AppConfig):
    name = 'blockchain'
    verbose_name = "Django Blockchain"

    @classmethod
    def start_mine(cls):
        global blockchain
        blockchain.mine()

    def ready(self, recall=False):
        global blockchain
        blockchain = Blockchain()

        callback = lambda: Thread(target=self.start_mine).start()
        Thread(target=blockchain.load_database, args=(callback,)).start()
