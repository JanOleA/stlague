import argparse
import os
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from district import District
from election import parse_args, Norway


class USA(Norway):
    def __init__(self, args, filename = "./usa/president_county_candidate.csv", num_leveling_seats = 1):
        self._active_message = False
        self.args = args
        self.results = pd.read_csv(filename, delimiter = ",")

        poparea = pd.read_csv("./usa/poparea.csv")

        populations = {}
        dist_areas = {}

        for row in poparea.iterrows():
            state = row[1]["State"]
            pop = row[1]["Population"]
            area = row[1]["Area"]
            populations[state] = pop
            dist_areas[state] = area

        self.populations = populations
        self.dist_areas = dist_areas
        self.num_leveling_seats = num_leveling_seats

        self.total_votes = self.results["total_votes"].sum()

    def _calculate_seat_distribution(self):
        if self.args.usadist:
            seat_distribution = District(538 - 2*len(self.populations.items()),
                                         method = "hunthill", initial_seats = 1)
        else:
            seat_distribution = District(538, initial_divisor = 1)

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
        s = 0 # check that the total is 538 as well
        for key, item in self.total_seats.items():
            s += item
            self.seats_without_leveling[key] = item - self.num_leveling_seats
        assert s == 538 # check that the total is 538 as well

    def _calculate_direct_seats(self, method = "stlague"):
        results = self.results
        seats_without_leveling = self.seats_without_leveling

        candidate_votes_total = {}
        candidate_names = []
        distribution = {}
        state_distributions = {}
        state_votes_distributions = {}

        for state in self.populations.keys():
            results_state = results[results["state"] == state]
            candidates = results_state.candidate.unique()

            state_votes = {}

            electoral_district = District(seats_without_leveling[state],
                                          initial_divisor = self.args.initialdivisor,
                                          method = method)
            
            for candidate in candidates:
                if candidate not in candidate_names:
                    candidate_names.append(candidate)
                results_state_candidate = results_state[results_state["candidate"] == candidate]
                votes_state_candidate = results_state_candidate["total_votes"].sum()

                state_votes[candidate] = votes_state_candidate
                electoral_district.add_votes(candidate, votes_state_candidate)

                if candidate in candidate_votes_total:
                    candidate_votes_total[candidate] += votes_state_candidate
                else:
                    candidate_votes_total[candidate] = votes_state_candidate

            state_distribution = electoral_district.calculate()
            state_distributions[state] = state_distribution
            state_votes_distributions[state] = state_votes

            for cand, seats in state_distribution.items():
                if not seats:
                    continue
                if cand in distribution:
                    distribution[cand] += seats
                else:
                    distribution[cand] = seats
            
        self.candidate_votes_total = candidate_votes_total
        self.candidate_names = candidate_names
        self.distribution = distribution
        self.state_distributions = state_distributions
        self.state_votes_distributions = state_votes_distributions
        self.state_votes_distributions_table = pd.DataFrame(state_votes_distributions).fillna(0)

    def _calculate_leveling_seats_parties(self):
        cand_vote_shares = {}
        leveling_seats = 538
        leveling_seats_limit = self.args.levelinglimit

        cand_competing_votes = {}

        for cand, votes in self.candidate_votes_total.items():
            if cand in self.distribution:
                seats = self.distribution[cand]
            else:
                seats = 0
            cand_percent_of_total = 100*votes/self.total_votes
            cand_vote_shares[cand] = np.round(cand_percent_of_total, 2)

            if cand_percent_of_total >= leveling_seats_limit:
                cand_competing_votes[cand] = votes
            elif cand in self.distribution and self.args.singleseatleveling:
                if seats >= 1:
                    cand_competing_votes[cand] = votes
            else:
                leveling_seats -= seats

        leveling_district = District(leveling_seats)
        for cand, votes in cand_competing_votes.items():
            leveling_district.add_votes(cand, votes)
        
        leveling_distribution = leveling_district.calculate()

        cands_over = None
        while cands_over or cands_over is None:
            cands_over = []

            for cand, level_seats in leveling_distribution.items():
                if cand in self.distribution:
                    state_seats = self.distribution[cand]
                else:
                    state_seats = 0
                if state_seats >= level_seats:
                    cands_over.append(cand)
                    leveling_district.remove_party(cand)
                    leveling_district.seats = leveling_district.seats - state_seats
            
            leveling_distribution = leveling_district.calculate()

        distribution_with_leveling = {}

        for cand, seats in self.distribution.items():
            if cand in leveling_distribution:
                seats_before = seats
                seats = leveling_distribution[cand]
                diff = seats - seats_before
            else:
                diff = 0
            votes_for_leveling = np.ceil(((leveling_seats_limit/100)*(self.total_votes) - self.candidate_votes_total[cand])/(1 - leveling_seats_limit/100))
            distribution_with_leveling[cand] = [seats, diff, cand_vote_shares[cand], self.candidate_votes_total[cand], votes_for_leveling]

        for cand, seats in leveling_distribution.items():
            if not cand in self.distribution:
                seats = leveling_distribution[cand]
                votes_for_leveling = np.ceil(((leveling_seats_limit/100)*(self.total_votes) - self.candidate_votes_total[cand])/(1 - leveling_seats_limit/100))
                distribution_with_leveling[cand] = [seats, diff, cand_vote_shares[cand], self.candidate_votes_total[cand], votes_for_leveling]

        self.leveling_distribution = leveling_distribution # just the distribution for the leveling seats
        self.distribution_with_leveling = distribution_with_leveling # full distribution of seats, including leveling seats
        self.candidate_vote_shares = cand_vote_shares

    def _calculate_leveling_seats_districts(self):
        leveling_table = []        
        seats_without_leveling = self.seats_without_leveling
        leveling_distribution = self.leveling_distribution
        state_distributions = self.state_distributions
        distribution = self.distribution
        results = self.results

        for state in self.populations.keys():
            results_state = results[results["state"] == state]
            state_votes_total = results_state["total_votes"].sum()
            state_divisor = state_votes_total/self.total_seats[state]
            for cand, level_seats in leveling_distribution.items():
                cand_state_votes = results_state[results_state["candidate"] == cand]
                cand_state_votes = np.sum(cand_state_votes["total_votes"])
                if cand in state_distributions[state]:
                    direct_seats_in_state = state_distributions[state][cand]
                else:
                    direct_seats_in_state = 0
                divisor = direct_seats_in_state*2 + 1
                rest_quotient = (cand_state_votes/divisor)/state_divisor
                leveling_table.append([rest_quotient, state, cand])
        leveling_table = pd.DataFrame(leveling_table)
        if len(leveling_table) > 0:
            leveling_table.columns = ["quotient", "state", "candidate"]
            leveling_table = leveling_table.sort_values(by = "quotient", ascending = False)
        
        cands_awarded = {}
        leveling_awards = {}

        for line in leveling_table.iterrows():
            state = line[1]["state"]
            cand = line[1]["candidate"]
            if cand in distribution:
                seats_to_award = leveling_distribution[cand] - distribution[cand]
            else:
                seats_to_award = leveling_distribution[cand]
            if state in leveling_awards:
                continue
            if cand in cands_awarded:
                if cands_awarded[cand] >= seats_to_award:
                    continue
            else:
                cands_awarded[cand] = 0
            leveling_awards[state] = cand
            cands_awarded[cand] += 1

        for state, cand in leveling_awards.items():
            if cand in state_distributions[state]:
                state_distributions[state][cand] += 1
            else:
                state_distributions[state][cand] = 1

        self.state_distributions = state_distributions
        self.leveling_awards = leveling_awards

    def _make_distribution_table(self):
        distribution_table = pd.DataFrame(self.distribution_with_leveling).T
        distribution_table.columns = ["Seats", "Leveling seats", "% votes", "# votes", f"Votes to {self.args.levelinglimit}%"]
        distribution_table = distribution_table.sort_values("Seats", axis = 0, ascending = False)

        seat_sums = distribution_table.sum(axis = 0)
        assert seat_sums["Seats"] == 538

        self.distribution_table = distribution_table

    def show_individual_districts(self):
        individuals_lowered = [x.lower() for x in self.args.individuals]

        for district, dist_distribution in self.state_distributions.items():
            if self.args.individuals and district.lower() not in individuals_lowered:
                passing = False
                for individual in individuals_lowered:
                    if individual in district.lower():
                        passing = True
                if not passing:
                    continue
            print("\n" + "#"*50)
            print(f"Seats from {district}")
            print("-"*50)
            for party, seats in dist_distribution.items():
                if seats == 0:
                    continue
                print(f"{party:>35s} {seats:>3d}")
            print(f"Votes in {district}")
            district_votes = self.state_votes_distributions_table[district]
            print(district_votes.sort_values(ascending = False))
            print("Of total:",np.sum(district_votes))


    def print_blanks_info(self):
        return None

    def show_results(self):
        print("")
        print("Votes per candidate and state")
        print(self.state_votes_distributions_table)

        print("")
        print(f"Total number of votes: {self.total_votes}")

        print("")
        print(f"Limit for leveling seats = {self.args.levelinglimit}%  |  First divisor: {self.args.initialdivisor}")
        print(self.distribution_table)

    def calculate(self, dist_method = "stlague"):
        self._calculate_seat_distribution()
        self._message_start("Calculating direct distribution")
        self._calculate_direct_seats(method = dist_method)
        self._message_start("Calculating candidate leveling seats")
        self._calculate_leveling_seats_parties()
        self._message_start("Calculating state leveling seats")
        self._calculate_leveling_seats_districts()
        self._message_end()
        self._make_distribution_table()


def main():
    args = parse_args()
    usa = USA(args)
    usa.calculate()
    usa.show_results()

    if args.displaydistricts or args.individuals:
        usa.show_individual_districts()


if __name__ == "__main__":
    main()