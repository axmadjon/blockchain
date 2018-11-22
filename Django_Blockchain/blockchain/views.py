import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from Django_Blockchain import NODES
from blockchain.apps import blockchain
from blockchain.core.blockchain import Block
from blockchain.core.transaction import Transaction


def check_and_add_block(block, recall=False):
    if blockchain.add_block(block):
        return HttpResponse('S', status=200)

    if recall:
        return HttpResponse('E', status=200)

    last_block = blockchain.last_chain()

    if last_block.index >= block.index:
        return HttpResponse('E', status=200)

    elif last_block.index < block.index:
        blockchain.synchronization()
        return check_and_add_block(block=block, recall=True)


def load_blocks_in_blockchain(req_json):
    start_index = req_json['start_index']
    end_index = req_json.get('end_index', blockchain.last_chain().index)

    return [json.loads(block.to_json()) for block in blockchain.chains if start_index < block.index < end_index]


@csrf_exempt
def load_nodes(request):
    return HttpResponse(json.dumps(NODES), content_type='application/json; charset=utf-8', status=200)


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
    blockchain.add_transaction(transaction)
    return HttpResponse(status=200)


@csrf_exempt
def add_new_block(request):
    # blockchain.synchronization()
    block = Block.parse(json.loads(request.body))
    return check_and_add_block(block)
