from .blockchain_launch import blockchain_launch

def single_launch_history(params, **options):
    return blockchain_launch(
        params,
        mode='blockchain',
        last=False,
        **options)
