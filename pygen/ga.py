from .util import TIS
from itertools import product
import numpy as np
from random import randint
import matplotlib.pyplot as plt
from tqdm import tqdm
from copy import deepcopy


class Individual:
    """
    Individual for "genetic" tinkering
    """
    def __init__(self, n, m, tis):
        self.cols = n
        self.rows = m
        self.data = np.zeros((n, m), np.int8)
        self._rand_init(tis)

    def fitness(self, tis:TIS) -> int:
        score = 0
        for x, y in self._positions():
            t = self.data[x][y]
            for nid, i, j in self._neighbors(x, y):
                if self.data[i][j] in tis.nids(t, nid):
                    score += 1
        return score

    def mutate(self, tis:TIS):
        x, y = self._rand_pos()
        t = self._rand_individual(tis)
        self.data[x][y] = t

    def _positions(self):
        return product(range(self.cols), range(self.rows))

    def _neighbors(self, x, y):
        if x < self.cols - 1:
            yield 0, x + 1, y
        if y < self.rows - 1:
            yield 3, x, y + 1
        if x > 0:
            yield 2, x - 1, y
        if y > 0:
            yield 1, x, y - 1

    def _rand_pos(self) -> tuple[int, int]:
        return randint(0, self.cols - 1), randint(0, self.rows - 1)

    def _rand_individual(self, tis:TIS) -> int:
        return randint(0, tis.n - 1)

    def _rand_init(self, tis:TIS):
        """Set each position to a random valid value. """
        for x, y in self._positions():
            self.data[x][y] = self._rand_individual(tis)



class MutateEvolve:
    """
    1. Initialize the population randomly
    2. for t time steps
    3. order the population by fitness
    4. cull the bottom half
    5. copy the fit half, mutating each at a random position
    6. goto 3.
    """
    def __init__(self, pop:int, n:int, m:int, tis:TIS, t=1000):
        self.pop = pop
        self.n = n
        self.m = m
        self.tis = tis
        self.t = t
        self.epoch = 0

        self.reset()

    def reset(self):
        self.population:list[Individual] = []
        self.epoch = 0
        for _ in range(self.pop):
            self.population.append(Individual(self.n, self.m, self.tis))

    def cull(self):
        """Drop the unfit half of the population. """
        n = self.pop // 2
        sortable = [(i.fitness(self.tis), i) for i in self.population]
        ordered = sorted(sortable, key=lambda x:x[0])
        fit = [i[1] for i in ordered]
        self.population = fit[0:n]

    def mutate(self):
        """
        For each individual in the population mutate it and append it to the population.
        Doubles the population.
        """
        new = []
        for i in self.population:
            fork = deepcopy(i)
            fork.mutate(self.tis)
            new.append(fork)
        self.population += new

    def run(self, reset=False, plot=False):
        """
        Evolve the population [self.t] time steps,
        if reset is True the population is reset, otherwise evolution is continued.
        """
        if reset:
            self.reset()

        if plot:
            avg_fitness = []

        for _ in tqdm(range(self.t)):
            if plot:
                avg_fitness.append(self._avg_fitness())

            self.cull()
            self.mutate()

        if plot:
            plt.plot(avg_fitness)
            plt.ylabel('fitness')
            plt.xlabel('time')
            plt.title('average fitness over time')
            plt.savefig(f'{self.n}x{self.m} population {self.pop} epoch {self.epoch}.png')
        self.epoch += 1


    def _avg_fitness(self) -> float:
        score = 0
        for i in self.population:
            score += i.fitness(self.tis)
        return score / len(self.population)

