# Procedural Image Generation

How can I turn a single image into more images that are somewhat like it?


(you need [xhub](https://github.com/nschloe/xhub)
extension to view the math, maybe it won't be a pain in the ass to write it
natively in the README one day...)

## Todo

- Write unit and integration tests for the image module, tit panics when computing
  TIS for safari.png
- Prototype genetic algos in python:
    - write some words about why GA are suitable for image generation
      (how does this fit as an optimization problem?)

## Theory

`$\mathbb{I}$` denotes a tiled image, that is an image composed of a **tile sheet**
also known as a **tile set**.

![A tile sheet generates an image](https://imgur.com/suCdR2N.png)

`$\mathbb{T}$` denotes the tile sheet of `$\mathbb{I}$`,

```math
\mathbb{T} = \{t_1, t_2, \cdots{}, t_n\}
```
each tile set `$\mathbb{T}$` contains `$n$` items each denoted `$t_i$` where
`$1\leq i \leq n$`.


Each image `$\mathbb{I}$` also has an associated **neighbor** function,

```math
    \mathcal{N}_{\mathbb{I}}::t\to d\to \left[t\right],
```

![Example of the neighbor function](https://imgur.com/8reI0hs.png)

that takes a tile and a direction and returns a list of the tiles seen adjacent
in the specified direction `$\{0, 1, 2, 3\}$`.

![Neighbor directions](https://imgur.com/9MSJKR7.png)

Together `$(\mathbb{I}, \mathbb{T}, \mathcal{N})$` can be called
**tiled image statistics** (TIS).

## Procedures

Here I describe a variety of data structures and algorithms for procedural image
generation using TIS.

### Fragment

A set of `$3\times 3$` tiled images generated by a single tile and a specific
expansion algorithm.

```math
   \mathcal{F}=
   \begin{bmatrix}
    t & t & t \\
    t & t & t \\
    t & t & t
   \end{bmatrix}
```

#### CENTER

Fix `$\left(1, 1\right)$` in `$\mathcal{F}$` with `$t_i$`

```math
    \mathcal{F}_{(1, 1, t_i)}=
    \begin{bmatrix}
    & & \\
    & t_i & \\
    & &
    \end{bmatrix}
```

The `$CENTER$` algorithm expands a fragment of the form `$\mathcal{F}_{(1, 1, t)}$`

```math
    CENTER\langle\mathcal{F}_{(1, 1, t)}\rangle=
    \begin{bmatrix}
    G=\mathcal{N}(c, 1)\cap \mathcal{N}(b, 2)  & B=\mathcal{N}(t,1) & F=\mathcal{N}(b, 0)\cap \mathcal{N}(a, 1) \\
    C=\mathcal{N}(t,2) & t & A=\mathcal{N}(t,0) \\
    H=\mathcal{N}(c, 3)\cap \mathcal{N}(d, 2) & D=\mathcal{N}(t,3) & E=\mathcal{N}(d, 0)\cap \mathcal{N}(a, 3)
    \end{bmatrix}
```

The `$CENTER$` algorithm takes two steps:

1. Compute `$\{A, B, C, D\}$` from `$t_i$` directly
    1. select `$\{a, b, c, d\}$` from `$\{A, B, C, D\}$` respectively.
2. Compute `$\{E, F, G, H\}$` from `$\mathcal{N}(d, 0)\cap\mathcal{N}(a, 3)$`,
   `$\mathcal{N}(b, 0)\cap\mathcal{N}(a, 1)$`,
   `$\mathcal{N}(c, 1)\cap\mathcal{N}(b, 2)$` and,
   `$\mathcal{N}(c, 3)\cap\mathcal{N}(d, 2)$` respectively
    1. select `$\{e, f, g, h\}$` from `$\{E, F, G, H\}$` respectively.

![Expanded description of the CENTER algorithm](https://imgur.com/3a8AQ2M.png)

#### SIDE

Fix `$(1, 0)$` in `$\mathcal{F}$` with `$t_i$`

```math
\mathcal{F}_{(1, 0, t_i)}=
\begin{bmatrix}
& t_i  &   \\  &  &   \\   &   &  
\end{bmatrix}
```


The `$SIDE$` algorithm expands a fragment of the form `$\mathcal{F}_{(1, 0, t)}$`
(or any of its symmetries, `$(0, 1), (2, 1), (1, 2)$`).

```math
    SIDE\langle\mathcal{F}_{(1, 1, t)}\rangle=
    \begin{bmatrix}
    B=\mathcal{N}(t, 2) & t & A=\mathcal{N}(t, 0) \\
    D=\mathcal{N}(b, 3)\cap\mathcal{N}(c, 2) & C=\mathcal{N}(t, 3) & E=\mathcal{N}(a, 3)\cap\mathcal{N}(c, 0) \\
    H=\mathcal{N}(d, 3)\cap\mathcal{N}(f, 2) & F=\mathcal{N}(c, 3) & G=\mathcal{N}(f, 0)\cap\mathcal{N}(e, 2)
    \end{bmatrix}
```

The `$SIDE$` algorithm takes three steps:

1. Compute `$\{A, B, C\}$` directly from `$t_i$`,
    1. select `$\{a, b, c\}$` from `$\{A, B, C\}$` respectively.
2. Compute `$\{D, E\}$` from `$\mathcal{N}(d, 3)\cap\mathcal{N}(f, 2)$` and
   `$\mathcal{N}(f, 0)\cap\mathcal{N}(e, 2)$` respectively, compute `$F$` directly
   from `$c$`
    1. select `$\{d, e, f\}$` from `$\{E, D, F\}$` respectively.
3. Compute `$\{H, G\}$` from `$\mathcal{N}(d, 3)\cap\mathcal{N}(f, 2)$` and
   `$\mathcal{N}(f, 0)\cap\mathcal{N}(e, 2)$` respectively
    1. select `$\{h, g\}$` from `$\{H, G\}$` respectively.

![Expanded description of the SIDE algorithm](https://imgur.com/9pCNOWH.png)

#### CORNER

Fix `$(0, 0)$` in `$\mathcal{F}$` with `$t_i$`

```math
\mathcal{F}_{(0, 0, t_i)}=
\begin{bmatrix}
t_i  &   &  \\  &  &  \\  &  &
\end{bmatrix}
```

The `$CORNER$` algorithm expands a fragment of the form `$\mathcal{F}_{(0, 0, t)}$`
(or any of its symmetries, `$(2, 0), (0, 2), (2, 2)$`).

```math
    CORNER\langle\mathcal{F}_{(1, 1, t)}\rangle=
\begin{bmatrix}
    t & A=\mathcal{N}(t,2) & F=\mathcal{N}(b, 0)\cap \mathcal{N}(a, 1) \\
    B=\mathcal{N}(t,1) & C = \mathcal{N}(b, 0)\cap \mathcal{N}(a, 3) & D=\mathcal{N}(c,0) \\
    H=\mathcal{N}(b, 3)\cap \mathcal{N}(e, 2) & E=\mathcal{N}(c,3) & G=\mathcal{N}(e, 0)\cap \mathcal{N}(d, 3)
\end{bmatrix}
```

The `$CORNER$` algorithm takes 4 steps:

1. Compute `$\{A, B\}$` directly from `$t$`
    1. select `$\{a, b\}$` from `$\{A, B\}$` respectively.
2. Compute `$C$` from `$\mathcal{N}(b,0)\cap\mathcal{N}(a, 3)$`
    1. select `$c$` from `$C$`.
3. Compute `$\{D, E\}$` from `$c$` directly
    1. select `$\{d, e\}$` from `$\{D, E\}$` respectively.
4. Compute `$\{F, G, H\}$` from `$\mathcal{N}(b, 0)\cap\mathcal{N}(a, 1)$`, `$\mathcal{N}(e, 0)\cap\mathcal{N}(d, 3)$` and
   `$\mathcal{N}(b, 3)\cap\mathcal{N}(e, 2)$` respectively
    1. select `$\{f, g, h\}$` from `$\{F, G, H\}$` respectively.

![Expanded description of the CORNER algorithm](https://imgur.com/IRQ4Ppm.png)

### Edge Expansion

Considering a fragment member how can it's edge's be expanded?

```math
   \mathcal{F}=
   \begin{bmatrix}
   & & & &\\ & a & b & c & \\ & d & e & f & \\ & h & i & j & \\ & & & &
   \end{bmatrix}
```

Considering a fragment member is `$D_4$` (symmetry group of the square) any
algorithm written to expand a specific edge can be transformed into an
equivalent algorithm for another edge. There for all expansion algorithms
described will be described for a single edge only.


I propose 3 algorithms, 2 of which are mirrored for computing the edge expansion
of

```math
\begin{bmatrix}
t_0 \\ t_1 \\ t_2
\end{bmatrix}

```

`$CENTERX$` and `$CORNERX$` (and it's mirror).

#### CENTERX

```math
CENTERX
\langle
\begin{bmatrix}
    t_0 \\ t_1 \\ t_2
\end{bmatrix}
\rangle=
\begin{bmatrix}
    B=\mathcal{N}(t_0, 0)\cap\mathcal{N}(a, 1)\\
    A=\mathcal{N}(t_1, 0) \\ 
    C=\mathcal{N}(t_2, 0)\cap\mathcal{N}(a, 3)
\end{bmatrix}
```

#### CORNERX

```math
CORNERX
\langle
\begin{bmatrix}
    t_0 \\ t_1 \\ t_2
\end{bmatrix}
\rangle
=
\begin{bmatrix}
    A=\mathcal{N}(t_0, 0) \\
    B=\mathcal{N}(t_1, 0)\cap\mathcal{N}(a, 3) \\
    C=\mathcal{N}(t_2, 0)\cap\mathcal{N}(b, 3)
\end{bmatrix}
```

```math
\overline{CORNERX}
\langle
\begin{bmatrix}
    t_0 \\ t_1 \\ t_2
\end{bmatrix}
\rangle
=
\begin{bmatrix}
C=\mathcal{N}(t_0, 0)\cap\mathcal{N}(b, 1) \\
B=\mathcal{N}(t_1, 0)\cap\mathcal{N}(a, 1) \\
A=\mathcal{N}(t_2, 0)
\end{bmatrix}
```

## tiled-image-tool

A command line tool written in rust for computing statistics from tiled images
and procedurally generating new images.
