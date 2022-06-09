from itertools import product
from random import choice


class Image:
    def __init__(self, n, tid):
        self.n = n
        self.tid = tid
        self.img = {(x, y): None for x, y in product(range(self.n), range(self.n))}

    def __call__(self):
        out = []
        for x in range(self.n):
            row = []
            for y in range(self.n):
                row.append(self[(x, y)])
            out.append(row)
        return out

    def __getitem__(self, A):
        x, y = A
        assert 0 <= x < self.n
        assert 0 <= y < self.n
        return self.img[A]

    def assign(self, x, y, t):
        assert 0 <= x < self.n
        assert 0 <= y < self.n
        assert 0 <= t < self.tid.n
        self.img[(x, y)] = t

    def odd(self):
        for (x, y) in self.img:
            if x + y % 2 == 1:
                yield (x, y, self.img[(x, y)])
    def even(self):
        for (x, y) in self.img:
            if x + y % 2 == 0:
                yield (x, y, self.img[(x, y)])

    def neighbors(self, x, y):
        assert 0 <= x < self.n
        assert 0 <= y < self.n
        out = []
        if x + 1 < self.n:
            out.append((0, x + 1, y))
        if y + 1 < self.n:
            out.append((1, x, y + 1))
        if x - 1 >= 0:
            out.append((2, x - 1, y))
        if y - 1 >= 0:
            out.append((3, x, y - 1))
        return out

    def defined_neighbors(self, x, y):
        n = 0
        for _, h, k in self.neighbors(x, y):
            if self[(h, k)] is not None:
                n += 1
        return n

    def neighbor_intersect(self, x, y):
        ids = None
        for n, h, k in self.neighbors(x, y):
            t = self.img[(h, k)]
            if t is not None:
                A = set(self.tid.nids(t, (n + 2) % 4))
                if ids is None:
                    ids = A
                else:
                    ids.intersection(A)
        return ids

    def empty_tiles(self):
        for x, y in product(range(self.n), range(self.n)):
            if self[(x, y)] is None:
                yield (x, y)

    def complete(self):
        for x, y in product(range(self.n), range(self.n)):
            if self[(x, y)] is not None:
                return False
        return True




class Square:
    def __init__(self, n, tid):
        self.n = n
        self.tid = tid

    def generate(self, i):
        img = Image(self.n, self.tid)
        # seed
        img.assign(0, 0, i)
        while not img.complete():
            for x, y in img.empty_tiles():
                available = img.neighbor_intersect(x, y)
                if len(available) > 0:
                    img.assign(x, y, choice(list(available)))
        return img



