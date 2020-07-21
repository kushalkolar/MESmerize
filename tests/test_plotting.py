import numpy as np

a = b = np.random.rand(5,1)

def random(x,y):
    return (x*y)

value = random(a,b)

def test_random(x,y):
    assert random(a,b) == value