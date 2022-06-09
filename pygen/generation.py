from pygen.util import TIS
from itertools import product
from copy import deepcopy
from collections import deque
from os import mkdir
from os.path import exists
from shutil import rmtree
import matplotlib.pyplot as plt


class Image:
    def __init__(self, n: int, m: int, tis: TIS):
        self.n = n
        self.m = m
        self.tis = tis

        self.img = [[set(range(tis.n)) for _ in range(m)] for _ in range(n)]

    def _indicies(self):
        return product(range(self.n), range(self.m))

    def complete(self) -> bool:
        """
        return True if the image is fully collapsed
        False otherwise
        """
        for h, k in self._indicies():
            t = self.img[h][k]
            if isinstance(t, set):
                return False
        return True
    def good(self) -> bool:
        """
        return True if the image is fully collapsed and defined
        i.e. contains no None
        False otherwise
        """
        if self.complete():
            for h, k in self._indicies():
                if self.img[h][k] is None:
                    return False
        return True

    def min_entropy(self) -> tuple[int, int]:
        e = None
        x, y = -1, -1
        for h, k in self._indicies():
            s = self.img[h][k]
            if isinstance(s, set) and (e is None or len(s) < e):
                e = len(s)
                x, y = h, k
        return x, y

    def __getitem__(self, x):
        # if it is desireable to have advanced control
        # over the object returned here when using self[x]
        # notation a special data type must be defined for
        # the columns
        return self.img[x]

    def neighbors(self, x, y):
        if x < self.n - 1 and isinstance(self.img[x + 1][y], set):
            yield 0, x + 1, y
        if y < self.m - 1 and isinstance(self.img[x][y + 1], set):
            yield 3, x, y + 1
        if x > 0 and isinstance(self.img[x - 1][y], set):
            yield 2, x - 1, y
        if y > 0 and isinstance(self.img[x][y - 1], set):
            yield 1, x, y - 1

    def collapse(self, h: int, k: int, t: int):
        if t in self.img[h][k]:
            self.img[h][k] = t
            for nid, i, j in self.neighbors(h, k):
                T = self.img[i][j].intersection(set(self.tis(t, nid)))
                if len(T) > 0:
                    self.img[i][j] = T
                else:
                    self.img[i][j] = None

    def copy(self):
        return deepcopy(self)

    def to_image(self):
        return self.tis.to_image(self.img)


def generate(n: int, m: int, tis: TIS, verbose:bool, log:bool):
    active = deque()
    active.append(Image(n, m, tis))
    if log:
        pop_history = []
        img_done = []  # a list of time steps when images terminated
        _time_step = 0
    if verbose:
        i = 0
        ith = 0
    while len(active) > 0:
        if verbose:
            if i % 1000 == 0:
                print(len(active))
            i += 1
        if log:
            pop_history.append(len(active))
        img = active.popleft()
        x, y = img.min_entropy()
        for t in img[x][y]:
            fork = img.copy()
            fork.collapse(x, y, t)
            if fork.complete():
                if log:
                    img_done.append(_time_step)
                if verbose:
                    print(f'{ith}.png')
                    ith += 1
                yield fork
            else:
                active.append(fork)
        if log:
            _time_step += 1
    if log:
        plt.plot(pop_history)
        plt.vlines(img_done, 0, max(pop_history) * 0.25, colors='r')
        plt.ylabel('# of possible images being collapsed')
        plt.xlabel('t')
        plt.title(f'{n}x{m} Population over lifetime of Generation algorithm')
        plt.savefig(f'{n}x{m} population plot.png')


def sudoku_dump(n: int, m: int, tis: TIS, path: str, verbose=False, log=False):
    if exists(path):
        rmtree(path)
    mkdir(path)
    mkdir(f'{path}/partial')
    for i, img in enumerate(generate(n, m, tis, verbose, log)):
        out = img.to_image()
        if img.good():
            out.save(f"{path}/{i}.png")
        else:
            out.save(f"{path}/partial/{i}.png")
