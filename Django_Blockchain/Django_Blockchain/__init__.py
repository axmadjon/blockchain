import configparser
import os

default_app_config = 'blockchain.apps.BlockchainConfig'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROP_PATH = os.path.join(BASE_DIR, '.properties')

NODES = []
DATABASE_DIRS = os.path.join(BASE_DIR, 'db_blockchain')

BLOCK_SECOND = 60
BLOCK_TRANSACTION = 5
BLOCK_DIFFICULTY = 5

if not os.path.exists(PROP_PATH):
    with open(PROP_PATH, 'w', encoding="utf-8") as f:
        f.write("[NETWORK]\n"
                "nodes=\n\n"

                "[LOCAL]\n"
                "db_dirs={}\n\n"

                "[SETTING]\n"
                "block_second=60\n"
                "block_difficulty=5\n"
                "block_transaction=5".format(DATABASE_DIRS))
else:
    config = configparser.RawConfigParser()
    config.read(PROP_PATH)

    # Server properties
    network_config = dict(config.items('NETWORK'))
    NODES = [item.strip() for item in network_config.get('nodes').split('|')]

    local_config = dict(config.items("LOCAL"))
    DATABASE_DIRS = local_config.get("db_dirs")

    media_config = dict(config.items("SETTING"))
    BLOCK_SECOND = int(media_config.get("block_second", BLOCK_SECOND))
    BLOCK_TRANSACTION = int(media_config.get("block_transaction"))
    BLOCK_DIFFICULTY = int(media_config.get("block_difficulty"))

NODES = [node for node in NODES if node.startswith('http')]

if not os.path.exists(DATABASE_DIRS):
    os.makedirs(DATABASE_DIRS)
