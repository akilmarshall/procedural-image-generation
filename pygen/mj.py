"""Implementes an algorithm insprised by the work in this repository https://github.com/mxgmn/MarkovJunior. """
from .util import Individual, TIS, V
from collections import defaultdict
import numpy as np
from random import choice



def to_array(x:tuple):
    match x:
        case (a, b, 0): return np.array([[a], [b]])
        case (a, b, 2): return np.array([[b], [a]]) 
        case (a, b, 1): return np.array([[a, b]])
        case (a, b, 3): return np.array([[b, a]])
        # case (a, b, c, d): pass
        case _: pass

def to_tuple(x:np.ndarray):
    match x.shape:
        case (1, 2):
            a = x[0][0] 
            b = x[0][1] 
            if a is None:
                return V(a, b, 3)
            elif b is None:
                return V(a, b, 1)
        case (2, 1):
            a = x[0][0] 
            b = x[1][0] 
            if a is None:
                return V(a, b, 0)
            elif b is None:
                return V(b, a, 2)

def ruleset(tis:TIS):
    """Compute all possible 2 rules from TIS. """
    rules = defaultdict(list)
    for i in range(tis.n):
        # compute vector rules
        for d in range(4):
            key = (i, None, d)
            for n in tis.nids(i, d):
                val = (i, n, d)
                rules[key].append(val)

    return rules

class MJ:
    def __init__(self, cols:int , rows:int, tis:TIS):
        self.cols = cols
        self.rows = rows
        self.nids = tis.nids
        self.n = tis.n
        self.rules = ruleset(tis)
        self.individual = Individual(self.cols, self.rows, tis)

        self.reset()

    def reset(self):
        self.individual.reset()
        h, k = self.cols // 2, self.rows // 2 
        self.individual.seed(h, k)

    def apply_rule(self, x:int, y:int, a:None|int, b:None|int, d:int):
        match (a, b, d):
            case (a, b, 0):
                self.individual.set(x, y, a)
                self.individual.set(x + 1, y, b)
            case (a, b, 1):
                self.individual.set(x, y, a)
                self.individual.set(x, y - 1, b)
            case (a, b, 2):
                self.individual.set(x, y, a)
                self.individual.set(x - 1, y, b)
            case (a, b, 3):
                self.individual.set(x, y, a)
                self.individual.set(x, y + 1, b)

    def step(self):
        (x, y), (a, b, d) = choice(list(self.individual.rule_match_candidates()))
        h = list(self.individual._defined_neighbors(x, y))
        match len(h):
            case 1:
                # do a rule check
                self.apply_rule(x, y, a, b, d)
            case 2:
                # do an inference
                pass


    def run(self):
        while not self.individual.empty():
            self.step()
