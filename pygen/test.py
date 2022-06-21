"""
Module for creating test images
"""
from PIL import Image
from itertools import product
from random import randint

def chessboard(n, m, fname, tile=(16, 16)):
    tx, ty = tile
    h, k = tx * n, ty * m 
    img = Image.new('RGBA', (h, k), color="black") 
    black = Image.new('RGBA', tile, color="black")
    white = Image.new('RGBA', tile, color="white")
    tiles = [black, white]
    for (i, (x, y)) in enumerate(product(range(n), range(m))):
        a, b = x * tx, y * ty
        img.paste(tiles[i % 2], (a, b))
    img.save(fname)

def rand_n(col, row, n, fname, tile=(16, 16)):
    tiles = list(map(lambda c: Image.new('RGBA', tile, color=c), ["black", "white", "red", "blue", "green", "purple"]))
    tx, ty = tile
    h, k = tx * col, ty * row 
    img = Image.new('RGBA', (h, k)) 
    for (x, y) in product(range(col), range(row)):
        a, b = x * tx, y * ty
        img.paste(tiles[randint(0, n - 1)], (a, b))
    img.save(fname)
