import json
import os

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from Django_Blockchain import DATABASE_DIRS
from Django_Blockchain import NODES, REGISTER_NODE, BLOCK_DIFFICULTY
from blockchain.apps import blockchain, node_register
from blockchain.core.blockchain import Block
from blockchain.core.transaction import Transaction


def check_and_add_block(block, recall=False):
    if block.difficulty < BLOCK_DIFFICULTY:
        return HttpResponse('E', status=400)

    if blockchain.add_block(block, False):
        return HttpResponse('S', status=200)

    if recall:
        return HttpResponse('E', status=400)

    last_block = blockchain.last_chain()

    if last_block.index >= block.index:
        return HttpResponse('E', status=400)

    elif last_block.index < block.index:
        blockchain.synchronization()
        return check_and_add_block(block=block, recall=True)


def load_blocks_in_blockchain(req_json):
    start_index = req_json['start_index']
    end_index = req_json.get('end_index', blockchain.last_chain().index)

    result_blocks = list()

    if not os.path.exists(DATABASE_DIRS):
        return result_blocks

    position = start_index

    for index in range((end_index - start_index) + 1):
        file_name = blockchain.generate_block_file_name(position)
        position += 1

        file_path = '{}/{}'.format(DATABASE_DIRS, file_name)
        if not os.path.exists(file_path):
            break

        with open(file_path, 'r') as file_json:
            result_blocks.append(json.load(file_json))

    return result_blocks


@csrf_exempt
def load_nodes(request):
    return HttpResponse(json.dumps(NODES), content_type='application/json; charset=utf-8', status=200)


@csrf_exempt
def register_nodes(request):
    node_conf = json.loads(request.body)
    node = node_conf['node']

    if node.startswith('http') and \
                    node not in NODES and \
            (len(REGISTER_NODE) == 0 or node != REGISTER_NODE):
        NODES.append(node)
        node_register(node)

    return HttpResponse(status=200)


@csrf_exempt
def load_last_block(request):
    return HttpResponse(blockchain.last_chain().to_json(), content_type='application/json; charset=utf-8', status=200)


@csrf_exempt
def load_blocks(request):
    results = load_blocks_in_blockchain(json.loads(request.body))
    return HttpResponse(json.dumps(results), content_type='application/json; charset=utf-8', status=200)


@csrf_exempt
def add_transaction(request):
    transaction = Transaction.parse(json.loads(request.body))

    if transaction.verify():
        print('add new transaction {} in wait'.format(transaction.hash_tx()))
        blockchain.add_transaction(transaction)
        return HttpResponse(status=200)

    else:
        message = 'cannot add transaction {} is not valid you transaction {}'.format(transaction.hash_tx(),
                                                                                     transaction.to_json())
        print(message)
        return HttpResponse(message, status=400)


@csrf_exempt
def add_new_block(request):
    block = Block.parse(json.loads(request.body))
    return check_and_add_block(block)
