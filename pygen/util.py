import json
from os import mkdir
from os.path import exists
from shutil import rmtree

from PIL import Image, ImageDraw
from tqdm import tqdm
from itertools import product


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
            self._setup(tid["mapping"])

    def _setup(self, mapping):
        self.mapping = []
        for data in mapping:
            neighbors = []
            for n in data:
                neighbors.append(n["data"])
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
        ids = []
        for (i, x) in enumerate(self.mapping[t][n]):
            if x > 0:
                ids.append(i)
        return ids

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
        for x in range(cols):
            for y in range(rows):
                h = x * self.width
                k = y * self.height
                t = fragment[x][y]
                if t is not None:
                    img.paste(self.tiles[t], box=(h, k))

        return img
