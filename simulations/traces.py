from .blockchain_launch import blockchain_launch


def traces(params, **options):
    return blockchain_launch(
        params,
        mode='blockchain',
        last=True, 
        **options)
