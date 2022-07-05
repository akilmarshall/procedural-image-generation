# Procedural Image Generation

How can I turn a single image into more images that are somewhat like it?

## Todo

- implement tile sheet dump [rust]
- implement neighbor function visual dump [rust]
- write code to make animated gifs from MCI algorithms

## Examples

Using the following image as input 

<p align="center">
<img src=https://imgur.com/ZuOinkm.png/>
</p>
<p align = "center">minimal input example</p>

Made up of the following [tileset](https://github.com/akilmarshall/procedural-image-generation/wiki/Theory)

<p align="center">
<img src=https://imgur.com/CfTFzSk.png/>
</p>

It's [neighbor functions](https://github.com/akilmarshall/procedural-image-generation/wiki/Theory#neighbor-function) are visualized below

<p align="center">
<img src=https://imgur.com/GQAaMIr.png/>
</p>

### Constrained Backtracking Search

(this example uses [this](https://imgur.com/uFuMFEU.png) image as input)

Also known as [Wave Function Collapse](https://github.com/mxgmn/WaveFunctionCollapse) (tiled model)

When tasked with completed a fully uncollapsed image this algorithm's run time and output is enormous. It is often more interesting to provide it
with a "seeded" image:

<p align="center">
<img src=https://imgur.com/3JFRd9e.png/>
-->
<img src=https://i.imgur.com/WEzHzLh.gif/>
</p>
<p align = "center">5x5 fix (3, 3) with the door tile</p>

This door tile only appears once in the original image thus a large portion of the image space is constrained, however an enormous amount of variety is still observed in the outputs.

<p align="center">
<img src=https://imgur.com/Ow7uHy0.png/>
-->
<img src=https://imgur.com/vZ4Mdo9.gif/>
</p>
<p align = "center">5x5 fix several bike paths</p>

I was curious to see what would happen with the bike paths. In this example their generation is more constrained then I expected but this may not hold up to further testing.

<p align="center">
<img src=https://imgur.com/L7LUl8O.png/>
-->
<img src=https://imgur.com/oPeLdEJ.gif/>
</p>
<p align = "center">5x5 fix (3, 3) with a mud slide tile</p>

I wanted to see what kind of areas could be placed around the mud slide. I expected that the path in and out would be fairly constrained and the left and right allowed to vary wildly, it was in fact the opposite.

<p align="center">
<img src=https://imgur.com/hPRPo53.png/>
-->
<img src=https://imgur.com/6fZAtow.gif/>
</p>
<p align = "center">4x4 fix corner lake tiles</p>

I wanted to see what the algorithm was able to come up with given minimal input and I am quite pleased with the output.

<p align="center">
<img src=https://imgur.com/wImRKv5.png/>
-->
<img src=https://imgur.com/rvpEqSP.gif/>
</p>
<p align = "center">14x5 fix several corner roof tiles</p>

I wanted to test building a larger image leaning on the algorithm to fill in large areas.  Initially I believed that sucessively building an image and feeding larger and larger inputs would be the work flow, however this only increasese the search space over "every" (read many) variation which is theoritically comforting but practically useless. Edge exapnding and filling in small areas with fixed sections feels like the correct way to use this tool.

### [Fragment](https://github.com/akilmarshall/procedural-image-generation/wiki/Procedures#fragment)

For this incredibly minimal input image each algorithm produced only 10 outputs
each. Each algorithm was able to produce the original image, in fact each algorithm
produced the exact same output. This is not to be expected and is perhaps an
artifact of the simplicity of the input image, the exact reasons are currently unknown.

The images are in no particular order.

#### [CENTER](https://github.com/akilmarshall/procedural-image-generation/wiki/CENTER-algorithm)

<p align="center">
<img src=https://imgur.com/0fcqyXN.png/>
</p>
<p align = "center">CENTER algorithm output</p>

#### [CORNER](https://github.com/akilmarshall/procedural-image-generation/wiki/CORNER-algorithm)

<p align="center">
<img src=https://imgur.com/pXQtAjm.png>
</p>
<p align = "center">CORNER algorithm output</p>

#### [SIDE](https://github.com/akilmarshall/procedural-image-generation/wiki/SIDE-algorithm)

<p align="center">
<img src=https://imgur.com/dZEUcL5.png>
</p>
<p align = "center">SIDE algorithm output</p>

### [Minimum Conformity Improvement](https://github.com/akilmarshall/procedural-image-generation/wiki/Minimum-Conformity-Improvement)

1. Begin with an image
2. Select the tile with the least [conformity](https://github.com/akilmarshall/procedural-image-generation/wiki/Genetic-Algorithms#conformity-function) (halt if all conforming or [done](https://github.com/akilmarshall/procedural-image-generation/wiki/Minimum-Conformity-Improvement#termination))
3. change it's neighbors to tiles from it's neighbor sets (force conformity)
4. goto 2

Several runs of this naive algorithm produce the following select output

<p align="center">
<img src=https://imgur.com/MYrgU01.png>
</p>
<p align = "center">10x10 fitness score 50</p>

<p align="center">
<img src=https://imgur.com/5L3a8Ch.png>
</p>
<p align = "center">10x10 fitness score 220</p>

<p align="center">
<img src=https://imgur.com/3G4ylRZ.png>
</p>
<p align = "center">10x10 fitness score 130</p>

A **perfect** image would have a score of 400.
