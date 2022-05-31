# tiled-image-tool

This is the tiled-image-tool (tit) for computing statistics from tiled images
and using it for procedural image generation.

## Tiled Image Data

## Tiled Image Statistics

## Data Pipeline

(dots diagram coming soon)

tiled_image.png -> TIS(TID) [memory/disk]

TIS(TID) -> Algorithm -> new_image.png

## Image Generation

### pygen

A module to facilitate quick experimenting of image generation strategies.

### Fragments

A fragment is a 3x3 tiled image with a single fixed tile.

A B C
D E F
G H I

Center Fragment:

The center tile is fixed, {F, B, D, H} can be directly inferred from E via TIS.

  b
d E f
  h
  
The above is known as the set of core images of E where {f, b, d, h} vary over {F, B, D, H}.
For any core its corners are varied over the set intersections of it's neighbors.

A = B \intersection D
C = B \intersection F
G = D \intersection I
I = H \intersection F

### Questions

- Are all fragment generation strategies made equal? Does it matter if I fix the center or a corner?

## Todo

- pursue image generation via fragment database. TIS -> DB -> Image GEN
    - can this be done without the database? TIS -> Image GEN 
