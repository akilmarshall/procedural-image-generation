from itertools import product
from os import mkdir
from os.path import exists
from shutil import rmtree

from tqdm import tqdm


class FragmentCenter:
    '''
    3x3 Fragments with fixed centers:

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
            K = intersect(b,2,c,1)
            M = intersect(c,3,d,2)
            N = intersect(d,0,a,3)
            for h, k, m, n in product(H, K, M, N):
                # h top right
                # k top left
                # n bottom right
                # m bottom left
                # a right
                # b top
                # c left
                # d bottom
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
        for i in tqdm(range(self.tid.n)):
            local =f'{path}/{i}' 
            mkdir(local)
            for n, frag in enumerate(self.fragment(i)):
                self.tid.to_image(frag).save(f'{local}/{n}.png')
    def dump_all_cores(self):
        path = 'cores'
        if exists(path):
            rmtree(path)
        mkdir(path)
        for i in tqdm(range(self.tid.n)):
            local =f'{path}/{i}' 
            mkdir(local)
            for n, core in enumerate(self.core(i)):
                self.tid.to_image(core).save(f'{local}/{n}.png')
