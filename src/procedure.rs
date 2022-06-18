//! This module implements contrainted backracking search to generate a large number of images from
//! a seed image, empty or partially complete.

use crate::image::{IDMatrix, TID};
use crate::node::{Node, Tile};
use std::collections::VecDeque;

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
                            fork.collapse(x, y, t, &tis);
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
