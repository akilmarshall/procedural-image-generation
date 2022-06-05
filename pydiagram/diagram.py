from itertools import product
from turtle import *

def nice_dimensions(n) -> tuple[int, int]:
    for i in range(n):
        if i**2 >= n:
            return (i, i)

def square(x, y, s):
    hideturtle()
    penup()
    goto(x, y)
    pendown()
    forward(s)
    right(90)
    forward(s)
    right(90)
    forward(s)
    right(90)
    forward(s)
    right(90)

def arrow(x, y):
    hideturtle()
    penup()
    goto(x, y)
    pendown()
    forward(30)
    shapesize(0.5, 0.5, 0.5)
    shape('triangle')
    showturtle()

def tile_sheet_to_image(n, fname):
    width, height = 16, 16
    pad = 8
    W = width + pad
    H = height + pad
    x, y = nice_dimensions(n)
    for ((h, k), _) in zip(product(range(x), range(y)), range(n)):
        square(h * W, k * H, 16)
    h, k = pos()
    arrow(h + 40, k - (H * y / 2))
    stamp()
    h, k = pos()
    square(h + 40, 0.5 * 160, 160)
    Screen().getcanvas().postscript(file=f'{fname}.ps')

def neighbor_position_diagram(fname, s=40):
    def V(x, l):
        hideturtle()
        setheading(90)
        penup()
        goto(x, 0)
        pendown()
        forward(l)
    def H(y, l):
        hideturtle()
        setheading(0)
        penup()
        goto(0, y)
        pendown()
        forward(l)

    Screen().bgcolor("white")
    V(s, s * 3)
    V(s * 2, s * 3)
    H(s, s * 3)
    H(s * 2, s * 3)
    s2 = s / 2
    s4 = s2 / 2
    pos = [(s2 + 2 * s, s2 + s), (s2 + s, s2 + 2 * s), (s2, s2 + s), (s2 + s, s2)]
    penup()
    goto(s2 + s, s2 + s - s4)
    write('t', align='center', font=('arial', 14, 'normal'))
    for i, (h, k) in enumerate(pos):
        goto(h, k - s4)
        write(f'{i}', align='center', font=('arial', 14, 'italic'))
    Screen().getcanvas().postscript(file=f'{fname}.ps')
