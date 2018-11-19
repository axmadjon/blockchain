from threading import Thread

from django.apps import AppConfig

from blockchain.core.blockchain import Blockchain


class BlockchainConfig(AppConfig):
    name = 'blockchain'
    verbose_name = "Django Blockchain"

    @classmethod
    def start_mine(cls, blockchain):
        blockchain.mine()

    def ready(self, recall=False):
        blockchain = Blockchain()

        Thread(target=self.start_mine, args=(blockchain,)).start()
