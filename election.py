import argparse
import os
import time

import matplotlib.pyplot as plt
import numpy as np
from numpy.lib.type_check import nan_to_num
import pandas as pd

from district import District


class Norway:
    def __init__(self, args, filename = "2021-09-17_partydist.csv", num_leveling_seats = 1):
        self._active_message = False
        self.args = args
        self.results = pd.read_csv(filename, delimiter = ";")
        self.total_votes = np.sum(self.results["Antall stemmer totalt"])

        populations = {"Østfold":            299447,
                       "Akershus":           675240,
                       "Oslo":               693494,
                       "Hedmark":            197920,
                       "Oppland":            173465,
                       "Buskerud":           266478,
                       "Vestfold":           246041,
                       "Telemark":           173355,
                       "Aust-Agder":         118273,
                       "Vest-Agder":         188958,
                       "Rogaland":           479892,
                       "Hordaland":          528127,
                       "Sogn og Fjordane":   108404,
                       "Møre og Romsdal":    265238,
                       "Sør-Trøndelag":      334514,
                       "Nord-Trøndelag":     134188,
                       "Nordland":           241235,
                       "Troms Romsa":        167839,
                       "Finnmark Finnmárku": 75472}
    
        dist_areas = {"Østfold":            4004,
                      "Akershus":           5669,
                      "Oslo":               454,
                      "Hedmark":            27398,
                      "Oppland":            24675,
                      "Buskerud":           14920,
                      "Vestfold":           2168,
                      "Telemark":           15298,
                      "Aust-Agder":         9155,
                      "Vest-Agder":         7278,
                      "Rogaland":           9377,
                      "Hordaland":          15438,
                      "Sogn og Fjordane":   18433,
                      "Møre og Romsdal":    14356,
                      "Sør-Trøndelag":      20257,
                      "Nord-Trøndelag":     21944,
                      "Nordland":           38155,
                      "Troms Romsa":        26198,
                      "Finnmark Finnmárku": 48631}
    
        district_id_by_name =   {"Østfold": 1,
                                 "Akershus": 2,
                                 "Oslo": 3,
                                 "Hedmark": 4,
                                 "Oppland": 5,
                                 "Buskerud": 6,
                                 "Vestfold": 7,
                                 "Telemark": 8,
                                 "Aust-Agder": 9,
                                 "Vest-Agder": 10,
                                 "Rogaland": 11,
                                 "Hordaland": 12,
                                 "Sogn og Fjordane": 14,
                                 "Møre og Romsdal": 15,
                                 "Sør-Trøndelag": 16,
                                 "Nord-Trøndelag": 17,
                                 "Nordland": 18,
                                 "Troms Romsa": 19,
                                 "Finnmark Finnmárku": 20}

        district_name_by_id = {}
        for name, dist_id in district_id_by_name.items():
            district_name_by_id[dist_id] = name
    
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

        # define parties on a left to right scale, and give them a color
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

        all_parties = self.results.Partikode.unique()
        for party in all_parties:
            if party not in parties_left_to_right:
                parties_left_to_right[party] = "#424242"

        # actual results from the real election
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

        self.district_name_by_id = district_name_by_id
        self.district_id_by_name = district_id_by_name
        self.populations = populations
        self.dist_areas = dist_areas
        self.locations = locations
        self.parties_left_to_right = parties_left_to_right
        self.parties_actual_distri = parties_actual_distri
        self.num_leveling_seats = num_leveling_seats
        self.add_votes_dict = {}
        self.transfer_votes_dict = {}

    def add_votes(self, district, party, votes):
        if not district in self.populations:
            print(f"Attempted to add votes in district {district}, but it doesn't exist.")
        if district in self.add_votes_dict:
            parties_dict = self.add_votes_dict[district]
            parties_dict[party] = votes
        else:
            parties_dict = {party: votes}

        self.add_votes_dict[district] = parties_dict

    def transfer_votes(self, from_party, to_party):
        self.transfer_votes_dict[from_party] = to_party

    def _calculate_seat_distribution(self):
        if self.args.usadist:
            seat_distribution = District(169 - 2*len(self.populations.items()),
                                         method = "hunthill", initial_seats = 1)
        else:
            seat_distribution = District(169, initial_divisor = 1)

        for district_name, population in self.populations.items():
            area = self.dist_areas[district_name]
    
            score = area*self.args.areamultiplier + population
            seat_distribution.add_votes(district_name, score)
    
        # Seat distribution per district name
        self.total_seats = seat_distribution.calculate()

        if self.args.usadist:
            for district_name, seats in self.total_seats.items():
                self.total_seats[district_name] = seats + 2

        self.seats_without_leveling = {}
        s = 0 # check that the total is 169 as well
        for key, item in self.total_seats.items():
            s += item
            self.seats_without_leveling[key] = item - self.num_leveling_seats
        assert s == 169 # check that the total is 169 as well

    def _calculate_direct_seats(self, method = "stlague"):
        results = self.results
        total_seats = self.total_seats
        seats_without_leveling = self.seats_without_leveling

        party_votes_total = {}
        party_names = {}
        party_ids = {}
        distribution = {}
        district_distributions = {}
        district_votes_distributions = {}
        votes_per_seat = {}

        electoral_districts = results.Fylkenavn.unique()
        for district_name in electoral_districts:
            results_dis = results[results["Fylkenavn"] == district_name]
            parties = list(results_dis.Partikode.unique())
            total_votes_dis = np.sum(results_dis["Antall stemmer totalt"])
            votes_per_seat[district_name] = [district_name,
                                             np.round(total_votes_dis/total_seats[district_name], 1)]

            electoral_district = District(seats_without_leveling[district_name],
                                          initial_divisor = self.args.initialdivisor,
                                          method = method)

            district_votes_distribution = {}

            for party in parties:
                results_party = results_dis[results_dis["Partikode"] == party]
                party_name = results_party.Partinavn.unique()
                assert len(party_name) == 1 # check that only one party name belongs to the party code
                party_names[party] = party_name[0]
                party_ids[party_name[0]] = party
                votes = np.sum(results_party["Antall stemmer totalt"])
                if district_name in self.add_votes_dict:
                    if party in self.add_votes_dict[district_name]:
                        votes_add = self.add_votes_dict[district_name][party]
                        votes += votes_add
                        self.total_votes += votes_add

                if party in self.transfer_votes_dict:
                    party = self.transfer_votes_dict[party]

                if party in party_votes_total:
                    party_votes_total[party] += votes
                else:
                    party_votes_total[party] = votes

                if party == "BLANKE":
                    continue
                electoral_district.add_votes(party, votes)
                district_votes_distribution[party] = votes

            if self.args.hardlimit:
                # stop parties with less than the leveling limit from gaining any seats at all (even direct district seats)
                for party in parties:
                    if party == "BLANKE":
                        continue
                    party_votes_total_this = results[results["Partikode"] == party]
                    party_votes_total_this = party_votes_total_this.sum()
                    if party_votes_total_this["Antall stemmer totalt"]/(self.total_votes
                                                                        - self.number_of_blanks)*100 < self.args.levelinglimit:
                        electoral_district.remove_party(party)

            district_distribution = electoral_district.calculate()
            district_distributions[district_name] = district_distribution
            district_votes_distributions[district_name] = district_votes_distribution

            for party, seats in district_distribution.items():
                if not seats:
                    continue
                if party in distribution:
                    distribution[party] += seats
                else:
                    distribution[party] = seats

        self.party_votes_total = party_votes_total
        self.party_names = party_names
        self.party_ids = party_ids
        self.distribution = distribution
        self.district_distributions = district_distributions
        self.district_votes_ditributions = district_votes_distributions
        self.district_votes_distributions_table = pd.DataFrame(district_votes_distributions).fillna(0)
        self.votes_per_seat = votes_per_seat
        self.electoral_districts = electoral_districts

    def _calculate_leveling_seats_parties(self):
        party_vote_shares = {}

        leveling_seats = 169
        leveling_seats_limit = self.args.levelinglimit

        parties_competing_votes = {}

        for party, votes in self.party_votes_total.items():
            if party == "BLANKE":
                continue
            if party in self.distribution:
                seats = self.distribution[party]
            else:
                seats = 0
            party_percent_of_total = self.party_votes_total[party]/(self.total_votes - self.number_of_blanks)*100
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
                if party in self.distribution:
                    district_seats = self.distribution[party]
                else:
                    district_seats = 0
                if district_seats >= level_seats: # party is overrepresented (or level)
                    parties_over.append(party)
                    leveling_district.remove_party(party)
                    leveling_district.seats = leveling_district.seats - district_seats # remove this party's allocated seats from the calculation

            leveling_distribution = leveling_district.calculate()

        distribution_with_leveling = {}

        for party, seats in self.distribution.items():
            if party in leveling_distribution:
                seats_before = seats
                seats = leveling_distribution[party]
                diff = seats - seats_before
            else:
                diff = 0
            votes_for_leveling = np.ceil(((leveling_seats_limit/100)*(self.total_votes - self.number_of_blanks) - self.party_votes_total[party])/(1 - leveling_seats_limit/100)) # votes required for the party to gain leveling seats
            distribution_with_leveling[party] = [seats, diff, party_vote_shares[party], self.party_votes_total[party], votes_for_leveling]

        for party, seats in leveling_distribution.items():
            if not party in self.distribution:
                seats = leveling_distribution[party]
                votes_for_leveling = np.ceil(((leveling_seats_limit/100)*(self.total_votes - self.number_of_blanks) - self.party_votes_total[party])/(1 - leveling_seats_limit/100)) # votes required for the party to gain leveling seats
                distribution_with_leveling[party] = [seats, seats, party_vote_shares[party], self.party_votes_total[party], votes_for_leveling]

        self.leveling_distribution = leveling_distribution # just the distribution for the leveling seats
        self.distribution_with_leveling = distribution_with_leveling # full distribution of seats, including leveling seats
        self.party_vote_shares = party_vote_shares

    def _calculate_leveling_seats_districts(self):
        leveling_table = []
        electoral_districts = self.electoral_districts
        seats_without_leveling = self.seats_without_leveling
        leveling_distribution = self.leveling_distribution
        district_distributions = self.district_distributions
        distribution = self.distribution
        results = self.results

        for district_name in electoral_districts:
            results_dis = results[results["Fylkenavn"] == district_name]
            district_votes_total = results_dis["Antall stemmer totalt"].sum()
            district_votes_total -= results_dis[results_dis["Partikode"] == "BLANKE"]["Antall stemmer totalt"].sum()
            district_divisor = district_votes_total/seats_without_leveling[district_name]
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
        if len(leveling_table) > 0:
            leveling_table.columns = ["Restkvotient", "Fylke", "Partikode"]
            leveling_table = leveling_table.sort_values(by = "Restkvotient", ascending = False)

        parties_awarded = {}
        leveling_awards = {}

        for line in leveling_table.iterrows():
            district = line[1]["Fylke"]
            party = line[1]["Partikode"]
            if party in distribution:
                seats_to_award = leveling_distribution[party] - distribution[party]
            else:
                seats_to_award = leveling_distribution[party]
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

        self.district_distributions = district_distributions
        self.leveling_awards = leveling_awards

    def _calculate_blanks(self):
        results = self.results
        blank_votes = results[results["Partikode"] == "BLANKE"][["Fylkenavn", "Antall stemmer totalt"]]
        num_possible_voters = results[results["Partikode"] == "BLANKE"]["Antall stemmeberettigede"]
        percent_blanks = blank_votes["Antall stemmer totalt"]/num_possible_voters*100
        blank_votes["% av stemmeberettigede"] = percent_blanks
        self.number_of_blanks = blank_votes["Antall stemmer totalt"].sum(axis = 0)
        self.total_minus_blanks = self.total_votes - self.number_of_blanks
        self.blank_votes = blank_votes

    def calculate(self, dist_method = "stlague"):
        self._calculate_seat_distribution()
        self._calculate_blanks()
        self._message_start("Beregner direktedistribusjon av mandater")
        self._calculate_direct_seats(method = dist_method)
        self._message_start("Beregner hvilke partier som får utjevningsmandater")
        self._calculate_leveling_seats_parties()
        self._message_start("Beregner hvilke valgdistrikt som får utjevningsmandater")
        self._calculate_leveling_seats_districts()
        self._message_end()
        self._make_votes_per_seat_table()
        self._make_distribution_table()

    def _message_start(self, message):
        if self._active_message:
            self._message_end()
        self._start_time = time.perf_counter()
        self._message = message
        self._active_message = True
        print(f"{message:60s}  [kjører]  ", end = "\r")

    def _message_end(self):
        print(f"{self._message:60s}  [  ok  ]  ({time.perf_counter() - self._start_time:>7.5f}s)  ")
        self._active_message = False

    def _make_distribution_table(self):
        display_dict = {}
        for party, seats in self.distribution_with_leveling.items():
            display_dict[self.party_names[party]] = seats

        distribution_table = pd.DataFrame(display_dict).T
        distribution_table.columns = ["Mandater", "Utjevningsmandater", "% Stemmer", "Antall stemmer", f"Stemmer til {self.args.levelinglimit}%"]
        distribution_table = distribution_table.sort_values("Mandater", axis = 0, ascending = False)

        seat_sums = distribution_table.sum(axis = 0)
        assert seat_sums["Mandater"] == 169, f"Sum of seats should be 169, not {seat_sums['Mandater']}"

        self.distribution_table = distribution_table

    def _make_votes_per_seat_table(self):
        votes_per_seat = pd.DataFrame(self.votes_per_seat).T
        votes_per_seat.columns = ["Valgdistrikt", "Antall stemmer per mandat"]
        self.votes_per_seat = votes_per_seat

    def analyze(self):
        smalldists_results_2021 = pd.read_csv("2021-09-15_partydist_smalldistricts.csv", delimiter = ";")
        # Benford's law analysis
        leading_digits = []
        for line in smalldists_results_2021.iterrows():
            value = line[1]["Antall stemmer totalt"]
            if value > 0:
                first_digit = str(value)[0]
                leading_digits.append(int(first_digit))

        plt.figure()
        plt.hist(leading_digits, bins = range(1,11))
        plt.xticks([1, 2, 3, 4, 5, 6, 7, 8, 9])
        plt.xlabel("Ledende siffer ")
        plt.ylabel("Antall tilfeller")
        plt.title("Ledende siffer for antall stemmer ved alle valgkretser i Norge")
        plt.show()

    def show_individual_districts(self):
        individuals_lowered = [x.lower() for x in self.args.individuals]

        for district, dist_distribution in self.district_distributions.items():
            if self.args.individuals and district.lower() not in individuals_lowered:
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
                print(f"{self.party_names[party]:>35s} {seats:>3d}")
            print(f"\nStemmer i {district}")
            district_votes = self.district_votes_distributions_table[district]
            print(district_votes.sort_values(ascending = False))
            print("Av totalt:",np.sum(district_votes))

    def print_blanks_info(self):
        print("\n" + "#"*30)
        print(f"Blanke stemmer:")
        print("-"*30)
        print(self.blank_votes.sort_values(by = "Antall stemmer totalt", ascending = False))
        print("Total:", self.number_of_blanks)
        print("")

    def show_results(self):
        if self.args.blanks:
            self.print_blanks_info()

        print("")
        print("Antall stemmer per parti og valgdistrikt")
        print(self.district_votes_distributions_table)

        print("")
        print(f"Antall stemmer totalt: {self.total_minus_blanks}")

        print("")
        print(self.votes_per_seat)

        print("")
        print(f"Grense for utjevningsmandater = {self.args.levelinglimit}%  |  Første delingstall: {self.args.initialdivisor}")
        print(self.distribution_table)

    def plot_results(self):
        if self.args.title == "":
            self.args.title = f"Sperregrense: {self.args.levelinglimit}% | Første delingstall: {self.args.initialdivisor}"
        if not os.path.isdir(self.args.folder):
            os.makedirs(self.args.folder)
        self.plot_parliament()
        self.plot_num_seats()
        self.plot_map()
        self.plot_blocks()
        if self.args.showplot: plt.show()

    def plot_parliament(self, save = True):
        plt.figure(figsize = (12,3.2))
        
        plt.title(self.args.title)
        plt.axis("off")
        plt.tight_layout()
        plt.ylim((-6.5, 1))
        plt.xlim((-2, 32))
        i = 0
        while i < 169:
            for party, color in self.parties_left_to_right.items():
                if not party in self.distribution_with_leveling:
                    continue
                seats = self.distribution_with_leveling[party][0]
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
        if save: plt.savefig(os.path.join(self.args.folder, "tinget.png"))

    def plot_num_seats(self, save = True):
        plt.figure()
        plt.title(self.args.title)
        plt.axis("off")
        plt.tight_layout()

        row = 0
        for party, color in self.parties_left_to_right.items():
            if not party in self.distribution_with_leveling:
                if party in self.parties_actual_distri:
                    seats = 0
                else:
                    continue
            else:
                seats = self.distribution_with_leveling[party][0]
            partyname = self.party_names[party]
            
            if party in self.parties_actual_distri:
                actual = self.parties_actual_distri[party]
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
        if save: plt.savefig(os.path.join(self.args.folder, "seter.png"))

    def plot_map(self, save = True):
        plt.figure(figsize = (14,9))
        plt.title(self.args.title)
        plt.tight_layout()
        row_sizes = np.array([1, 6, 12, 24])
        row_sizes_cum = np.cumsum(row_sizes)

        parties_in_legend = []

        for district_name, location in self.locations.items():
            leveling_awarded = False
            district_distribution = self.district_distributions[district_name]

            if district_name == "Oslo" or district_name == "Akershus":
                plt.text(location[0] + 0.6, location[1] + 0.25, district_name, fontfamily = "Cascadia Code")
            elif district_name == "Hordaland" or district_name == "Rogaland":
                plt.text(location[0] -1.5, location[1] + 0.25, district_name, fontfamily = "Cascadia Code")
            elif district_name == "Sør-Trøndelag" or district_name == "Nordland":
                plt.text(location[0] + 0.5, location[1] + 0.25, district_name, fontfamily = "Cascadia Code")
            elif district_name == "Sogn og Fjordane":
                plt.text(location[0] -1.6, location[1] + 0.35, district_name, fontfamily = "Cascadia Code")
            elif district_name == "Møre og Romsdal":
                plt.text(location[0] -1.7, location[1] + 0.35, district_name, fontfamily = "Cascadia Code")
            elif district_name == "Buskerud":
                plt.text(location[0] + 0.2, location[1] - 0.35, district_name, fontfamily = "Cascadia Code")
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

                    marker = "h"

                    rowsize = row_sizes[row]
                    angle_diff = 2*np.pi/(rowsize)

                    radius = row*0.19
                    if party in parties_in_legend:
                        label = None
                    else:
                        label = self.party_names[party]
                        parties_in_legend.append(party)
                    x = np.cos(position*angle_diff)*radius + location[0]
                    y = np.sin(position*angle_diff)*radius + location[1]
                    if district_name in self.leveling_awards:
                        if self.leveling_awards[district_name] == party and not leveling_awarded:
                            plt.plot(x, y, marker = marker, markersize = 12, color = "black")
                            plt.plot(x, y, marker = marker, markersize = 10, color = "gold")
                            leveling_awarded = True
                    plt.plot(x, y, marker = marker, markersize = 7.5, color = "black")
                    plt.plot(x, y, marker = marker, markersize = 7, color = self.parties_left_to_right[party], label = label)

                    position += 1
                    seats_plotted += 1            
        plt.axis("equal")
        plt.axis("off")
        plt.legend()
        if save: plt.savefig(os.path.join(self.args.folder, "kart.png"))

    def plot_blocks(self, save = True):
        plt.figure(figsize = (14,9))
        plt.title(self.args.title)
        plt.tight_layout()

        plt.ylim(-8, 1)
        plt.xlim(-1, 170)
        
        blocks = {"Jonas' drøm": ("A", "SP", "SV"),
                  "Veldigrød+littgrønn": ("A", "SV", "RØDT", "MDG"),
                  "'Hele venstresiden'": ("A", "SP", "SV", "RØDT", "MDG"),
                  "Ernas drøm": ("H", "FRP", "V", "KRF"),
                  "De blågrønne": ("H", "SP", "FRP", "V", "KRF"),
                  "Sentrum-Høyre": ("H", "V", "KRF"),
                  "Sentrum-Sentrum-Høyre": ("H", "SP", "V", "KRF"),
                  "Pls no": ("H", "SP", "FRP")}

        legend_parties = []

        for i, key in enumerate(blocks):
            item = blocks[key]
            plt.text(1, -i + 0.4, key, fontfamily = {"Cascadia Code"})
            plt.barh(-i, 0.2, 0.8, left = 84.9, color = "black")
            plt.barh(-i, 169, 0.6, color = "#bbbbbb", edgecolor = "black")

            left = 0
            for party in item:
                if party not in self.distribution_with_leveling:
                    continue
                seats = self.distribution_with_leveling[party][0]
                if not party in legend_parties:
                    label = party
                    legend_parties.append(party)
                else:
                    label = None
                plt.barh(-i, seats, 0.6, left = left,
                         color = self.parties_left_to_right[party],
                         edgecolor = "black", label = label)
                left += seats

            for party, color in self.parties_left_to_right.items():
                if party not in self.distribution_with_leveling:
                    continue
                data = self.distribution_with_leveling[party]
                if party not in item:
                    seats = data[0]
                    plt.barh(-i, seats, 0.6, left = left,
                             color = color,
                             edgecolor = "black", alpha = 0.05)
                    left += seats
        plt.axis("off")
        plt.legend(loc = "upper right")
        if save: plt.savefig(os.path.join(self.args.folder, "blokker.png"))
       

