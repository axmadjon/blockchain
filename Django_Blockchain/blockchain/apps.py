import json
import time
from threading import Thread

import requests as http
from django.apps import AppConfig

from Django_Blockchain import NODES
from blockchain.core.blockchain import Blockchain
from blockchain.util import print_exception

blockchain = None


def node_sync(thread_start=False):
    if thread_start:
        time.sleep(5 * 60)

        all_nodes = []

        for node in NODES:
            try:
                response = http.get('{}/{}'.format(node, 'node&load_nodes'))
                if response.ok:
                    all_nodes += json.loads(response.text)
            except:
                print_exception()

        for node in all_nodes:
            if node.startswith('http') and node not in NODES:
                NODES.append(node)

    Thread(target=node_sync, args=(True,)).start()


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

        node_sync()

        callback = lambda: Thread(target=self.start_mine).start()
        Thread(target=blockchain.load_database, args=(callback,)).start()
