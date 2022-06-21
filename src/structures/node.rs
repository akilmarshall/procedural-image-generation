//! A data structure for representing partially or completely defined images, each tile may be
//! undefined, defined, or a defined as several competing options.
use crate::image::{IDMatrix, TID};
use crate::structures::matrix::{Matrix, Neighbors};
use std::collections::HashSet;

#[derive(Debug, Clone, Eq, PartialEq)]
pub enum Tile {
    This(Option<usize>),
    These(Vec<usize>),
}

impl Default for Tile {
    fn default() -> Self {
        Tile::This(None)
    }
}

/// A partially collapsed image. A graph with the nodes as "partially realized images" and edges
/// are "set" and "unset" operations on a tile in the image, i.e. nodes separated by one edge
/// differ at one tile.
pub type Node = Matrix<Tile>;

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
    pub fn empty(cols: usize, rows: usize, t: usize) -> Self {
        Node {
            rows,
            cols,
            data: (0..cols * rows)
                .map(|_| Tile::These((0..t).collect()))
                .collect(),
        }
    }
    /// Return true if the node is fully collapsed, i.e. each position is Tile::This(None) or
    /// Tile::This(Some(_)).
    pub fn complete(&self) -> bool {
        for d in self.data() {
            if let Tile::These(_) = d {
                return false;
            }
        }
        true
    }
    /// Return true if the node is fully defined, i.e. each position is Tile::This(Some(_)).
    pub fn good(&self) -> bool {
        for d in self.data() {
            match d {
                Tile::This(None) => return false,
                Tile::These(_) => return false,
                _ => {}
            }
        }
        true
    }
    /// Returns the position with the fewest options to choose from, i.e. for each tile in
    /// self.data for each that is Tile::These(v), return the first position with the smallest
    /// v.len() otherwise None.
    pub fn min_choices(&self) -> Option<(usize, usize)> {
        let mut out: Option<(usize, usize)> = None;
        let mut min: Option<usize> = None;
        for (i, d) in self.data().iter().enumerate() {
            let x: usize = i % self.cols();
            let y: usize = i / self.cols();
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
    /// Set (x, y) to t and propogate the consequences according to the neighbor function.
    pub fn collapse(&mut self, x: usize, y: usize, t: usize, tid: &TID) {
        self.set(x, y, Tile::This(Some(t)));
        for (d, h, k) in self.neighbors(x, y) {
            if let Tile::These(neighbors) = self.at(h, k) {
                let ts = intersection(neighbors.to_vec(), tid.neighborhood(t, d));
                self.set(h, k, ts);
            }
        }
    }

    /// Compute an IDMatrix representation.
    pub fn to_idmatrix(&self) -> IDMatrix {
        let mut id_matrix = IDMatrix::new(self.cols, self.rows);
        id_matrix.data = self
            .data
            .iter()
            .map(|d| match d {
                Tile::This(Some(t)) => Some(t.clone()),
                Tile::This(None) | Tile::These(_) => None,
            })
            .collect();
        id_matrix
    }
}

/// Specialized function to compute the result of the intersection of a Vec<Tile> and
/// HashSet<Tile> as a Tile enum.
fn intersection(as_: Vec<usize>, bs: HashSet<usize>) -> Tile {
    let mut ts = Vec::new();
    for a in as_ {
        if bs.contains(&a) {
            ts.push(a);
        }
    }
    match ts.len() {
        0 => return Tile::This(None),
        1 => return Tile::This(ts.pop()),
        _ => return Tile::These(ts),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::image::Neighborhood;
    #[test]
    fn neighborhood() {
        let a = Node::new(1, 2);
        assert_eq!(a.neighbors(0, 0).len(), 1);
        assert_eq!(a.neighbors(0, 1).len(), 1);
        let b = Node::new(1, 3);
        assert_eq!(b.neighbors(0, 1).len(), 2);
        let c = Node::new(3, 3);
        assert_eq!(c.neighbors(0, 0).len(), 2);
        assert_eq!(c.neighbors(0, 1).len(), 3);
        assert_eq!(c.neighbors(1, 1).len(), 4);
    }
    #[test]
    fn node_empty() {
        let n = 5;
        let a = Node::empty(1, 1, n);
        let b = Node::empty(1, 2, n);
        let c = Node::empty(2, 1, n);
        let d = Node::empty(1, 3, n);
        let e = Node::empty(3, 1, n);
        let f = Node::empty(2, 2, n);
        let x = Tile::These((0..n).collect());
        assert_eq!(a.data, vec![x.clone()]);
        assert_eq!(b.data, vec![x.clone(), x.clone()]);
        assert_eq!(c.data, vec![x.clone(), x.clone()]);
        assert_eq!(d.data, vec![x.clone(), x.clone(), x.clone()]);
        assert_eq!(e.data, vec![x.clone(), x.clone(), x.clone()]);
        assert_eq!(f.data, vec![x.clone(), x.clone(), x.clone(), x.clone()]);
    }
    #[test]
    fn complete() {
        let mut a = Node::new(1, 1);
        assert_eq!(a.complete(), true);
        a.set(0, 0, Tile::These(vec![0]));
        assert_eq!(a.complete(), false);
        a.set(0, 0, Tile::This(Some(2)));
        assert_eq!(a.complete(), true);
    }
    #[test]
    fn good() {
        let mut a = Node::new(1, 1);
        let b = Node::empty(1, 1, 1);
        assert_eq!(a.good(), false);
        assert_eq!(b.good(), false);

        a.set(0, 0, Tile::This(Some(0)));
        assert_eq!(a.good(), true);
        a.set(0, 0, Tile::This(None));
        assert_eq!(a.good(), false);
    }
    #[test]
    fn min_choices() {
        let mut a = Node::empty(1, 2, 1);
        assert_eq!(a.min_choices(), Some((0, 0)));
        a.set(0, 0, Tile::This(Some(0)));
        assert_eq!(a.min_choices(), Some((0, 1)));
        let mut b = Node::new(2, 2);
        assert_eq!(b.min_choices(), None);
        b.set(1, 1, Tile::These(vec![]));
        assert_eq!(b.min_choices(), Some((1, 1)));
    }
    /// Crude test, requires futhre research into minimal neighborhood rule sets before it will
    /// be clear what is necessary and crucial to test.
    #[test]
    fn collapse() {
        let mut n = Neighborhood::new();
        n.insert(0, 0);
        n.insert(0, 1);
        n.insert(0, 2);
        n.insert(0, 3);
        let mut tid = TID::new();
        tid.mapping(vec![n]);
        let mut a = Node::empty(1, 2, 1);
        assert_eq!(a.data, vec![Tile::These(vec![0]), Tile::These(vec![0])]);
        a.collapse(0, 0, 0, &tid);
        assert_eq!(a.data, vec![Tile::This(Some(0)), Tile::This(Some(0))]);
    }
    #[test]
    fn to_idmatrix() {
        let mut a = Node::new(1, 1);
        assert_eq!(a.to_idmatrix().data, vec![None]);
        a.set(0, 0, Tile::This(Some(0)));
        assert_eq!(a.to_idmatrix().data, vec![Some(0)]);

        let mut b = Node::new(1, 2);
        b.set(0, 1, Tile::This(Some(0)));
        assert_eq!(b.to_idmatrix().data, vec![None, Some(0)]);

        let mut c = Node::new(3, 1);
        c.set(1, 0, Tile::This(Some(0)));
        c.set(2, 0, Tile::This(Some(1)));
        assert_eq!(c.to_idmatrix().data, vec![None, Some(0), Some(1)]);

        let mut d = Node::new(3, 3);
        d.set(0, 0, Tile::This(Some(0)));
        d.set(1, 1, Tile::This(Some(1)));
        d.set(2, 2, Tile::This(Some(2)));
        d.set(2, 0, Tile::This(Some(3)));
        d.set(0, 2, Tile::This(Some(4)));
        d.set(1, 0, Tile::This(Some(5)));
        d.set(2, 1, Tile::This(Some(6)));
        d.set(1, 2, Tile::This(Some(7)));
        d.set(0, 1, Tile::This(Some(8)));
        assert_eq!(
            d.to_idmatrix().data,
            vec![
                Some(0),
                Some(5),
                Some(3),
                Some(8),
                Some(1),
                Some(6),
                Some(4),
                Some(7),
                Some(2)
            ]
        );
    }
}
