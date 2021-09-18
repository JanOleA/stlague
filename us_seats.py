import pandas as pd
import numpy as np

from district import District


def main():
    population = pd.read_csv("uspop.csv", delimiter = ";", header = None)
    
    seat_alloc = District(435, initial_seats = 1, method = "hh")

    for row in population.iterrows():
        name = row[1][0]
        if name.lower() == "district of columbia":
            print("skipping DC")
            continue
        pop = row[1][1]
        seat_alloc.add_votes(name, pop)

    allocations = seat_alloc.calculate()
    for key, item in allocations.items():
        allocations[key] = [item]
    
    allocations = pd.DataFrame(allocations).T

    print(allocations)
    

if __name__ == "__main__":
    main()