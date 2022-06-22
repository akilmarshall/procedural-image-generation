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

![minimal input example](https://imgur.com/ZuOinkm.png).

Made up of the following tileset

![tileset](https://imgur.com/CfTFzSk.png)

It's neighbor functions are visualized below

![neighbor function visualization](https://imgur.com/GQAaMIr.png)

### Fragment

For this incredibly minimal input image each algorithm produced only 10 outputs
each. Each algorithm was able to produce the original image, in fact each algorithm
produced the exact same output. This is not to be expected and is perhaps an
artifact of the simplicity of the input image, the exact reasons are currently unknown.

The images are in no particular order.

#### CENTER

![CENTER algorithm output](https://imgur.com/0fcqyXN.png)

#### CORNER

![CORNER algorithm output](https://imgur.com/pXQtAjm.png)

#### SIDE

![SIDE algorithm output](https://imgur.com/dZEUcL5.png)
