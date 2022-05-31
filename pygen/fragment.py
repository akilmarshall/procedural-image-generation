from itertools import product
from os import mkdir
from os.path import exists
from shutil import rmtree

from tqdm import tqdm


class Fragment:
    '''
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

    def _core(self, i):
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
    
    def _yield(self, a, b, c, d, e, f, g, h, i):
        return [
                [a, d, g],
                [b, e, h],
                [c, f, i],
               ]

    def center_fragment(self, i):
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
                yield [
                        [k, c, m],
                        [b, i, d],
                        [h, a, n],
                      ]
                

    def corner_fragment(self, a):
        '''
        3x3 Fragments with fixed corners:

        abc
        def
        ghi

        a is fixed

        b = a0
        d = a3

        e = d intersection b
        f = e0
        h = e3

        i = h intersection f
        g = d intersection h
        c = b intersection f
        '''
        assert 0 <= a < self.tid.n
        B = self.tid.nids(a, 0)
        D = self.tid.nids(a, 3)
        
        for b, d in product(B, D):
            for e in self.tid.intersect(b, 3, d, 0):
                F = self.tid.nids(e, 0) 
                H = self.tid.nids(e, 3) 
                for f, h in product(F, H):
                    I = self.tid.intersect(h, 0, f, 3) 
                    G = self.tid.intersect(d, 3, h, 2)
                    C = self.tid.intersect(b, 0, f, 1)
                    for i, g, c in product(I, G, C):
                        yield self._yield(a, b, c, d, e, f, g, h, i)

    def side_fragment(self, b):
        '''
        3x3 Fragments with fixed sides:

        abc
        def
        ghi

        b is fixed

        C = b0
        A = b2
        E = b3

        D = a3 intersect e2
        F = e0 intersect c3
        H = e3

        G = d3 intersect h2
        I = h0 intersect f3
        '''
        C = self.tid.nids(b, 0)
        A = self.tid.nids(b, 2)
        E = self.tid.nids(b, 3)
        for a, c, e in product(A, C, E):
            D = self.tid.intersect(a, 3, e, 2)
            F = self.tid.intersect(e, 0, c, 3)
            H = self.tid.nids(e, 3)
            for d, f, h in product(D, F, H):
                G = self.tid.intersect(d, 3, h, 2)
                I = self.tid.intersect(h, 0, f, 3)
                for g, i in product(G, I):
                        yield self._yield(a, b, c, d, e, f, g, h, i)
    def _dump_all(self, f, name):
        print(name)
        if exists(name):
            rmtree(name)
        mkdir(name)
        for i in tqdm(range(self.tid.n)):
            local =f'{name}/{i}' 
            mkdir(local)
            for n, frag in enumerate(f(i)):
                self.tid.to_image(frag).save(f'{local}/{n}.png')

    def dump_all_center_fragment(self):
        self._dump_all(self.center_fragment, 'Center Fragments')

    def dump_all_corner_fragment(self):
        self._dump_all(self.corner_fragment, 'Corner Fragments')

    def dump_all_side_fragment(self):
        self._dump_all(self.side_fragment, 'Side Fragments')

    def dump_all_center_core(self):
        self._dump_all(self._core, 'Center Core')

