# Procedural Image Generation

How can I turn a single image into more images that are somewhat like it?

## Todo

- implement tile sheet dump [rust]
- implement neighbor function visual dump [rust]

## Examples

Using the following image as input 

<p align="center">
<img src=https://imgur.com/ZuOinkm.png/>
</p>
<p align = "center">minimal input example</p>

Made up of the following tileset

<p align="center">
<img src=https://imgur.com/CfTFzSk.png/>
</p>

It's neighbor functions are visualized below

<p align="center">
<img src=https://imgur.com/GQAaMIr.png/>
</p>

### Fragment

For this incredibly minimal input image each algorithm produced only 10 outputs
each. Each algorithm was able to produce the original image, in fact each algorithm
produced the exact same output. This is not to be expected and is perhaps an
artifact of the simplicity of the input image, the exact reasons are currently unknown.

The images are in no particular order.

#### CENTER

<p align="center">
<img src=https://imgur.com/0fcqyXN.png/>
</p>
<p align = "center">CENTER algorithm output</p>

#### CORNER

<p align="center">
<img src=https://imgur.com/pXQtAjm.png>
</p>
<p align = "center">CORNER algorithm output</p>

#### SIDE

<p align="center">
<img src=https://imgur.com/dZEUcL5.png>
</p>
<p align = "center">SIDE algorithm output</p>

### Minimum Conformity Improvement

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
