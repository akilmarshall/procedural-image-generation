//! This module implements strategies which use Tiled Image Data in an attempt to generate new
//! images

use crate::image::{IDMatrix, TID};
use priority_queue::PriorityQueue;
use std::collections::HashSet;

/// Potential ID Matrix
type PIDMatrix = Vec<Vec<HashSet<usize>>>;

/// A partially collapsed image. A graph with the nodes as "partially realized images" and edges
/// are "set" and "unset" operations on a tile in the image, i.e. nodes separated by one edge
/// differ at one tile.
struct Node {
    data: PIDMatrix,
}

impl Node {
    pub fn new(i: IDMatrix) -> Self {
        let mut pid = Vec::new();
        for row in i {
            let mut wor = Vec::new();
            for tile in row {
                match tile {
                    Some(tile) => {
                        let mut set = HashSet::new();
                        set.insert(tile);
                        wor.push(set);
                    }
                    None => wor.push(HashSet::new()),
                }
            }
            pid.push(wor);
        }
        Node { data: pid }
    }
    /// Query if the current object is a leaf (terminal).
    pub fn leaf(&self) -> bool {
        for row in &self.data {
            for item in row {
                if item.len() > 1 {
                    return false;
                }
            }
        }
        true
    }
    pub fn least_entropy(&self) -> Vec<(usize, usize)> {
        let mut pq = PriorityQueue::new();
        for i in 0..self.data.len() {
            for j in 0..self.data[0].len() {
                let len = self.data[i][j].len();
                // dont care about singleton sets
                if len > 1 {
                    pq.push((i, j), len);
                }
            }
        }
        pq.into_sorted_vec()
    }
    // pub fn collapse(&self) -> IDMatrix {
    pub fn collapse(&self) {
        for (x, y) in self.least_entropy() {}
    }
}

/// Natrual function to convert Option a -> HashSet a.\n
/// None -> {}, \n
/// Some(a) -> {a}
fn id_to_pid(id: Option<usize>) -> HashSet<usize> {
    let mut out = HashSet::new();
    if let Some(i) = id {
        out.insert(i);
    }
    out
}
