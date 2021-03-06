from itertools import product
import json
from os import mkdir
from os.path import exists
from random import choice, randint
from shutil import rmtree
from copy import deepcopy

from PIL import Image, ImageDraw
import numpy as np
from tqdm import tqdm


class TIS:
    """
    Tiled Image Statistics.
    Loads TIS as created by the tit binary
    """

    def __init__(self, path="TIS"):
        self.path = path
        with open("TIS/TIS.json", "r") as f:
            tid = json.load(f)
            self.n = tid["n"]
            self.width = tid["width"]
            self.height = tid["height"]
            self._setup(tid["neighborhoods"])

    def _setup(self, neighborhoods):
        self.mapping = []
        for n in neighborhoods:
            neighbors = n['neighbors']
            self.mapping.append(neighbors)
        self.tiles = []

        for i in range(self.n):
            self.tiles.append(Image.open(f"{self.path}/tiles/{i}.png"))

    def __call__(self, tid, direction):
        """
        Shorthand to the Neighbor function
        tile id -> direction -> [tile id]
        """
        return self.nids(tid, direction)

    def nids(self, t, n) -> list[int]:
        """
        Neighbor function.
        tile id -> direction -> neighbor list
        """
        assert 0 <= t < self.n
        assert 0 <= n < 4
        return self.mapping[t][n]

    def intersect(self, u, x, v, y):
        """
        Compute the intersection of u_x and v_y.
        tile ids: {u, v}
        neigbor set {x, y}
        """
        assert 0 <= u < self.n
        assert 0 <= v < self.n
        assert x in [0, 1, 2, 3]
        assert y in [0, 1, 2, 3]
        A = set(self.nids(u, x))
        B = set(self.nids(v, y))
        return A.intersection(B)

    def neighbors(self, i):
        """
        For a tile i, return a list of its neighbor lists (set)
        [i0, i1, i2, i3] where in is a list (set)
        """
        assert 0 <= i < self.n
        out = []
        for n in range(4):
            out.append(self.nids(i, n))
        return out

    def dump_tile_sheet(self, fname, dim=None, gap=0):
        """
        Save a tile sheet to file
        fname   file name of the tilesheet image
        dim     optionally specify how many rows and cols to use
                for the tilesheet
        gap     number of pixels between the tiles
        """

        def nice_dimensions(n) -> tuple[int, int]:
            for i in range(n):
                if i**2 >= n:
                    return (i, i)
            return (n, 1)

        if dim is None:
            x, y = nice_dimensions(len(self.tiles))
        else:
            x, y = dim

        W = gap + self.width
        H = gap + self.height
        img = Image.new("RGBA", ((1 + x) * W, (1 + y) * H), color=0)
        for t, (h, k) in zip(self.tiles, product(range(x), range(y))):
            img.paste(t, (h * W, k * H))
        img.save(fname)

    def dump_all_neighbor_split(self):
        """
        Debug method, dump all tiles and their images in a directory split into sub directories './neigbors/'
        """
        print("Neighbors")
        path = "neighbors"
        if exists(path):
            rmtree(path)
        mkdir(path)
        for i in tqdm(range(self.n)):
            local = f"{path}/{i}"
            mkdir(local)
            self.tiles[i].save(f"{local}/{i}.png")
            for n, nids in enumerate(self.neighbors(i)):
                final = f"{local}/{n}"
                mkdir(final)
                for nid in nids:
                    self.tiles[nid].save(f"{final}/{nid}.png")

    def dump_all_neighbor(self):
        """
        Debug method, dump all tiles and their images in a directory './neigbors/'
        """
        print("Neighbors")
        path = "neighbors"
        if exists(path):
            rmtree(path)
        mkdir(path)
        for i in tqdm(range(self.n)):
            neighbors = [None] * 4
            for n, nids in enumerate(self.neighbors(i)):
                neighbors[n] = nids
            gap_w = self.width // 8
            gap_h = self.height // 8
            margin = 2 * max(self.width, self.height)
            w = 1 + len(neighbors[0]) + len(neighbors[2])
            h = 1 + len(neighbors[1]) + len(neighbors[3])

            width = (w * self.width) + (2 * margin) + (w * gap_w)
            height = (h * self.height) + (2 * margin) + ((h - 1) * gap_h)
            img = Image.new("RGBA", (width, height), color=0)
            d = ImageDraw.Draw(img)

            x = width // 2
            y = height // 2
            dx = (self.width / 2) + gap_w
            dy = (self.height / 2) + gap_h
            img.paste(self.tiles[i], box=(x, y))

            for j, a in enumerate(neighbors[0], start=1):
                l = x + j * (gap_w + self.width)
                m = y
                img.paste(self.tiles[a], box=(l, m))
            for j, a in enumerate(neighbors[2], start=1):
                l = x - j * (gap_w + self.width)
                m = y
                img.paste(self.tiles[a], box=(l, m))
            for j, a in enumerate(neighbors[1], start=1):
                l = x
                m = y - j * (gap_h + self.height)
                img.paste(self.tiles[a], box=(l, m))
            for j, a in enumerate(neighbors[3], start=1):
                l = x
                m = y + j * (gap_h + self.height)
                img.paste(self.tiles[a], box=(l, m))
            img.save(f"{path}/{i}.png")

    def to_image(self, fragment):
        """
        convert a id matrix to Image
        """
        cols = len(fragment)
        rows = len(fragment[0])
        img = Image.new("RGBA", (cols * self.width, rows * self.height), color=0)
        for x, y in product(range(cols),range(rows)):
            h = x * self.width
            k = y * self.height
            t = fragment[x][y]
            if t is not None:
                img.paste(self.tiles[t], box=(h, k))

        return img