class NewCountiesNorway(Norway):
    def __init__(self, args, filename = "2021-09-17_partydist.csv", num_leveling_seats = 1):
        super().__init__(args, filename = filename, num_leveling_seats = num_leveling_seats)

        new_counties = {"Vestland": [12, 14],
                        "Agder": [9, 10],
                        "Vestfold og Telemark": [7, 8],
                        "Innlandet": [4, 5],
                        "Viken": [1, 2, 6],
                        "Troms og Finnmark": [19, 20],
                        "Rogaland": [11],
                        "Møre og Romsdal": [15],
                        "Nordland": [18],
                        "Oslo": [3],
                        "Trøndelag": [16, 17]}

        locations = {"Viken":                [0.85, 1.1],
                     "Oslo":                 [0, 0],
                     "Innlandet":            [-0.6, 2],
                     "Vestfold og Telemark": [-1.9, -0.6],
                     "Agder":                [-2.5, -1.7],
                     "Rogaland":             [-4.3, -1.5],
                     "Vestland":             [-4.75, 0.5],
                     "Møre og Romsdal":      [-3.58, 2.6],
                     "Trøndelag":            [-0.5, 3.5],
                     "Nordland":             [1, 5.5],
                     "Troms og Finnmark":    [5, 6.8]}

        old_to_new_mapping = {}
        populations = {}
        dist_areas = {}
        for county, old_districts in new_counties.items():
            pops = 0
            area = 0
            for old_id in old_districts:
                old_name = self.district_name_by_id[old_id]
                pops += self.populations[old_name]
                area += self.dist_areas[old_name]
                old_to_new_mapping[old_name] = county

            populations[county] = pops
            dist_areas[county] = area
            
        self.populations = populations
        self.dist_areas = dist_areas
        self.locations = locations

        self._calculate_seat_distribution()

        # change district names to new counties
        for row in self.results.iterrows():
            index = row[0]
            data = row[1]
            old_fylkenavn = data["Fylkenavn"]
            new_fylkenavn = old_to_new_mapping[old_fylkenavn]
            data["Fylkenavn"] = new_fylkenavn
            self.results.iloc[index] = data
      
    def plot_map(self, save = True):
        plt.figure(figsize = (14,9))
        plt.title(self.args.title)
        plt.tight_layout()
        row_sizes = np.array([1, 6, 12, 24])
        row_sizes_cum = np.cumsum(row_sizes)

        parties_in_legend = []

        for district_name, location in self.locations.items():
            leveling_awarded = False
            district_distribution = self.district_distributions[district_name]
            if district_name == "Oslo" or district_name == "Viken":
                plt.text(location[0] + 0.35, location[1] - 0.4, district_name, fontfamily = "Cascadia Code")
            elif district_name == "Vestland":
                plt.text(location[0] - 0.35, location[1] - 0.6, district_name, fontfamily = "Cascadia Code")
            else:
                plt.text(location[0] - 0.35, location[1] - 0.4, district_name, fontfamily = "Cascadia Code")

            seats_plotted = 0
            prev_row = 0
            position = 0
            for party, seats in district_distribution.items():
                for seat in range(seats):
                    row = np.argmax(row_sizes_cum > seats_plotted)
                    if row != prev_row:
                        position = 0
                        prev_row = row

                    marker = "h"

                    rowsize = row_sizes[row]
                    angle_diff = 2*np.pi/(rowsize)

                    radius = row*0.19
                    if party in parties_in_legend:
                        label = None
                    else:
                        label = self.party_names[party]
                        parties_in_legend.append(party)
                    x = np.cos(position*angle_diff)*radius + location[0]
                    y = np.sin(position*angle_diff)*radius + location[1]
                    if district_name in self.leveling_awards:
                        if self.leveling_awards[district_name] == party and not leveling_awarded:
                            plt.plot(x, y, marker = marker, markersize = 12, color = "black")
                            plt.plot(x, y, marker = marker, markersize = 10, color = "gold")
                            leveling_awarded = True
                    plt.plot(x, y, marker = marker, markersize = 7.5, color = "black")
                    plt.plot(x, y, marker = marker, markersize = 7, color = self.parties_left_to_right[party], label = label)

                    position += 1
                    seats_plotted += 1            
        plt.axis("equal")
        plt.axis("off")
        plt.legend()
        if save: plt.savefig(os.path.join(self.args.folder, "kart.png"))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--levelinglimit",
                        help = "The vote share required to be awarded leveling seats",
                        default = 4,
                        metavar = "VOTESHARE",
                        type = float)
    parser.add_argument("-i", "--initialdivisor",
                        help = "Set the initial divisor when using the Sainte-Laguë method (default 1.4)",
                        default = 1.4,
                        type = float)
    parser.add_argument("-a", "--areamultiplier",
                        help = "Area multiplier for distribution of seats to districts (default 1.8)",
                        default = 1.8,
                        type = float)
    parser.add_argument("-m", "--method",
                        help = "Method to use when calculating results for each district",
                        choices = ["stlague", "fptp", "hunthill"],
                        default = "stlague",
                        type = str)
    parser.add_argument("-n", "--newcounties",
                        help = "Use the modern (new in 2020) counties of Norway to calculate the distribution of seats and results",
                        action = "store_true")
    parser.add_argument("-O", "--onedistrict",
                        help = "Treat the whole country as a single electoral district",
                        action = "store_true")
    parser.add_argument("-H", "--hardlimit",
                        help = "Treat the leveling limit as a hard limit (parties with less than the limit are excluded from gaining any seats)",
                        action = "store_true")
    parser.add_argument("-N", "--noleveling",
                        help = "Disable leveling seats",
                        action = "store_true")
    parser.add_argument("-U", "--usadist",
                        help = "Distribute seats to the districts in a similar way similar to the method used for the states in the US",
                        action = "store_true")
    parser.add_argument("-B", "--blanks",
                        help = "Display statistics for blank votes",
                        action = "store_true")
    parser.add_argument("-I", "--individuals",
                        help = "Display direct seats from individual districts provided as arguments",
                        nargs = "+",
                        default = [],
                        metavar = "DISTRICTS",
                        type = str)
    parser.add_argument("-D", "--displaydistricts",
                        help = "Display direct seats from all districts",
                        action = "store_true")
    parser.add_argument("-R", "--runanalyze",
                        help = "Run an analysis on the election results",
                        action = "store_true")
    parser.add_argument("-P", "--plot",
                        help = "Create the plots",
                        action = "store_true")
    parser.add_argument("-S", "--showplot",
                        help = "Show the plots",
                        action = "store_true")
    parser.add_argument("-t", "--title",
                        help = "Title for the plots (default is no title)",
                        default = "",
                        type = str)
    parser.add_argument("-f", "--folder",
                        help = "Folder to save plots in",
                        default = "./figs",
                        type = str)
    args = parser.parse_args()
    return args


def main():
    args = parse_args()

    if args.noleveling:
        num_leveling_seats = 0
    else:
        num_leveling_seats = 1

    if args.onedistrict:
        norway = Norway(args, num_leveling_seats = 169) # can't disable leveling seats for single district,
                                                        # since all seats are equivalent to leveling seats
                                                        # in this case
    elif args.newcounties:
        norway = NewCountiesNorway(args, num_leveling_seats = num_leveling_seats)
    else:
        norway = Norway(args, num_leveling_seats = num_leveling_seats)
        adjustments = pd.read_excel("justeringer.ods")
        for row in adjustments.iterrows():
            party = row[1]["Partikode"]
            for district in row[1].iteritems():
                name = district[0]
                votes = district[1]
                if name == "Partikode" or name == "Partinavn":
                    continue
                norway.add_votes(name, party, votes)

    norway.calculate(dist_method = args.method)
    norway.show_results()

    if args.displaydistricts or args.individuals:
        norway.show_individual_districts()

    if args.runanalyze:
        norway.analyze()

    if args.plot:
        norway.plot_results()


if __name__ == "__main__":
    main()
