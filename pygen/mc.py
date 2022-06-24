"""
This module implements the Minimum Conformity procedure for image evolution/generation
"""

from .util import Individual, TIS
import matplotlib.pyplot as plt


class MinimumConformity:
    def __init__(self, cols:int, rows:int, tis:TIS):
        self.cols = cols
        self.rows = rows
        self.tis = tis

        self._setup()

    def _setup(self):
        self.individual = Individual(self.cols, self.rows, self.tis)


    def run(self, log=False, verbose=False, maxstep=100):
        if log:
            data = []
        i = 0
        while pos:= self.individual.min_conform(self.tis):
            if i > maxstep:
                break
            if verbose:
                print(pos,end=" ")
            if log:
                v = self.individual.fitness(self.tis) 
                if verbose:
                    print(v)
                data.append(v)
            x, y = pos
            self.individual.conform(x, y, self.tis)
            i += 1

        if log:
            plt.plot(data)
            plt.axhline(y=self.individual._max_score(), color='gold', linestyle='-.')
            plt.ylabel('fitness')
            plt.xlabel('time')
            plt.title('Fitness over Time')
            plt.savefig(f'min_conform_{self.cols}x{self.rows}.png')
            plt.clf()

