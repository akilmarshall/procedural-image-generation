from .util import TIS
from itertools import product
import numpy as np
from random import randint, choice
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

    def conform(self,t, x, y, tis) -> int:
        score = 0
        for nid, i, j in self._neighbors(x, y):
            if self.data[i][j] in tis.nids(t, nid):
                score += 1
        return score

    def fitness(self, tis:TIS) -> int:
        score = 0
        for x, y in self._positions():
            t = self.data[x][y]
            score += self.conform(t, x, y, tis)
        return score

    def mutate(self, tis:TIS):
        """Randomly mutate self. """
        x, y = self._rand_pos()
        t = self._rand_individual(tis)
        self.data[x][y] = t

    def mutate_improve(self, tis:TIS, mc):
        """At a random position it's neighbors are made to conform to the neighbor function. """
        if mc:
            x, y = self._min_conform(tis)
        else:
            x, y = self._rand_pos()
        t = self.data[x][y]
        for (nid, i, j) in self._neighbors(x, y):
            nids =tis.nids(t, nid) 
            if t not in nids and nids:
                self.data[i][j] = choice(nids)


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
    
    def _min_conform(self, tis:TIS) -> tuple[int, int]:
        c = None
        i, j = 0, 0
        for x, y in self._positions():
            t = self.data[x][y]
            v = self.conform(t, x, y, tis)
            if c is None or v < c:
                c = v
                i, j = x, y
        return i, j

    def _rand_individual(self, tis:TIS) -> int:
        return randint(0, tis.n - 1)

    def _rand_init(self, tis:TIS):
        """Set each position to a random valid value. """
        for x, y in self._positions():
            self.data[x][y] = self._rand_individual(tis)

    def _max_score(self) -> int:
        if self.cols > 2 and self.rows > 2:
            return 2 * 3 * (self.rows - 2) + 2 * 3 * (self.cols - 2) + 8 + 4 * (self.rows - 2) * (self.cols - 2)

        return 0



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
        self.avg_fitness = []

        self.reset()

    def reset(self):
        self.population:list[Individual] = []
        self.epoch = 0
        self.avg_fitness = []
        for _ in range(self.pop):
            self.population.append(Individual(self.n, self.m, self.tis))

    def cull(self):
        """Drop the unfit half of the population. """
        n = self.pop // 2
        sortable = [(i.fitness(self.tis), i) for i in self.population]
        ordered = sorted(sortable, key=lambda x:x[0])
        fit = [i[1] for i in ordered]
        self.population = fit[0:n]

    def mutate(self, improve, min_conform):
        """
        For each individual in the population mutate it and append it to the population.
        Doubles the population.
        """
        new = []
        for i in self.population:
            fork = deepcopy(i)
            if improve:
                fork.mutate_improve(self.tis, min_conform)
            else:
                fork.mutate(self.tis)
            new.append(fork)
        self.population += new

    def run(self, reset=False, plot=False, improve=False, min_conform=False):
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
            self.mutate(improve, min_conform)

        if plot:
            self.avg_fitness.append(avg_fitness)
            for i, a in enumerate(self.avg_fitness):
                plt.plot(a, label=f'epoch {i}')
            plt.axhline(y=self.population[0]._max_score(), color='gold', linestyle='-.')
            plt.ylabel('fitness')
            plt.xlabel('time')
            plt.title('Average Fitness over Time')
            plt.legend()
            plt.savefig(f'{self.n}x{self.m} population {self.pop} epoch {self.epoch}.png')
            plt.clf()
        self.epoch += 1


    def _avg_fitness(self) -> float:
        score = 0
        for i in self.population:
            score += i.fitness(self.tis)
        return score / len(self.population)

