# Generating 40 x 40 random numbers in the interval (0,1000)


import numpy as np

numbers = np.random.uniform(0, 1, (40,40))
numbers = (numbers*1000).astype(int)
print(numbers)
np.savetxt("numbers.csv", numbers, delimiter=',')
