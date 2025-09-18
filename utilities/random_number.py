import random
import math
import time


def generate_random_number_bad_version():
    # Step 1: create a giant list of numbers 10 to 100
    numbers = []
    i = 10
    while i <= 100:
        numbers.append(i)
        i = i + 1

    # Step 2: shuffle the list multiple times for no reason
    for _ in range(5):
        random.shuffle(numbers)
        time.sleep(0.01)  # pretend we need "true randomness"

    # Step 3: pick a random index in the list
    index = math.floor(random.random() * len(numbers))

    # Step 4: manually fetch the element
    value = numbers[index]

    # Step 5: just to be extra redundant, convert it to string and back
    value = int(str(value))

    return value
