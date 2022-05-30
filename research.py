import json
from itertools import product
from PIL import Image
from os import mkdir
from os.path import exists
from shutil import rmtree

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


    def nids(self, t, n):
        '''
        for tile t and neigbor n, return a list (set) of neighbor ids
          1
        2 t 0
          3
        '''
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
        '''
        for the tile i, how many fragments can it generate?
        '''
        assert 0 <= i < self.tid.n
        A = self.tid.nids(i, 0)
        B = self.tid.nids(i, 1) 
        C = self.tid.nids(i, 2)
        D = self.tid.nids(i, 3)
        a = len(A)
        b = len(B)
        c = len(C)
        d = len(D)
        print(a,b,c,d,a*b*c*d)
    
    def fragment(self, i):
        '''
        generator for the fragments seeded with i
        '''
        assert 0 <= i < self.tid.n
        A = self.tid.nids(i, 0)
        B = self.tid.nids(i, 1)
        C = self.tid.nids(i, 2)
        D = self.tid.nids(i, 3)

        def intersect(u, x, v, y):
            A = set(self.tid.nids(u, x))
            B = set(self.tid.nids(v, y))
            return A.intersection(B)
        for a, b, c, d in product(A, B, C, D):
            H = intersect(a,1,b,0)
            K = intersect(b,0,c,1)
            M = intersect(c,3,d,2)
            N = intersect(d,0,a,3)
            for h, k, m, n in product(H, K, M, N):
                img = [
                        [k, c, m],
                        [b, i, d],
                        [h, a, n],
                        ]
                yield img

    def core(self, i):
        '''
        generator for the cores seeded with i, i.e. only the primary infered tiles are generated
        _ 1 _
        2 i 0
        _ 3 _
        '''
        assert 0 <= i < self.tid.n
        A = self.tid.nids(i, 0)
        B = self.tid.nids(i, 1)
        C = self.tid.nids(i, 2)
        D = self.tid.nids(i, 3)
        for a, b, c, d in product(A, B, C, D):
                img = [
                        [None, c, None],
                        [b, i, d],
                        [None, a, None],
                        ]
                yield img



    def dump_all_fragment(self):
        path = 'fragments'
        if exists(path):
            rmtree(path)
        mkdir(path)
        for i in range(self.tid.n):
            print(f'{i+1}/{self.tid.n}')
            local =f'{path}/{i}' 
            mkdir(local)
            for n, frag in enumerate(self.fragment(i)):
                self.to_image(frag).save(f'{local}/{n}.png')
    def dump_all_cores(self):
        path = 'cores'
        if exists(path):
            rmtree(path)
        mkdir(path)
        for i in range(self.tid.n):
            print(f'{i+1}/{self.tid.n}')
            local =f'{path}/{i}' 
            mkdir(local)
            for n, core in enumerate(self.core(i)):
                self.to_image(core).save(f'{local}/{n}.png')


    def neighbors(self, i):
        assert 0 <= i < self.tid.n
        out = []
        for n in range(4):
            out.append(self.tid.nids(i, n))
        return out
    def dump_all_neighbor(self):
        path = 'neighbors'
        if exists(path):
            rmtree(path)
        mkdir(path)
        for i in range(self.tid.n):
            print(f'{i+1}/{self.tid.n}')
            local =f'{path}/{i}' 
            mkdir(local)
            self.tid.tiles[i].save(f'{local}/{i}.png')
            for n, nids in enumerate(self.neighbors(i)):
                final = f'{local}/{n}'
                mkdir(final)
                for nid in nids:
                    self.tid.tiles[nid].save(f'{final}/{nid}.png')

    def to_image(self, fragment) -> Image.Image:
        '''
        convert a id matrix to Image
        '''
        height = len(fragment)
        width = len(fragment[0])
        img = Image.new('RGBA', (width * self.tid.width, height * self.tid.height), color=0)
        for x in range(width):
            for y in range(height):
                h = x * self.tid.width
                k = y * self.tid.height
                t = fragment[x][y]
                if t is not None:
                    img.paste(self.tid.tiles[t], box=(h, k))

        return img


tid = TIS()
frag = Fragment(tid)
# frag.dump_all_cores()
frag.dump_all_fragment()
