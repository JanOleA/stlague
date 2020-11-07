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
        awarded_seats = np.zeros(num_parties)
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


if __name__ == "__main__":
    states_dict = {}
    states_distribution = {}
    states = pd.read_csv("states.csv", delimiter = ";")
    for state in states.iterrows():
        name = state[1]["state"]
        electoral_votes = state[1]["votes"]
        states_dict[name] = District(electoral_votes)

    #votes = pd.read_csv("1976-2016-president.csv")
    #votes = votes[votes["year"] == 2016]
    #votes_column = "candidatevotes"

    votes = pd.read_csv("president_county_candidate.csv")
    votes_column = "votes"
    
    df_states = list(votes.state.unique())

    total_distribution = {}
    candidate_vote_number = {}

    yticks = []

    fig, ax = plt.subplots()
    for n, state in enumerate(states_dict):
        state_df = votes[votes["state"] == state]
        state_candidates = list(state_df.candidate.unique())
        for cand in state_candidates:
            candidate_votes = np.sum(state_df[state_df["candidate"] == cand][votes_column])
            states_dict[state].add_votes(cand, candidate_votes)
            if cand in candidate_vote_number:
                candidate_vote_number[cand] += candidate_votes
            else:
                candidate_vote_number[cand] = candidate_votes

        distribution = states_dict[state].calculate()
        ax.barh(n, distribution["Joe Biden"], height = 0.8, color = "blue")
        ax.barh(n, distribution["Donald Trump"], left = distribution["Joe Biden"], height = 0.8, color = "red")
        yticks.append(state)
        
        for cand, electoral_votes in distribution.items():
            if cand in total_distribution:
                total_distribution[cand] += electoral_votes
            else:
                total_distribution[cand] = electoral_votes
    
    plt.yticks(np.arange(0, 51), yticks)

    candidates_list = []
    electoral_votes = []
    total_votes = []
    for cand, evs in total_distribution.items():
        if cand == " Write-ins":
            continue
        candidates_list.append(cand)
        electoral_votes.append(evs)
        total_votes.append(candidate_vote_number[cand])
    
    candidates_list = np.array(candidates_list)
    electoral_votes = np.array(electoral_votes)
    total_votes = np.array(total_votes)

    idx = np.argsort(total_votes)[::-1]
    candidates_list = candidates_list[idx]
    electoral_votes = electoral_votes[idx]
    total_votes = total_votes[idx]

    print("Top six candidates:")

    print(f"{'Name':>20s} {'EV':>5s} {'Votes':>10s} {'% of EV':>11s} {'% of votes':>12s} {'ppt diff':>10s}")
    print("#"*73)

    fig, ax = plt.subplots()
    i = 0
    for cand, evs, vote in zip(candidates_list[:6], electoral_votes[:6], total_votes[:6]):
        evshare = evs/538*100
        voteshare = vote/np.sum(total_votes)*100
        print(f"{cand:>20s} {int(evs):>5d} {int(vote):>10d} {evshare:>9.2f} % {voteshare:>10.2f} % {evshare - voteshare:>10.2f}")
        if evs > 0:
            ax.barh(0, evs, left = np.sum(electoral_votes[:i]), label = cand, height = 0.2)
        i += 1

    plt.legend()
    plt.show()

    """
    # mandatfordeling per fylkenummer, uten utjevningsmandater
    mandatfordeling = {1: 8,
                       2: 16,
                       3: 18,
                       4: 6,
                       5: 6,
                       6: 8,
                       7: 6,
                       8: 5,
                       9: 3,
                       10: 5,
                       11: 13,
                       12: 15,
                       14: 3,
                       15: 8,
                       16: 9,
                       17: 4,
                       18: 8,
                       19: 5,
                       20: 4}

    fordeling = {}
    partistemmer = {}
    results_2017 = pd.read_csv("2017.csv", delimiter = ";")

    fylker = list(results_2017.Fylkenavn.unique())
    for fylke in fylker:
        results_fylke = results_2017[results_2017["Fylkenavn"] == fylke]
        fylkenummer = int(results_fylke.Fylkenummer.unique())
        partier = list(results_fylke.Partinavn.unique())

        valgdistrikt = District(mandatfordeling[fylkenummer])
        
        for parti in partier:
            results_parti = results_fylke[results_fylke["Partinavn"] == parti]
            stemmer = np.sum(results_parti["Antall stemmer totalt"])
            if parti in partistemmer:
                partistemmer[parti] += stemmer
            else:
                partistemmer[parti] = stemmer
            if parti == "Blanke":
                continue
            valgdistrikt.add_votes(parti, stemmer)

        distriktfordeling = valgdistrikt.calculate()

        for parti, seter in distriktfordeling.items():
            if seter == 0:
                continue
            if parti in fordeling:
                fordeling[parti] += seter
            else:
                fordeling[parti] = seter
    
    s = 0
    for key, item in fordeling.items():
        s += item
    print(s)
    
    utgjevning = District(19)
    totalt_antall_stemmer = np.sum(results_2017["Antall stemmer totalt"])

    for parti, stemmer in partistemmer.items():
        if stemmer/totalt_antall_stemmer < 0.04:
            continue
        utgjevning.add_votes(parti, stemmer)
    
    utgjevningsresultater = utgjevning.calculate()
    
    s = 0
    for parti, resultat in utgjevningsresultater.items():
        print(parti, resultat)
        #diff = resultat - fordeling[parti]
        #print(parti, diff)
        #s += resultat
        #if diff < 0:
        #    print("Overrepresentation, remove", parti)
    print(s)"""