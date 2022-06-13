//! This module implements contrainted backracking search to generate a large number of images from
//! a seed image, empty or partially complete.

use crate::image::{direction, IDMatrix, Matrix, TID};
use priority_queue::PriorityQueue;
use std::collections::HashSet;

/// A partially collapsed image. A graph with the nodes as "partially realized images" and edges
/// are "set" and "unset" operations on a tile in the image, i.e. nodes separated by one edge
/// differ at one tile.
pub type Node = Matrix<HashSet<usize>>;

impl Node {
    pub fn from_IDMatrix(i: IDMatrix) -> Node {
        Node {
            rows: i.rows(),
            cols: i.cols(),
            data: i.data().iter().map(|d| id_to_pid(*d)).collect(),
        }
    }
    /// Construct an uncollapsed image with t options for every position
    pub fn empty(rows: usize, cols: usize, t: usize) -> Self {
        Node {
            rows,
            cols,
            data: (0..rows * cols).map(|_| (0..t).collect()).collect(),
        }
    }
    /// Return true if the node is fully collapsed, i.e. each set contains 1 or fewer members
    pub fn complete(&self) -> bool {
        for d in self.data() {
            if d.len() > 1 {
                return false;
            }
        }
        true
    }
    /// Return true if each member in self.data contains exactly 1 item
    pub fn good(&self) -> bool {
        for d in self.data() {
            if d.len() != 1 {
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
            match min {
                None => {
                    min = Some(d.len());
                    out = Some((x, y));
                }
                Some(m) => {
                    if d.len() < m {
                        min = Some(d.len());
                        out = Some((x, y));
                    }
                }
            }
        }
        out
    }
    pub fn neighbors(&self, x: usize, y: usize) -> Vec<(direction, usize, usize)> {
        let mut out = Vec::new();
        // if let N = self.at(x + 1, y) {}
        out
    }
}

/// Natural function to convert Option a -> HashSet a.\n
/// None -> {}, \n
/// Some(a) -> {a}
fn id_to_pid(id: Option<usize>) -> HashSet<usize> {
    let mut out = HashSet::new();
    if let Some(i) = id {
        out.insert(i);
    }
    out
}