"""
hashable representations for vector and matrix fragments
"""
def V(a:int|None, b:int|None, d:int):
    """2 element vector, orientation described by d. """
    return a, b, d
def M(a:int|None, b:int|None, c:int|None, d:int|None):
    """
    2x2 square matrix,
    a b
    c d
    """
    return a, b, c, d

class Individual:
    """
    Individual image for tinkering.
    General datastructure representing images for a number of
    algorithms.
    """
    def __init__(self, cols:int, rows:int, tis:TIS, rand=False):
        self.cols = cols
        self.rows = rows
        self.data = np.full((self.cols, self.rows), None)
        self.n = tis.n
        self.nids = tis.nids

        self.reset(rand)


    def reset(self, rand=False):
        self._start = deepcopy(self.data)
        self._change_history = []
        if rand:
            self._rand_init()

    def seed(self, x:int, y:int, t:None|int=None):
        """Seed the image at (x, y) with t (otherwise uniform rand). """
        if t is None:
            t = randint(0, self.n - 1)
            self.data[x % self.cols][y % self.rows] = t
        else:
            self.data[x % self.cols][y % self.rows] = t

    def to_gif(self, tis:TIS, fname:str):
        frames = [tis.to_image(self._start)]
        img = deepcopy(self._start)
        for x, y, t in self._change_history:
            img[x][y] = t
            frames.append(tis.to_image(img))
        frames[0].save(fname,
			save_all = True, append_images = frames[1:],
			optimize = False)

    def set(self, x, y, t):
        # assert(x < self.cols and y < self.rows and t < self.n)
        if x < self.cols and y < self.rows:
            self.data[x][y] = t 
            self._change_history.append((x, y, t))


    def simple_conformity(self, x:int, y:int, t:int|None=None) -> int:
        """
        for a defined position or hypothetical query compute conformity
        """
        score = 0
        if t is None:
            t = self.data[x][y]
        for nid, i, j in self._neighbors(x, y):
            if self.data[i][j] in self.nids(t, nid):
                score += 1
        return score

    def conformity(self, x:int, y:int) -> int | None:
        """
        Compute the extended conformity at (x, y)
        """
        if t := self.data[x][y]:
            return self.simple_conformity(x, y, t)

    def conform(self, x:int, y:int):
        """(x, y)'s neighborbood is made to conform with it w.r.t. tis. """
        t = self.data[x][y]
        values = {}
        for (nid, i, j) in self._neighbors(x, y):
            nids = self.nids(t, nid) 
            if t not in nids and nids:
                self.set(i, j, choice(nids))
                values[nid] = choice(nids)

    def fitness(self) -> int:
        """Compute the fitness, aka the sum of each tiles conformity. """
        score = 0
        for x, y in self._positions():
            if v := self.conformity(x, y):
                score += v 
        return score

    def mutate(self):
        """Set a random location to a random tile. """
        x, y = self._rand_pos()
        t = self._rand_individual()
        self.set(x, y, t)

    def mutate_improve(self):
        """A random position's neighbors are made to conform to the neighbor function. """
        x, y = self._rand_pos()
        self.conform(x, y)

    def min_conform(self) -> tuple[int, int] | None:
        """Return the position with minimum conformity or None. """
        c = None
        i, j = -1, -1
        for x, y in self._positions():
            if v := self.conformity(x, y):
                if v == 0:
                    return x, y
                if v < 4 and (c is None or v < c):
                    c = v
                    i, j = x, y
        if c is not None: 
            return i, j

    def undefined(self):
        """return each point (x, y) that is undefined in the image (self.data). """
        for x, y in self._positions():
            if self.data[x][y] is None:
                yield x, y

    def H(self, x:int, y:int):
        """H function, return the adjacent tiles to (x, y) and return an iterable of (i, j, id). """
        for t, i, j in self._neighbors(x, y):
            yield i, j, (t + 2) % 4

    def potential(self, x:int, y:int, most=True):
        """Return a set of points, the best possible choices. """
        # t = self.data[x][y]
        # if t is None:
        #     H = list(self.H(x, y))
        #     match len(H):
        #         case 0: return []
        #         case 1: return H[0]
        #         case n: 
        #             U = list(reduce(lambda a, b: set(a).intersection(set(b)), H))
        #             if len(U) > 0:
        #                 return U 
        #             vs = []
        #             for i, _ in enumerate(H):
        #                 J = list(set(H[:i]).intersection(  set(H[i:] )))
        #                 if len(J) > 0:
        #                     vs.append((i, J, len(J)))

        #             if len(vs) > 0:
        #                 vs.sort(key=lambda a:a[2], reverse=most)
        #                 return vs[0]
        #             J = []
        #             for h in H:
        #                 J.append((len(h), h))
        #             J.sort(key=lambda a:a[0], reverse=most)
        #             return J[0]
        # else:
        #     pass
            # s = 0
            # for d, i, j in self._neighbors(x, y):
            #     nid = self.data[i][j]
            #     if nid in self.nids(t,d):
            #         s += 1
            # return s

    def rule_match_candidates(self):
        """
        yields vectors from the image that could satisfy a rule,
        of the form (a, None) or (None, b)
        """
        for v in self._rule_match_candidate_V():
            if (v[1][0] is None) ^ (v[1][1] is None):
                yield v

    def rule_query(self, x:int, y:int):
        if x + 1 < self.cols - 1:
            a = self.data[x][y]
            b = self.data[x + 1][y]
            yield V(a, b, 0)
        if x - 1 >= 0:
            a = self.data[x][y]
            b = self.data[x - 1][y]
            yield V(a, b, 2)
        if y + 1 < self.rows - 1:
            a = self.data[x][y]
            b = self.data[x][y + 1]
            yield V(a, b, 1)
        if y - 1 >= 0:
            a = self.data[x][y]
            b = self.data[x][y - 1]
            yield V(a, b, 3)

    def empty(self) -> bool:
        for x, y in self._positions():
            if self.data[x][y] is None:
                return False
        return True

    def _rule_match_candidate_V(self):
        for x, y in self._positions():
            if x + 1 < self.cols - 1:
                a = self.data[x][y]
                b = self.data[x + 1][y]
                yield (x, y), V(a, b, 0)
            if x - 1 >= 0:
                a = self.data[x][y]
                b = self.data[x - 1][y]
                yield (x, y), V(a, b, 2)
            if y + 1 < self.rows - 1:
                a = self.data[x][y]
                b = self.data[x][y + 1]
                yield (x, y), V(a, b, 1)
            if y - 1 >= 0:
                a = self.data[x][y]
                b = self.data[x][y - 1]
                yield (x, y), V(a, b, 3)

    def _rule_match_candidate_M(self):
        for x, y in self._positions():
            i = self.data[x][y]
            # upper right
            # a u
            # i b
            if x + 1 < self.cols and y - 1 >= 0:
                a = self.data[x][y - 1]
                b = self.data[x + 1][y]
                u = self.data[x + 1][y - 1]
                yield (x, y), M(a, u, i, b)
            # upper left
            # u a
            # b i
            if x - 1 >= 0 and y - 1 >= 0:
                a = self.data[x][y - 1]
                b = self.data[x - 1][y]
                u = self.data[x - 1][y - 1]
            # bottom right
            # i a
            # b u
            if x + 1 < self.cols - 1 and y + 1 < self.rows - 1:
                a = self.data[x + 1][y]
                b = self.data[x][y + 1]
                u = self.data[x + 1][y + 1]
                yield (x, y), M(i, a, b, u)
            # bottom left
            # a i
            # u b
            if x - 1 >= 0 and y + 1 < self.rows - 1:
                a = self.data[x - 1][y]
                b = self.data[x][y + 1]
                u = self.data[x - 1][y + 1]
                yield (x, y), M(a, i, u, b)

    def _positions(self):
        """Return an iterator over all positions. """
        return product(range(self.cols), range(self.rows))

    def _empty_positions(self):
        """Return an iterator over all empty positions. """
        for x, y in self._positions():
            if self.data[x][y] is None:
                yield x, y

    def _empty_neighbors(self, x:int, y:int):
        for _, i, j in self._neighbors(x, y):
            if self.data[i][j] is None:
                yield i, j

    def _defined_neighbors(self, x:int, y:int):
        for _, i, j in self._neighbors(x, y):
            if self.data[i][j] is not None:
                yield i, j

    def _neighbors(self, x, y):
        """Return an iterator of the neighbors of (x, y) on a torus. """
        yield 0, (x + 1) % self.cols, y
        yield 3, x, (y + 1) % self.rows
        yield 2, (x - 1) % self.cols, y
        yield 1, x, (y - 1) % self.rows

    def _rand_pos(self) -> tuple[int, int]:
        """Return a random position. """
        return randint(0, self.cols - 1), randint(0, self.rows - 1)
    
    def _rand_individual(self) -> int:
        """Return a random valid individual. """
        return randint(0, self.n - 1)

    def _rand_init(self):
        """Set each position to a random valid value. """
        for x, y in self._positions():
            self.data[x][y] = self._rand_individual()

    def _max_score(self) -> int:
        """Return the maximum conformity score, aka each tile is fully accepted. """
        return 4 * self.cols * self.rows
