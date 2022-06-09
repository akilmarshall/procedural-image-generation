from pygen.util import TIS
from pygen.fragment import Fragment
from itertools import product
from copy import deepcopy
from collections import deque
from os import mkdir
from os.path import exists
from shutil import rmtree


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
            yield 1, x, y + 1
        if x > 0 and isinstance(self.img[x - 1][y], set):
            yield 2, x - 1, y
        if y > 0 and isinstance(self.img[x][y - 1], set):
            yield 3, x, y - 1

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


def generate(n: int, m: int, tis: TIS):
    active = deque()
    active.append(Image(n, m, tis))
    while len(active) > 0:
        img = active.popleft()
        x, y = img.min_entropy()
        for t in img[x][y]:
            fork = img.copy()
            fork.collapse(x, y, t)
            if fork.complete():
                yield fork.to_image()
            else:
                active.append(fork)


def sudoku_dump(n: int, m: int, tis: TIS, path: str):
    if exists(path):
        rmtree(path)
    mkdir(path)
    for i, img in enumerate(generate(n, m, tis)):
        img.save(f"{path}/{i}.png")
