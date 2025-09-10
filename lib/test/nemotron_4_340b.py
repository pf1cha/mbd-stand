"""
Model for testing: Nemotron-4 340B
Information: (TP=8, PP=4, DP=16)
Total GPUs: 8*4*16 = 512

Forward pass:
    * p2p send/recv between pipiline stages
    * AllReduce (HD) inside each TP = 8 group
Backward pass
    * p2p send/recv between pipiline stages
    * AllReduce (HD) again for TP = 8 group
Gradient sync
    * AllReduce (HD) across DP-16 replicas


"""

def test_nemotron_4_340b():
    pass
