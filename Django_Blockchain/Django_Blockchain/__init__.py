import configparser
import os

default_app_config = 'blockchain.apps.BlockchainConfig'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROP_PATH = os.path.join(BASE_DIR, '.properties')

NODES = []
REGISTER_NODE = ''
DATABASE_DIRS = os.path.join(BASE_DIR, 'db_blockchain')
ALLOW_HOSTS_LIST = ['localhost']
RUN_DEBUG = True

BLOCK_SECOND = 30
BLOCK_TRANSACTION = 10
BLOCK_DIFFICULTY = 6

if not os.path.exists(PROP_PATH):
    with open(PROP_PATH, 'w', encoding="utf-8") as f:
        f.write("[NETWORK]\n"
                "nodes=\n"
                "register_node=\n\n"

                "[LOCAL]\n"
                "db_dirs={}\n"
                "allow_host=\n"
                "run_debug=Y\n\n"

                "[SETTING]\n"
                "block_second=30\n"
                "block_difficulty=6\n"
                "block_transaction=10".format(DATABASE_DIRS))
else:
    config = configparser.RawConfigParser()
    config.read(PROP_PATH)

    # Server properties
    network_config = dict(config.items('NETWORK'))
    NODES = [item.strip() for item in network_config.get('nodes').split('|')]
    REGISTER_NODE = network_config.get("register_node")

    local_config = dict(config.items("LOCAL"))
    DATABASE_DIRS = local_config.get("db_dirs")
    ALLOW_HOSTS_LIST = [item.strip() for item in local_config.get('allow_host').split('|')]
    RUN_DEBUG = local_config.get("run_debug") == 'Y'

    media_config = dict(config.items("SETTING"))
    BLOCK_SECOND = int(media_config.get("block_second", BLOCK_SECOND))
    BLOCK_TRANSACTION = int(media_config.get("block_transaction"))
    BLOCK_DIFFICULTY = int(media_config.get("block_difficulty"))

NODES = [node for node in NODES if node.startswith('http') and (len(REGISTER_NODE) == 0 or node != REGISTER_NODE)]

if not os.path.exists(DATABASE_DIRS):
    os.makedirs(DATABASE_DIRS)
