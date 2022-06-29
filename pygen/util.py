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

class Individual:
    """
    Individual image for tinkering.
    General datastructure representing images for a number of
    algorithms.
    """
    def __init__(self, n:int, m:int, tis:TIS):
        self.cols = n
        self.rows = m
        self.data = np.full((self.cols, self.rows), None)
        self._rand_init()
        self._max = tis.n
        self._start = deepcopy(self.data)
        self._change_history = []
        self.nids = tis.nids

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
        # assert(x < self.cols and y < self.rows and t < self._max)
        if x < self.cols and y < self.rows and t < self._max:
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

    def potential(self, x:int, y:int):
        """Return a set of points, the best possible choices. """
        t = self.data[x % self.cols][y % self.rows]
        if t is None:
            pass
        else:
            pass



    def _positions(self):
        """Return an iterator over all positions. """
        return product(range(self.cols), range(self.rows))

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
        return randint(0, self._max - 1)

    def _rand_init(self):
        """Set each position to a random valid value. """
        for x, y in self._positions():
            self.data[x][y] = self._rand_individual()

    def _max_score(self) -> int:
        """Return the maximum conformity score, aka each tile is fully accepted. """
        return 4 * self.cols * self.rows
