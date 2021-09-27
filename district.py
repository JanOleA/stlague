import numpy as np


class District:
    def __init__(self, seats, initial_divisor = 1.4, method = "stlague",
                 initial_seats = 1, hh_threshold = 4):
        self._seats = seats
        self._initial_divisor = initial_divisor
        self._initial_seats = initial_seats
        self._hh_threshold = hh_threshold
        self._votes = []
        self._names = []

        if method.lower() == "stlague":
            self.calculate = self.stlague
        elif method.lower() == "fptp":
            self.calculate = self.fptp
        elif method.lower() == "dhondt":
            self.calculate = self.dhondt
        elif method.lower() == "hunthill" or method.lower() == "hh":
            self.calculate = self.hunthill

    def add_votes(self, name, result):
        if name in self._names:
            idx = self._names.index(name)
            self._votes[idx] += result
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

    def dhondt(self):
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
            divisor_array[next_seat] = awarded_seats[next_seat] + 1

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
        tmp_votes = self._votes
        tmp_names = self._names
        sum_votes = sum(tmp_votes)
        rem_names = []
        for name, votes in zip(tmp_names, tmp_votes):
            percent_votes = votes/sum_votes*100
            if percent_votes < self._hh_threshold:
                rem_names.append(name)

        while rem_names:
            name = rem_names.pop()
            idx = tmp_names.index(name)
            tmp_votes.pop(idx)
            tmp_names.pop(idx)

        if len(self._votes) == 0:
            return {}
        num_parties = len(self._votes)
        awarded_seats = np.full(num_parties, self._initial_seats)
        votes_array = np.array(self._votes)
        divisor_array = np.full(num_parties, np.sqrt(self._initial_seats*(self._initial_seats + 1)))

        while np.sum(awarded_seats) < self._seats:
            scores = votes_array/divisor_array
            scores = np.nan_to_num(scores)
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
