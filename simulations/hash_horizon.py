from .blockchain_launch import *

def hash_horizon(params, **options):
    return averaged_blockchain_launch(
        params,
        count=25,
        mode='miner',
        **options)
