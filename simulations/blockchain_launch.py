from argparse import ArgumentParser
from typing import Optional

from hashwars import *

_DEFAULT_HOURS = 6
_DEFAULT_STEP = 60
_DEFAULT_PREMIUM = 1.0
_DEFAULT_MAX_REORG = 4
_DEFAULT_COUNT = 2

_parser = ArgumentParser(description="The launch of a blockchain.")
_parser.add_argument("--hours", help="Number of hours to simulate", type=int, default=_DEFAULT_HOURS)
_parser.add_argument("--step", help="Step length in seconds", type=int, default=_DEFAULT_STEP)
_parser.add_argument("--premium", help="Hash premium", type=float, default=_DEFAULT_PREMIUM)
_parser.add_argument("--max-reorg", help="Max. reorg block difference", type=int)

class MajorityMiners(Miners):
    
    def react(self, time,  transmission):
        if (not self.active) and isinstance(transmission, (BlockchainLaunch,)):
            self.active = True
            log("MINER {} ACTIVATING".format(self.id))
        Miners.react(self, time, transmission)

class BlockchainLaunch(Transmission):
    pass

class ReorgProtectedBlockchain(Blockchain):

    def __init__(self, 
                 id:str, 
                 genesis_block:Block, 
                 block_time: Optional[float] = 600.0, 
                 difficulty_readjustment_period: Optional[int] = 2016, 
                 initial_difficulty: Optional[float] = 600.0, 
                 max_difficulty_change_factor: Optional[int] = 4,
                 max_reorg_block_difference: Optional[int] = _DEFAULT_MAX_REORG):

        Blockchain.__init__(self, 
                            id, 
                            genesis_block, 
                            block_time,
                            difficulty_readjustment_period,
                            initial_difficulty,
                            max_difficulty_change_factor)
        self.chain_params = tuple(list([param for param in self.chain_params]) + [self.max_reorg_block_difference])


    def merge(self, other: 'Blockchain') -> bool:
        log("BLOCKCHAIN {} MERGING {}".format(self, other))

        assert other.chain_params == self.chain_params

        if other.weight < self.weight:
            log("BLOCKCHAIN {} REJECT {} AS LIGHTER CHAIN".format(self, other))
            return False

        other_block_ids = set([block_id for block_id in other.blocks.keys()])
        self_block_ids  = set([block_id for block_id in self.blocks.keys()])
        if self_block_ids.difference(other_block_ids) > self.max_reorg_block_difference:
            log("BLOCKCHAIN {} REJECT {} AS TOO DIFFERENT".format(self, other))
            return False

        log("BLOCKCHAIN {} ACCEPT {}".format(self, other))
        self.blocks = {block_id:block for (block_id, block) in other.blocks.items()}
        self.heights = [block_id for block_id in other.heights]
        self.height = other.height
        self.weight = other.weight
        self.difficulty = other.difficulty
        return True

def averaged_blockchain_launch(params, **options):
    count = options.get('count', _DEFAULT_COUNT)
    results = []
    for i in range(count):
        results.append(blockchain_launch(params, last=True, **options)[2])
    return (params[0], params[1], array(results).mean())

def blockchain_launch(params, **options):
    distance, hashrate_ratio = params
    distance = float(distance)
    hashrate_ratio = float(hashrate_ratio)
    difficulty_premium = float(options.get('difficulty_premium', _DEFAULT_PREMIUM))
    assert difficulty_premium > 0.0
    hours = float(options.get('hours', _DEFAULT_HOURS))
    assert hours > 0
    step = float(options.get('step', _DEFAULT_STEP))
    assert step > 0
    max_reorg = (int(options.get('max_reorg')) if options.get('max_reorg') else None)
    mode = options.get('mode', 'blockchain')
    last = options.get('last', False)
    
    run_id = random_string()
    reset_simulation()
    set_log_id(run_id)
    set_spatial_boundary(-1, distance + 1)

    genesis_block = Block("genesis", None, difficulty=600, height=1, time=current_time())
    minority_blockchain = _build_blockchain(max_reorg, "minority", genesis_block)
    majority_blockchain = _build_blockchain(max_reorg, "majority", genesis_block)
    minority_miners  = Miners("minority-miners", 0, minority_blockchain, initial_hashrate=1.0)
    majority_miners = MajorityMiners(
        "majority-miners", 
        distance, 
        majority_blockchain, 
        initial_hashrate=hashrate_ratio, 
        difficulty_premium=difficulty_premium, 
        active=(mode == 'miner'))

    add_agent(minority_miners)
    add_agent(majority_miners)

    if mode == 'blockchain':
        genesis_block_mined = BlockchainLaunch("genesis-mined", minority_miners, current_time())
        add_agent(genesis_block_mined)
    
    times = []
    minority_miners_minority_weight = []
    minority_miners_majority_weight = []
    majority_miners_minority_weight = []
    majority_miners_majority_weight = []
    max_time = (3600 * hours)

    while current_time() < max_time:
        advance_time(step)

        times.append(current_time())

        if minority_miners.blockchain.height > 1:
            minority_miners_minority_weight.append(sum([block.weight for block in minority_miners.blockchain.blocks.values() if minority_miners.id in block.id]))
            minority_miners_majority_weight.append(sum([block.weight for block in minority_miners.blockchain.blocks.values() if majority_miners.id in block.id]))
        else:
            minority_miners_minority_weight.append(0)
            minority_miners_majority_weight.append(0)

        if majority_miners.blockchain.height > 1:
            majority_miners_minority_weight.append(sum([block.weight for block in majority_miners.blockchain.blocks.values() if minority_miners.id in block.id]))
            majority_miners_majority_weight.append(sum([block.weight for block in majority_miners.blockchain.blocks.values() if majority_miners.id in block.id]))
        else:
            majority_miners_minority_weight.append(0)
            majority_miners_majority_weight.append(0)

    last_minority_weight_ratio = _weight_ratio(minority_miners_minority_weight[-1], minority_miners_majority_weight[-1])

    # notify("FINISHED {}: H={} D={} HR={:0.4f} Minority={:0.4f}".format(
    #     run_id,
    #     hours,
    #     int(distance),
    #     hashrate_ratio,
    #     last_minority_weight_ratio,
    # ))

    if last:
        return (distance, hashrate_ratio, last_minority_weight_ratio)
    else:
        return (
            distance,
            hashrate_ratio,
            times, 
            minority_miners_minority_weight,
            minority_miners_majority_weight,
            majority_miners_minority_weight,
            majority_miners_majority_weight,
        )

def _build_blockchain(max_reorg, name, genesis_block):
    if max_reorg is not None:
        return ReorgProtectedBlockchain(name, genesis_block, max_reorg_block_difference=max_reorg)
    else:
        return Blockchain(name, genesis_block)

def _weight_ratio(part, complement):
    return part / (part + complement)
