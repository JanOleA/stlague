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
        if len(self._votes) == 0:
            return {}
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
    parser.add_argument("-a", "--analyze",
                        help = "Run various analyses on the election results",
                        action = "store_true")
    parser.add_argument("-p", "--plot",
                        help = "Display a plot of the parliament",
                        action = "store_true")
    parser.add_argument("-s", "--startdivisor",
                        help = "Set the initial divisor (default 1.4)",
                        default = 1.4,
                        type = float)
    parser.add_argument("-t", "--title",
                        help = "Title for the plots (default is no title)",
                        default = "",
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

    results_2021 = pd.read_csv("2021-09-17_partydist.csv", delimiter = ";")
    all_parties = results_2021.Partikode.unique()
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

    total_votes = np.sum(results_2021["Antall stemmer totalt"])

    start = time.perf_counter()
    print("Calculating main distribution... [running]  ", end = "\r")
    districts = results_2021.Fylkenavn.unique()
    for district_name in districts:
        results_dis = results_2021[results_2021["Fylkenavn"] == district_name]
        district_id = int(results_dis.Fylkenummer.unique())
        parties = list(results_dis.Partikode.unique())

        electoral_district = District(seats_no_leveling[district_id], initial_divisor = args.startdivisor)

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
        
        """
        # this block stops parties with less than the leveling limit from gaining any seats at all (even direct district seats)
        for party in parties:
            if party == "BLANKE":
                continue
            party_votes_total_this = results_2021[results_2021["Partikode"] == party]
            party_votes_total_this = party_votes_total_this.sum()
            if party_votes_total_this["Antall stemmer totalt"]/(total_votes - number_of_blanks)*100 < args.levelinglimit:
                electoral_district.remove_party(party)
        """

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
        votes_for_leveling = np.ceil(((leveling_seats_limit/100)*(total_votes - number_of_blanks) - party_votes_total[party])/(1 - leveling_seats_limit/100)) # votes required for the party to gain leveling seats
        distribution_with_leveling[party] = [seats, diff, party_vote_shares[party], party_votes_total[party], votes_for_leveling]

    for party, seats in leveling_distribution.items():
        if not party in distribution:
            seats = leveling_distribution[party]
            votes_for_leveling = np.ceil(((leveling_seats_limit/100)*(total_votes - number_of_blanks) - party_votes_total[party])/(1 - leveling_seats_limit/100)) # votes required for the party to gain leveling seats
            distribution_with_leveling[party] = [seats, seats, party_vote_shares[party], party_votes_total[party], votes_for_leveling]

    print(f"Calculating leveling seats... [Completed in: {time.perf_counter() - start:>7.5f}s]  ")
    print("Calculating districts for leveling seats... [running]  ", end = "\r")
    start = time.perf_counter()
    leveling_table = []
    for district_name in districts:
        results_dis = results_2021[results_2021["Fylkenavn"] == district_name]
        district_votes_total = results_dis["Antall stemmer totalt"].sum()
        district_votes_total -= results_dis[results_dis["Partikode"] == "BLANKE"]["Antall stemmer totalt"].sum()
        district_id = int(results_dis.Fylkenummer.unique())
        district_divisor = district_votes_total/seats_no_leveling[district_id]
        for party, level_seats in leveling_distribution.items():
            party_district_votes = results_dis[results_dis["Partikode"] == party]
            party_district_votes = np.sum(party_district_votes["Antall stemmer totalt"])
            if party in district_distributions[district_name]:
                direct_seats_in_district = district_distributions[district_name][party]
            else:
                direct_seats_in_district = 0
            divisor = direct_seats_in_district*2 + 1
            rest_quotient = (party_district_votes/divisor)/district_divisor
            leveling_table.append([rest_quotient, district_name, party])
    leveling_table = pd.DataFrame(leveling_table)
    leveling_table.columns = ["Restkvotient", "Fylke", "Partikode"]
    leveling_table = leveling_table.sort_values(by = "Restkvotient", ascending = False)

    parties_awarded = {}
    leveling_awards = {}

    print("")
    for line in leveling_table.iterrows():
        district = line[1]["Fylke"]
        party = line[1]["Partikode"]
        if party in distribution:
            seats_to_award = leveling_distribution[party] - distribution[party]
        else:
            seats_to_award = leveling_distribution[party]
        #print(party, seats_to_award)
        if district in leveling_awards:
            continue
        if party in parties_awarded:
            if parties_awarded[party] >= seats_to_award:
                continue
        else:
            parties_awarded[party] = 0
        leveling_awards[district] = party
        parties_awarded[party] += 1

    for district, party in leveling_awards.items():
        if party in district_distributions[district]:
            district_distributions[district][party] += 1
        else:
            district_distributions[district][party] = 1

    print(f"Calculating districts for leveling seats... [Completed in: {time.perf_counter() - start:>7.5f}s]  ")

    print("")
    print(f"Antall stemmer totalt: {total_votes-number_of_blanks}")

    display_dict = {} # create a new dict where the party codes are replaced with party names for pretty printing
    for party, seats in distribution_with_leveling.items():
        display_dict[party_names[party]] = seats

    distribution_table = pd.DataFrame(display_dict).T
    distribution_table.columns = ["Mandater", "Utjevningsmandater", "% Stemmer", "Antall stemmer", f"Stemmer til {leveling_seats_limit}%"]
    distribution_table = distribution_table.sort_values("Mandater", axis = 0, ascending = False)
    print(f"Grense for utjevningsmandater = {leveling_seats_limit}%  |  Første delingstall: {args.startdivisor}")
    print(distribution_table)

    seat_sums = distribution_table.sum(axis = 0)
    assert seat_sums["Mandater"] == 169, f"Sum of seats should be 169, not {seat_sums['Mandater']}"

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
            print(f"Mandater fra {district}")
            print("-"*50)
            for party, seats in dist_distribution.items():
                if seats == 0:
                    continue
                print(f"{party_names[party]:>35s} {seats:>3d}")

    if args.analyze:
        smalldists_results_2021 = pd.read_csv("2021-09-15_partydist_smalldistricts.csv", delimiter = ";")
        # Benford's law analysis
        leading_digits = []
        for line in smalldists_results_2021.iterrows():
            value = line[1]["Antall stemmer totalt"]
            if value > 0:
                first_digit = str(value)[0]
                leading_digits.append(int(first_digit))

        plt.hist(leading_digits, bins = range(1,11))
        plt.xticks([1, 2, 3, 4, 5, 6, 7, 8, 9])
        plt.xlabel("Ledende siffer ")
        plt.ylabel("Antall tilfeller")
        plt.title("Ledende siffer for antall stemmer ved alle valgkretser i Norge")
        plt.show()

    if args.plot:
        parties_left_to_right = {"RØDT": "#800000",
                                 "SV":   "#ff7dfb",
                                 "A":    "#ff0000",
                                 "SP":   "#93c77d",
                                 "MDG":  "#129600",
                                 "PP":   "#386782",
                                 "PS":   "#b3321c",
                                 "KRF":  "#d9ff00",
                                 "PF":   "#828282",
                                 "INP":  "#ffb300",
                                 "V":    "#00ffe1",
                                 "H":    "#0084ff",
                                 "FRP":  "#0038b0",
                                 "DEMN": "#7211b0",}

        parties_actual_distri = {"RØDT": 8,
                                 "SV":   13,
                                 "A":    48,
                                 "SP":   28,
                                 "MDG":  3,
                                 "KRF":  3,
                                 "PF":   1,
                                 "V":    8,
                                 "H":    36,
                                 "FRP":  21}
                                 
        plt.figure(figsize = (12,3.2))
        if args.title == "":
            args.title = f"Sperregrense: {args.levelinglimit}% | Første delingstall: {args.startdivisor}"
        plt.title(args.title)
        plt.axis("off")
        plt.tight_layout()
        plt.ylim((-6.5, 1))
        plt.xlim((-2, 32))
        i = 0
        while i < 169:
            for party, color in parties_left_to_right.items():
                if not party in distribution_with_leveling:
                    continue
                seats = distribution_with_leveling[party][0]
                for seat in range(seats):
                    if i < 84:
                        col = i//6
                        row = i%6
                    elif i == 84:
                        col = 13.8
                        row = 2.5
                    else:
                        col = (i-1)//6 + 0.6
                        row = (i-1)%6

                    if seat == 0:
                        label = party
                    else:
                        label = None

                    plt.plot([col], [-row], marker = "s", color = "#000000", markersize = 11)
                    plt.plot([col], [-row], marker = "s", color = color, markersize = 10, label = label)
                    i += 1

        plt.legend()

        plt.figure()
        plt.title(args.title)
        plt.axis("off")
        plt.tight_layout()

        row = 0
        for party, color in parties_left_to_right.items():
            if not party in distribution_with_leveling:
                continue
            partyname = party_names[party]
            seats = distribution_with_leveling[party][0]
            if party in parties_actual_distri:
                actual = parties_actual_distri[party]
            else:
                actual = 0
            diff = seats - actual
            if diff > 0:
                marker = "↑"
            elif diff < 0:
                marker = "↓"
            else:
                marker = "→"
            plt.plot([0], [-row], marker = "s", color = "#000000", markersize = 11)
            plt.plot([0], [-row], marker = "s", color = color, markersize = 10)
            plt.text(0, -row - 0.1, f"{partyname:>33s}, {seats:>3d}  {marker} {abs(diff)}", fontfamily = "Cascadia Mono")
            row += 1

        plt.xlim(-0.2, 0.7)

        locations = {"Østfold":            [0.8, -0.8],
                     "Akershus":           [0.85, 1.1],
                     "Oslo":               [0, 0],
                     "Hedmark":            [0.6, 2.3],
                     "Oppland":            [-1.8, 1.7],
                     "Buskerud":           [-1.75, 0.6],
                     "Vestfold":           [-0.7, -0.8],
                     "Telemark":           [-2.9, -0.4],
                     "Aust-Agder":         [-2, -1.6],
                     "Vest-Agder":         [-3.2, -1.8],
                     "Rogaland":           [-4.3, -1.5],
                     "Hordaland":          [-4.6, 0],
                     "Sogn og Fjordane":   [-4.91, 1.43],
                     "Møre og Romsdal":    [-3.58, 2.6],
                     "Sør-Trøndelag":      [-1.3, 3],
                     "Nord-Trøndelag":     [0, 4],
                     "Nordland":           [1, 5.5],
                     "Troms Romsa":        [3, 6.7],
                     "Finnmark Finnmárku": [6, 7],}

        plt.figure(figsize = (14,9))
        plt.title(args.title)
        plt.tight_layout()
        row_sizes = np.array([1, 6, 12, 24])
        row_sizes_cum = np.cumsum(row_sizes)

        parties_in_legend = []

        for district_name, location in locations.items():
            leveling_awarded = False
            results_dis = results_2021[results_2021["Fylkenavn"] == district_name] 
            district_id = int(results_dis.Fylkenummer.unique())
            district_seats = total_seats[district_id]

            district_distribution = district_distributions[district_name]

            if district_name == "Oslo" or district_name == "Akershus":
                plt.text(location[0] + 0.45, location[1] + 0.25, district_name, fontfamily = "Cascadia Code")
            elif district_name == "Hordaland" or district_name == "Rogaland":
                plt.text(location[0] -1.5, location[1] + 0.25, district_name, fontfamily = "Cascadia Code")
            elif district_name == "Sør-Trøndelag" or district_name == "Nordland":
                plt.text(location[0] + 0.5, location[1] + 0.25, district_name, fontfamily = "Cascadia Code")
            elif district_name == "Sogn og Fjordane":
                plt.text(location[0] -1.6, location[1] + 0.35, district_name, fontfamily = "Cascadia Code")
            elif district_name == "Møre og Romsdal":
                plt.text(location[0] -1.7, location[1] + 0.35, district_name, fontfamily = "Cascadia Code")
            elif district_name == "Vest-Agder":
                plt.text(location[0] + 0.1, location[1] - 0.35, district_name, fontfamily = "Cascadia Code")
            elif district_name == "Østfold":
                plt.text(location[0] + 0.4, location[1] + 0.35, district_name, fontfamily = "Cascadia Code")
            elif district_name == "Vestfold":
                plt.text(location[0] + 0.05, location[1] - 0.45, district_name, fontfamily = "Cascadia Code")
            elif district_name == "Aust-Agder":
                plt.text(location[0] - 0.4, location[1] + 0.35, district_name, fontfamily = "Cascadia Code")
            else:
                plt.text(location[0] + 0.2, location[1] + 0.2, district_name, fontfamily = "Cascadia Code")

            seats_plotted = 0
            prev_row = 0
            position = 0
            for party, seats in district_distribution.items():
                for seat in range(seats):
                    row = np.argmax(row_sizes_cum > seats_plotted)
                    if row != prev_row:
                        position = 0
                        prev_row = row

                    if row % 2 == 0:
                        marker = "h"
                    else:
                        marker = "h"

                    rowsize = row_sizes[row]
                    angle_diff = 2*np.pi/(rowsize)

                    radius = row*0.19
                    if party in parties_in_legend:
                        label = None
                    else:
                        label = party_names[party]
                        parties_in_legend.append(party)
                    x = np.cos(position*angle_diff)*radius + location[0]
                    y = np.sin(position*angle_diff)*radius + location[1]
                    if leveling_awards[district_name] == party and not leveling_awarded:
                        plt.plot(x, y, marker = marker, markersize = 12, color = "black")
                        plt.plot(x, y, marker = marker, markersize = 10, color = "gold")
                        leveling_awarded = True
                    plt.plot(x, y, marker = marker, markersize = 7.5, color = "black")
                    plt.plot(x, y, marker = marker, markersize = 7, color = parties_left_to_right[party], label = label)

                    position += 1
                    seats_plotted += 1            
        plt.axis("equal")
        plt.axis("off")
        plt.legend()
        plt.show()


if __name__ == "__main__":
    main()