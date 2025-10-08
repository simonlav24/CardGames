

import random

def initialize():
    # random.seed(12346)
    pass

def shuffle(list_to_shuffle):
    random.shuffle(list_to_shuffle)

def randint(lower: int, upper: int) -> int:
    return random.randint(lower, upper)