import json
from itertools import product
from PIL import Image

class TIS:
    def __init__(self, path='TIS'):
        self.path = path
        with open('TIS/TIS.json', 'r') as f:
            tid = json.load(f)
            self.n = tid['n']
            self.width = tid['width']
            self.height = tid['height']
            self._setup(tid['mapping'])

    def _setup(self, mapping):
        self.mapping = []
        for data in mapping:
            neighbors = []
            for n in data:
                neighbors.append(n['data'])
            self.mapping.append(neighbors)
        self.tiles = []
        for i in range(self.n):
            self.tiles.append(Image.open(f'{self.path}/tiles/{i}.png'))


    def _nid(self, t, n):
        assert 0 <= t < self.n
        assert 0 <= n < 4
        ids = []
        for (i,x) in enumerate(self.mapping[t][n]):
            if x > 0:
                ids.append(i)
        return ids

class Fragment:
    '''
    kbh
    cfa
    mdn

    h is constrained by (a1,b0)
    k is constrained by (b0,c1)
    m is constrained by (c3,d2)
    n is constrained by (d0,a3)

    f is fixed, {a, b, c, d} can be selected directly from f's mapping.
    - compute all possible fragments for each fixed center
    - how many are there?
    - convert fragment to Image
    '''
    def __init__(self, tid):
        self.tid = tid

    def n_fragmaent(self, i):
        assert 0 <= i < self.tid.n
        A = self.tid._nid(i, 0)
        B = self.tid._nid(i, 1)
        C = self.tid._nid(i, 2)
        D = self.tid._nid(i, 3)
        return len(A) * len(B) * len(C) * len(D)
    
    def all_fragment(self, i):
        assert 0 <= i < self.tid.n
        A = self.tid._nid(i, 0)
        B = self.tid._nid(i, 1)
        C = self.tid._nid(i, 2)
        D = self.tid._nid(i, 3)

        def intersect(u, x, v, y):
            return set(self.tid.mapping[u][x]).intersection(set(self.tid.mapping[v][y]))
        for a, b, c, d in product(A, B, C, D):
            H = intersect(a,1,b,0)
            K = intersect(b,0,c,1)
            M = intersect(c,3,d,2)
            N = intersect(d,0,a,3)
            for h, k, m, n in product(H, K, M, N):
                '''
                kbh
                cia
                mdn
                '''
                img = [
                        [k, b, h],
                        [c, i, a],
                        [m, d, n],
                        ]
                yield img

        yield None

    def to_image(self, fragment):
        height = len(fragment)
        width = len(fragment[0])
        img = Image.new('RGBA', (width * self.tid.width, height * self.tid.height), color=0)
        for x in range(width):
            for y in range(height):
                h = x * self.tid.width
                k = y * self.tid.height
                t = fragment[x][y]
                img.paste(self.tid.tiles[t], box=(h, k))

        return img


tid = TIS()
frag = Fragment(tid)
# for i in range(tid.n):
#     print(frag.n_fragmaent(i))
