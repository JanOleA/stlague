import numpy as np
import pandas as pd

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
    
    utgjevning = District(169)
    totalt_antall_stemmer = np.sum(results_2017["Antall stemmer totalt"])

    for parti, stemmer in partistemmer.items():
        if parti not in fordeling:
            continue
        if fordeling[parti] == 0:
            continue
        utgjevning.add_votes(parti, stemmer)
    
    utgjevningsresultater = utgjevning.calculate()
    
    s = 0
    for parti, resultat in utgjevningsresultater.items():
        diff = resultat - fordeling[parti]
        print(parti, diff)
        s += resultat
        if diff < 0:
            print("Overrepresentation, remove", parti)
    print(s)