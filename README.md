# Procedural Image Generation

How can I turn a single image into more images that are somewhat like it?

## Todo

- Write unit and integration tests for the image module, tit panics when computing
  TIS for safari.png
- Prototype genetic algos in python:
    - write some words about why GA are suitable for image generation
      (how does this fit as an optimization problem?)
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
