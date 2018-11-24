from django.conf.urls import url

from blockchain.views import load_nodes, load_last_block, load_blocks, add_transaction, add_new_block,register_nodes

urlpatterns = [
    url(r'^&load_nodes', load_nodes),
    url(r'^&register_nodes', register_nodes),

    url(r'^&load_last_block', load_last_block),
    url(r'^&load_blocks', load_blocks),

    url(r'^&add_transaction', add_transaction),
    url(r'^&add_new_block', add_new_block),
]
