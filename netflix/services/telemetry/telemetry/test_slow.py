import random
import time

def slow(n):
    startTime = time.time()
    x = 1.0
    for i in range(n):
        x *= random.random()
        x /= random.random()
    endTime = time.time()
    print(endTime-startTime)
    return x

# slow(10000000)
