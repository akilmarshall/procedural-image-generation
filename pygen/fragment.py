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
                yield [
                        [k, c, m],
                        [b, i, d],
                        [h, a, n],
                      ]
                


    def dump_all_fragment(self):
        print('Center Fragments')
        path = 'fragments (center)'
        if exists(path):
            rmtree(path)
        mkdir(path)
        for i in tqdm(range(self.tid.n)):
            local =f'{path}/{i}' 
            mkdir(local)
            for n, frag in enumerate(self.fragment(i)):
                self.tid.to_image(frag).save(f'{local}/{n}.png')

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
class FragmentCorner:
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
    def __init__(self, tid):
        self.tid = tid

    
    def fragment(self, a):
        '''
        generator for the fragments seeded with a
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
                        yield [
                                [a, d, g],
                                [b, e, h],
                                [c, f, i],
                              ]


    def dump_all_fragment(self):
        print('Corner Fragments')
        path = 'fragments (corner)'
        if exists(path):
            rmtree(path)
        mkdir(path)
        for i in tqdm(range(self.tid.n)):
            local =f'{path}/{i}' 
            mkdir(local)
            for n, frag in enumerate(self.fragment(i)):
                self.tid.to_image(frag).save(f'{local}/{n}.png')
