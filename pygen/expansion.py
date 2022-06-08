from .util import TIS
from itertools import chain
from .fragment import Fragment


class Store:
    '''
    A collection of fragments
    '''
    def __init__(self, tis:TIS):
        self.store = []
        fragment = Fragment(tis)
        for i in range(tis.n):
            for frag in chain(fragment.center_fragment(i), fragment.corner_fragment(i), fragment.side_fragment(i)):
                self.store.append(frag)
    def query(self, strip:list[int], edge:int):
        assert 0 <= edge < 4
        assert len(strip) == 3
        for frag in self.store:
            match edge:
                case 0:
                    if frag[0] == strip:
                        yield frag
                case 2:
                    if frag[2] == strip:
                        yield frag
                case 1:
                    if [frag[0][0], frag[1][0], frag[2][0]] == strip:
                        yield frag
                case 3:
                    if [frag[0][2], frag[1][2], frag[2][2]] == strip:
                        yield frag


class Expander:
    def __init__(self, tis: TIS):
        self.tis = tis

    def centerx(self, strip):
        assert len(strip) == 3
        # orientation is assumed,
        # probably should be described as an enum
        # to dictate the generation of the expanded vector
        out = [None] * 3
        for a in self.tis.nids(strip[1], 0):
            out[1] = a
            B = set(self.tis.nids(strip[0], 0)).intersection(set(self.tis.nids(a, 1)))
            C = set(self.tis.nids(strip[2], 0)).intersection(set(self.tis.nids(a, 3)))
            for b, c in zip(B, C):
                out[0] = b
                out[2] = c
                yield out

    def cornerx(self, strip, mirror=None):
        assert len(strip) == 3
        if mirror:
            self._cornerx_L(strip)
        else:
            self._cornerx_R(strip)

    def _cornerx_L(self, strip):
        out = [None] * 3
        for a in self.tis.nids(strip[0], 0):
            out[0] = a
            B = set(self.tis.nids(strip[1], 0)).intersection(set(self.tis.nids(a, 3)))
            for b in B:
                out[1] = b
                C = set(self.tis.nids(strip[2], 0)).intersection(set(self.tis.nids(b, 3)))
                for c in C:
                    out[2] = c
                    yield out

    def _cornerx_R(self, strip):
        out = [None] * 3
        for a in self.tis.nids(strip[2], 0):
            out[2] = a
            B = set(self.tis.nids(strip[1], 0)).intersection(set(self.tis.nids(a, 1)))
            for b in B:
                out[1] = b
                C = set(self.tis.nids(strip[0], 0)).intersection(set(self.tis.nids(b, 1)))
                for c in C:
                    out[0] = c
                    yield out

