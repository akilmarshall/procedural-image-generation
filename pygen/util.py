import json
from os import mkdir
from os.path import exists
from shutil import rmtree

from PIL import Image
from tqdm import tqdm


class TIS:
    '''
    Tiled Image Statistics. 
    Loads TIS as created by the tit tool, offers useful methods to access TIS data
    '''
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

    def nids(self, t, n) -> list[int]:
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

    def neighbors(self, i) -> list[list[int]]:
        '''
        For a tile i, return a list of its neighbor lists (set)
        [i0, i1, i2, i3] where in is a list (set)
        '''
        assert 0 <= i < self.n
        out = []
        for n in range(4):
            out.append(self.nids(i, n))
        return out

    def dump_all_neighbor(self):
        '''
        Debug method, dump all tiles and their images in a directory './neigbors/'
        '''
        path = 'neighbors'
        if exists(path):
            rmtree(path)
        mkdir(path)
        for i in tqdm(range(self.n)):
            local =f'{path}/{i}' 
            mkdir(local)
            self.tiles[i].save(f'{local}/{i}.png')
            for n, nids in enumerate(self.neighbors(i)):
                final = f'{local}/{n}'
                mkdir(final)
                for nid in nids:
                    self.tiles[nid].save(f'{final}/{nid}.png')

    def to_image(self, fragment) -> Image.Image:
        '''
        convert a id matrix to Image
        '''
        height = len(fragment)
        width = len(fragment[0])
        img = Image.new('RGBA', (width * self.width, height * self.height), color=0)
        for x in range(width):
            for y in range(height):
                h = x * self.width
                k = y * self.height
                t = fragment[x][y]
                if t is not None:
                    img.paste(self.tiles[t], box=(h, k))

        return img
