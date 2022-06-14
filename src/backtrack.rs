//! This module implements contrainted backracking search to generate a large number of images from
//! a seed image, empty or partially complete.

use crate::image::{Direction, IDMatrix, TID};
use crate::matrix::{Matrix, Neighbors};
use priority_queue::PriorityQueue;
use std::collections::{HashSet, VecDeque};

#[derive(Clone)]
pub enum Tile {
    This(Option<usize>),
    These(Vec<usize>),
}

/// A partially collapsed image. A graph with the nodes as "partially realized images" and edges
/// are "set" and "unset" operations on a tile in the image, i.e. nodes separated by one edge
/// differ at one tile.
pub type Node = Matrix<Tile>;

impl Neighbors for Node {
    fn rows(&self) -> usize {
        self.rows()
    }
    fn cols(&self) -> usize {
        self.cols()
    }
}

impl Node {
    // pub fn from_idmatrix(i: IDMatrix) -> Node {
    // when importing from idmatrix if only some positions are defined their undefined
    // neighbors must have Tile.These(...) defined WRT TIS
    // Node {
    //     rows: i.rows(),
    //     cols: i.cols(),
    //     data: i.data().iter().map(|d| {}).collect(),
    // }
    // }
    /// Construct an uncollapsed image with t options for every position
    pub fn empty(rows: usize, cols: usize, t: usize) -> Self {
        Node {
            rows,
            cols,
            data: (0..rows * cols)
                .map(|_| Tile::These((0..t).collect()))
                .collect(),
        }
    }
    /// Return true if the node is fully collapsed, i.e. each set contains 1 or fewer members
    pub fn complete(&self) -> bool {
        for d in self.data() {
            if let Tile::These(_) = d {
                return false;
            }
        }
        true
    }
    /// Return true if each member in self.data contains exactly 1 item
    pub fn good(&self) -> bool {
        for d in self.data() {
            if let Tile::These(_) = d {
                return false;
            }
        }
        true
    }
    pub fn min_choices(&self) -> Option<(usize, usize)> {
        let mut out: Option<(usize, usize)> = None;
        let mut min: Option<usize> = None;
        for (i, d) in self.data().iter().enumerate() {
            let x: usize = i / self.cols();
            let y: usize = i % self.cols();
            if let Tile::These(neighbors) = d {
                match min {
                    None => {
                        min = Some(neighbors.len());
                        out = Some((x, y));
                    }
                    Some(m) => {
                        if neighbors.len() < m {
                            min = Some(neighbors.len());
                            out = Some((x, y));
                        }
                    }
                }
            }
        }
        out
    }
    pub fn collapse(&mut self, x: usize, y: usize, t: usize, tid: &TID) {
        self.set(x, y, Tile::This(Some(t)));
        for (d, h, k) in self.neighbors(x, y) {
            if let Tile::These(neighbors) = self.at(h, k) {
                let mut T: Vec<usize> = intersection(neighbors.to_vec(), tid.N(t, d));
                match T.len() {
                    0 => self.set(h, k, Tile::This(None)),
                    1 => self.set(h, k, Tile::This(T.pop())),
                    _ => self.set(h, k, Tile::These(T)),
                }
            }
        }
    }

    pub fn to_idmatrix(&self) -> IDMatrix {
        let mut id_matrix = IDMatrix::new(self.rows, self.cols);
        for i in 0..self.rows {
            for j in 0..self.cols {
                match self.at(i, j) {
                    Tile::This(Some(t)) => {
                        id_matrix.set(i, j, Some(*t));
                    }
                    Tile::This(None) | Tile::These(_) => {
                        id_matrix.set(i, j, None);
                    }
                }
            }
        }
        id_matrix
    }
}

fn intersection(A: Vec<usize>, B: HashSet<usize>) -> Vec<usize> {
    let mut out = Vec::new();
    for a in A {
        if B.contains(&a) {
            out.push(a);
        }
    }
    out
}

pub fn backtrack_search(seed: Node, tis: TID) -> Vec<IDMatrix> {
    let mut out: Vec<IDMatrix> = Vec::new();
    let mut active = VecDeque::from([seed]);
    while !active.is_empty() {
        if let Some(img) = active.pop_front() {
            if let Some((x, y)) = img.min_choices() {
                match img.at(x, y) {
                    Tile::This(Some(id)) => {}
                    Tile::This(None) => {}
                    Tile::These(tiles) => {
                        for t in tiles {
                            let mut fork = img.clone();
                            fork.collapse(x, y, *t, &tis);
                            if fork.complete() {
                                out.push(fork.to_idmatrix())
                            } else {
                                active.push_front(fork);
                            }
                        }
                    }
                }
            }
        }
    }
    out
}
