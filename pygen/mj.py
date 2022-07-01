"""https://github.com/mxgmn/MarkovJunior. """
from PIL import Image as I
from .util import Individual, TIS, V
from collections import defaultdict
import numpy as np
from random import choice, shuffle
from itertools import product
from shutil import rmtree
from os import mkdir
from os.path import exists


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

PICO_8 = {
    "B" :"#000000",
    "I" :"#1D2B53",
    "P" :"#7E2553",
    "E" :"#008751",
    "N" :"#AB5236",
    "D" :"#5F574F",
    "A" :"#C2C3C7",
    "W" :"#FFF1E8",
    "R" :"#FF004D",
    "O" :"#FFA300",
    "Y" :"#FFEC27",
    "G" :"#00E436",
    "U" :"#29ADFF",
    "S" :"#83769C",
    "K" :"#FF77A8",
    "F" :"#FFCCAA"
    }

class Image:
    """
    An image for use in MarkovJunior
    """
    def __init__(self, cols:int, rows:int, pallet=PICO_8, tile=(16, 16), fill="B"):
        self.cols = cols
        self.rows = rows
        self.pallet = pallet
        self.w = tile[0]
        self.h = tile[1]

        self.setup(fill)

    def setup(self, fill:str):
        """Setup/reset the img and change history. """
        self.data = np.full((self.cols, self.rows), fill)
        self._init = np.full((self.cols, self.rows), fill)
        self._history = []

    def paste(self, x:int, y:int, img:np.ndarray, log=True):
        """
        Modify the image by pasting a sub image on to it, change is logged
        in self._history when log=True.
        """
        if log:
            self._history.append((x, y, img))
        self.data[x:x + img.shape[0], y:y + img.shape[1]] = img

    def region_query(self, x:int, y:int, shape:tuple[int, int]):
        return self.data[x:x + shape[0], y:y + shape[1]]

    def all_region(self, shape:tuple[int, int]):
        available = [_ for _ in product(range(self.cols), range(self.rows))]
        for x, y in available:
            r = self.region_query(x, y, shape)
            if r.shape == shape:
                yield r, (x, y)

    def to_image(self):
        img = I.new("RGBA", (self.w * self.cols, self.h * self.rows), color=0)
        for x, y in self._positions():
            if tile:=self._tile(self.data[x][y]):
                img.paste(tile, (x * self.w, y * self.h))
        return img

    def to_gif(self, fname:str):
        """Create a gif from the change history and initial state. """
        frames = []
        for img in self._frames():
            frames.append(img)
        frames[0].save(fname, save_all=True, append_images=frames[1:])

    def dump_frames(self, path='frame_dump'):
        if exists(path):
            rmtree(path)
        mkdir(path)
        for i, img in enumerate(self._frames()):
            img.save(f'{path}/{i}.png')


    def _replay(self):
        """Replay "history" and return an iterator of Image objects representing the paste history of the object. """
        img = Image(self.cols, self.rows, self.pallet, (self.w, self.h))
        for x, y, d in self._history:
            img.paste(x, y, d, False)
            yield img

    def _frames(self):
        for i in self._replay():
            yield i.to_image()
            
    def _positions(self):
        for x,y in product(range(self.cols),range(self.rows)):
            yield x, y

    def _tile(self, key):
        if key in self.pallet:
            return I.new("RGBA", (self.w, self.h), color=self.pallet[key])

class Algorithm:
    """
    A Markov Algorithm
    """
    def __init__(self):
        self.rules = []


    def add_rule(self, key:str, val:str):
        if len(key) == len(val):
            self.rules.append((key,val))

    def get_rule_image(self, rule:str):
        """Given a rule return it's image. """
        for (a, b) in self.rules:
            if a == rule:
                return b 

    def rule_match(self, img:Image) -> tuple[np.ndarray, np.ndarray] | None:
        """
        Identify the first rule that matches and return the pair
        (l, r) where l is embedded rule match and r is it's image.
        """
        for a, _ in self.rules:
            orientations = list(enumerate_rule_pair(a, self.get_rule_image(a)))
            shuffle(orientations)
            for l, r in orientations:
                for x, _ in img.all_region(l.shape):
                    if np.all(x == l):
                        return l, r

    def match_locations(self, rule:np.ndarray, img:Image):
        """
        Given a rule return all locations (upper left corner)
        in img that it matches. 
        """
        for r, (x, y) in img.all_region(rule.shape):
            try:
                if np.all(r == rule):
                    yield (x, y)
            except:
                import pdb
                pdb.set_trace()

    def step(self, img:Image) -> bool:
        """
        One step of the algo.
        """
        # find the first matching rule
        if (rule := self.rule_match(img)) is not None:
            l, r = rule
            # enumerate it's locations
            locations = list(self.match_locations(l, img))
            if len(locations) > 0:
                x, y = choice(locations)
                region = img.region_query(x, y, l.shape)
                if np.all(l == region):
                    img.paste(x, y, r)
                    return True
        return False

    def run(self, img):
        while self.step(img):
            """Hi mom. """

    def __call__(self, img:Image):
        self.run(img)


def enumerate_rule(rule:str):
    """
    Given the string repr of a rule, return it's 4 topological embeddings.
    The embedded string representing D4
    """
    a = np.array([[s for s in rule]])
    yield a
    yield np.flip(a)
    yield a.transpose()
    yield np.flip(a.transpose())

def enumerate_rule_pair(a:str, b:str):
    assert(len(a) == len(b))
    for l, r in zip(enumerate_rule(a), enumerate_rule(b)):
        yield l, r

def BW() -> Algorithm:
    a = Algorithm()
    a.add_rule("B", "W")
    return a

def WBWW() -> Algorithm:
    a = Algorithm()
    a.add_rule("WB", "WW")
    return a

def maze() -> Algorithm:
    a = Algorithm()
    a.add_rule("WBB", "WAW")
    return a

def self_avoid_walk() -> Algorithm:
    a = Algorithm()
    a.add_rule("RBB", "WWR")
    return a
