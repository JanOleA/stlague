import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class District:
    def __init__(self, seats, initial_divisor = 1.4):
        self._seats = seats
        self._initial_divisor = initial_divisor
        self._votes = []
        self._names = []

    def add_votes(self, name, result):
        if name in self._names:
            print("Party already added, can't be added again. Use `edit_votes()`")
            return
        self._votes.append(result)
        self._names.append(name)

    def edit_votes(self, name, result):
        idx = self._names.index(name)
        self._votes[idx] = result

    def remove_party(self, name):
        idx = self._names.index(name)
        self._votes.pop(idx)
        self._names.pop(idx)

    def calculate(self):
        num_parties = len(self._votes)
        awarded_seats = np.zeros(num_parties, dtype = np.int)
        votes_array = np.array(self._votes)
        divisor_array = np.full(num_parties, self._initial_divisor)
        score_history = []

        while np.sum(awarded_seats) < self._seats:
            scores = votes_array/divisor_array
            score_history.append(scores)
            next_seat = np.argmax(scores)
            awarded_seats[next_seat] += 1
            divisor_array[next_seat] = awarded_seats[next_seat]*2 + 1

        final_results = {}

        for name, seats in zip(self._names, awarded_seats):
            final_results[name] = seats

        return final_results

    @property
    def seats(self):
        return self._seats

    @seats.setter
    def seats(self, val):
        self._seats = val


def main():
    # Seat distribution per district id number
    total_seats = {1: 9,    # Østfold
                   2: 19,   # Akershus
                   3: 20,   # Oslo
                   4: 7,    # Hedmark    
                   5: 6,    # Oppland
                   6: 8,    # Buskerud    
                   7: 7,    # Vestfold
                   8: 6,    # Telemark
                   9: 4,    # Aust-Agder
                   10: 6,   # Vest-Agder
                   11: 14,  # Rogaland
                   12: 16,  # Hordaland
                   14: 4,   # Sogn og Fjordane
                   15: 8,   # Møre og Romsdal
                   16: 10,  # Sør-Trøndelag
                   17: 5,   # Nord-Trøndelag
                   18: 9,   # Nordland
                   19: 6,   # Troms Romsa
                   20: 5}   # Finnmark Finnmárku
    
    # Seat distribution without leveling seats (each district has one less)
    seats_no_leveling = {}
    s = 0 # check that the total is 169 as well
    for key, item in total_seats.items():
        s += item
        seats_no_leveling[key] = item - 1
    assert s == 169

    results_2021 = pd.read_csv("2021-09-14_partydist.csv", delimiter = ";")
    party_votes_total = {}
    distribution = {}
    district_distributions = {}

    districts = results_2021.Fylkenavn.unique()
    for district_name in districts:
        results_dis = results_2021[results_2021["Fylkenavn"] == district_name]
        district_id = int(results_dis.Fylkenummer.unique())
        parties = list(results_dis.Partinavn.unique())

        electoral_district = District(seats_no_leveling[district_id])

        for party in parties:
            results_party = results_dis[results_dis["Partinavn"] == party]
            votes = np.sum(results_party["Antall stemmer totalt"])

            if party in party_votes_total:
                party_votes_total[party] += votes
            else:
                party_votes_total[party] = votes

            if party == "Blanke":
                continue
            electoral_district.add_votes(party, votes)

        district_distribution = electoral_district.calculate()
        district_distributions[district_name] = district_distribution

        for party, seats in district_distribution.items():
            if not seats:
                continue
            if party in distribution:
                distribution[party] += seats
            else:
                distribution[party] = seats

    leveling_seats = 169
    if len(sys.argv) > 1:
        try:
            leveling_seats_limit = float(sys.argv[1])
        except ValueError:
            leveling_seats_limit = 4
    else:
        leveling_seats_limit = 4

    parties_competing_votes = {}

    total_votes = np.sum(results_2021["Antall stemmer totalt"])
    for party, votes in party_votes_total.items():
        if party == "Blanke":
            continue
        if party in distribution:
            seats = distribution[party]
        else:
            seats = 0
        party_percent_of_total = party_votes_total[party]/total_votes*100
    
        if party_percent_of_total < leveling_seats_limit:
            leveling_seats -= seats
        else:
            parties_competing_votes[party] = votes

    # initial distribution before removing overrepresented parties
    leveling_district = District(leveling_seats)
    for party, votes in parties_competing_votes.items():
        leveling_district.add_votes(party, votes)

    leveling_distribution = leveling_district.calculate()

    parties_over = None
    while parties_over or parties_over is None:
        parties_over = [] # append parties to the list as we go

        for party, level_seats in leveling_distribution.items():
            if party in distribution:
                district_seats = distribution[party]
            else:
                district_seats = 0
            if district_seats >= level_seats: # party is overrepresented (or level)
                parties_over.append(party)
                leveling_district.remove_party(party)
                leveling_district.seats = leveling_district.seats - district_seats # remove this party's allocated seats from the calculation

        leveling_distribution = leveling_district.calculate()

    distribution_with_leveling = {}

    for party, seats in distribution.items():
        if party in leveling_distribution:
            seats_before = seats
            seats = leveling_distribution[party]
            diff = seats - seats_before
        else:
            diff = 0
        distribution_with_leveling[party] = [seats, diff]

    for party, seats in leveling_distribution.items():
        if not party in distribution:
            seats = leveling_distribution[party]
            distribution_with_leveling[party] = [seats, seats]

    distribution_table = pd.DataFrame(distribution_with_leveling).T
    distribution_table.columns = ["Mandater", "Utjevningsmandater"]
    distribution_table = distribution_table.sort_values("Mandater", axis = 0, ascending = False)
    print(f"Grense for utjevningsmandater = {leveling_seats_limit}%")
    print(distribution_table)

    print(distribution_table.sum(axis = 0))


if __name__ == "__main__":
    main()