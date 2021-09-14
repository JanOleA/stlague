import argparse
import sys
import time

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
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--displaydistricts",
                        help = "Display direct seats from all districts",
                        action = "store_true")
    parser.add_argument("-b", "--blanks",
                        help = "Display statistics of blank votes",
                        action = "store_true")
    parser.add_argument("-l", "--levelinglimit",
                        help = "The vote share required to be awarded leveling seats",
                        default = 4,
                        metavar = "VOTESHARE",
                        type = float)
    parser.add_argument("-i", "--individuals",
                        help = "Display direct seats from individual districts provided as arguments",
                        nargs = "+",
                        default = [],
                        metavar = "DISTRICTS",
                        type = str)
    args = parser.parse_args()

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

    results_2021 = pd.read_csv("2021-09-14_partydist-22-52.csv", delimiter = ";")
    party_votes_total = {}
    party_vote_shares = {}
    party_names = {}
    distribution = {}
    district_distributions = {}

    blank_votes = results_2021[results_2021["Partikode"] == "BLANKE"][["Fylkenavn", "Antall stemmer totalt"]]
    num_possible_voters = results_2021[results_2021["Partikode"] == "BLANKE"]["Antall stemmeberettigede"]
    percent_blanks = blank_votes["Antall stemmer totalt"]/num_possible_voters*100
    blank_votes["% av stemmeberettigede"] = percent_blanks
    number_of_blanks = blank_votes["Antall stemmer totalt"].sum(axis = 0)
    if args.blanks:
        print("\n" + "#"*30)
        print(f"Blanke stemmer:")
        print("-"*30)
        print(blank_votes.sort_values(by = "Antall stemmer totalt", ascending = False))
        print("Total:", number_of_blanks)
        print("")

    start = time.perf_counter()
    print("Calculating main distribution... [running]  ", end = "\r")
    districts = results_2021.Fylkenavn.unique()
    for district_name in districts:
        results_dis = results_2021[results_2021["Fylkenavn"] == district_name]
        district_id = int(results_dis.Fylkenummer.unique())
        parties = list(results_dis.Partikode.unique())

        electoral_district = District(seats_no_leveling[district_id])

        for party in parties:
            results_party = results_dis[results_dis["Partikode"] == party]
            party_name = results_party.Partinavn.unique()
            assert len(party_name) == 1 # check that only one party name belongs to the party code
            party_names[party] = party_name[0]
            votes = np.sum(results_party["Antall stemmer totalt"])

            if party in party_votes_total:
                party_votes_total[party] += votes
            else:
                party_votes_total[party] = votes

            if party == "BLANKE":
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
    print(f"Calculating main distribution... [Completed in: {time.perf_counter() - start:>7.5f}s]  ")

    start = time.perf_counter()
    print("Calculating leveling seats... [running]  ", end = "\r")
    leveling_seats = 169
    leveling_seats_limit = args.levelinglimit

    parties_competing_votes = {}

    total_votes = np.sum(results_2021["Antall stemmer totalt"])
    for party, votes in party_votes_total.items():
        if party == "BLANKE":
            continue
        if party in distribution:
            seats = distribution[party]
        else:
            seats = 0
        party_percent_of_total = party_votes_total[party]/(total_votes - number_of_blanks)*100
        party_vote_shares[party] = np.round(party_percent_of_total, 2)
    
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
        distribution_with_leveling[party] = [seats, diff, party_vote_shares[party]]

    for party, seats in leveling_distribution.items():
        if not party in distribution:
            seats = leveling_distribution[party]
            distribution_with_leveling[party] = [seats, seats, party_vote_shares[party]]

    print(f"Calculating leveling seats... [Completed in: {time.perf_counter() - start:>7.5f}s]  ")
    print("")

    display_dict = {} # create a new dict where the party codes are replaced with party names for pretty printing
    for party, seats in distribution_with_leveling.items():
        display_dict[party_names[party]] = seats

    distribution_table = pd.DataFrame(display_dict).T
    distribution_table.columns = ["Mandater", "Utjevningsmandater", "% Stemmer"]
    distribution_table = distribution_table.sort_values("Mandater", axis = 0, ascending = False)
    print(f"Grense for utjevningsmandater = {leveling_seats_limit}%")
    print(distribution_table)

    seat_sums = distribution_table.sum(axis = 0)
    assert seat_sums["Mandater"] == 169

    individuals_lowered = [x.lower() for x in args.individuals]

    if args.displaydistricts or args.individuals:
        for district, dist_distribution in district_distributions.items():
            if args.individuals and district.lower() not in individuals_lowered:
                passing = False
                for individual in individuals_lowered:
                    if individual in district.lower():
                        passing = True
                if not passing:
                    continue
            print("\n" + "#"*50)
            print(f"Direct seats from {district}")
            print("-"*50)
            for party, seats in dist_distribution.items():
                if seats == 0:
                    continue
                print(f"{party_names[party]:>35s} {seats:>3d}")


if __name__ == "__main__":
    main()