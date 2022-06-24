from copy import deepcopy

import matplotlib.pyplot as plt
from tqdm import tqdm

from .util import Individual, TIS


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

    def mutate(self, improve):
        """
        For each individual in the population mutate it and append it to the population.
        Doubles the population.
        """
        new = []
        for i in self.population:
            fork = deepcopy(i)
            if improve:
                fork.mutate_improve(self.tis)
            else:
                fork.mutate(self.tis)
            new.append(fork)
        self.population += new

    def run(self, reset=False, plot=False, improve=False):
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
            self.mutate(improve)

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

