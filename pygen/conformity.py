"""
This module implements conformity algorithms.
"""

from .util import Individual, TIS
import matplotlib.pyplot as plt
from collections import deque, Counter
import numpy as np
# from math import abs


def repeat(d: deque, i:int, n) -> bool:
    c = Counter(d)
    if i in c and c[i] >= n:
        return True

    return False

def zero(x, eps=0.0001) -> bool:
    return abs(x) < eps



class MinimumConformity:
    def __init__(self, cols:int, rows:int, tis:TIS):
        self.cols = cols
        self.rows = rows
        self.tis = tis

        self._setup()

    def _setup(self):
        self.individual = Individual(self.cols, self.rows, self.tis)


    def run(self, log=True, window=20, maxstep=100, g=2):
        data = []
        recent = deque(maxlen=window)  # measure the variance over some window 
        rrecent = deque(maxlen=window // g) # measure the variance over the variance in a truncated window
        i = 0
        while pos:= self.individual.min_conform():
            x, y = pos
            if i > maxstep:
                break
            v = self.individual.fitness()
            if recent and len(recent) == window:
                var = np.array(recent).var() 
                rrecent.append(var)
                if recent and zero(var):
                    # variance went to zero
                    break
                if len(rrecent) == window // g:
                    vvar = np.array(rrecent).var() 
                    if zero(vvar):
                        # variance variance went to zero
                        break
            self.individual.conform(x, y)
            data.append(v)
            recent.append(v)
            i += 1

        if log:
            plt.plot(data)
            plt.axhline(y=self.individual._max_score(), color='gold', linestyle='-.')
            plt.ylabel('fitness')
            plt.xlabel('time')
            plt.title('Fitness over Time')
            plt.savefig(f'min_conform_{self.cols}x{self.rows}.png')
            plt.clf()


class SCI:
    """
    Stochastic Conformity Improvement
    """
    def __init__(self, cols:int, rows:int, tis:TIS, most=True):
        """
        """
        self.cols = cols
        self.rows = rows
        self.most = most
        self.n = tis.n
        self.nids = tis.nids
