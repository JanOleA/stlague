import numpy as np


class District:
    def __init__(self, seats, initial_divisor = 1.4, method = "stlague", initial_seats = 0):
        self._seats = seats
        self._initial_divisor = initial_divisor
        self._initial_seats = initial_seats
        self._votes = []
        self._names = []

        if method.lower() == "stlague":
            self.calculate = self.stlague
        if method.lower() == "fptp":
            self.calculate = self.fptp
        if method.lower() == "hunthill" or method.lower() == "hh":
            self.calculate = self.hunthill

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

    def stlague(self):
        if len(self._votes) == 0:
            return {}
        num_parties = len(self._votes)
        awarded_seats = np.zeros(num_parties, dtype = np.int)
        votes_array = np.array(self._votes)
        divisor_array = np.full(num_parties, self._initial_divisor)

        while np.sum(awarded_seats) < self._seats:
            scores = votes_array/divisor_array
            next_seat = np.argmax(scores)
            awarded_seats[next_seat] += 1
            divisor_array[next_seat] = awarded_seats[next_seat]*2 + 1

        final_results = {}

        for name, seats in zip(self._names, awarded_seats):
            final_results[name] = seats

        return final_results

    def fptp(self):
        if len(self._votes) == 0:
            return {}
        winner_ind = np.argmax(self._votes)
        final_results = {self._names[winner_ind]: self._seats}
        return final_results

    def hunthill(self):
        if len(self._votes) == 0:
            return {}
        num_parties = len(self._votes)
        awarded_seats = np.full(num_parties, self._initial_seats)
        votes_array = np.array(self._votes)
        divisor_array = np.full(num_parties, np.sqrt(self._initial_seats*(self._initial_seats + 1)))

        while np.sum(awarded_seats) < self._seats:
            scores = votes_array/divisor_array
            next_seat = np.argmax(scores)
            awarded_seats[next_seat] += 1
            awarded_seats_this = awarded_seats[next_seat]
            divisor_array[next_seat] = np.sqrt(awarded_seats_this*(awarded_seats_this + 1))

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
