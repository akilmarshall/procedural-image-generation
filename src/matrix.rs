use serde::{Deserialize, Serialize};

/// Generic 2D  matrix
#[derive(Serialize, Deserialize, Debug, Clone, Eq, PartialEq)]
pub struct Matrix<T> {
    pub rows: usize,
    pub cols: usize,
    pub data: Vec<T>,
}

impl<T> Matrix<T> {
    pub fn new(cols: usize, rows: usize) -> Matrix<T>
    where
        T: Default,
    {
        Matrix {
            rows,
            cols,
            data: (0..rows * cols).map(|_| T::default()).collect(),
        }
    }
    fn index(&self, col: usize, row: usize) -> usize {
        // assert!(row < self.rows());
        // assert!(col < self.cols());
        col + row * self.cols()
    }
    pub fn rows(&self) -> usize {
        self.rows
    }
    pub fn cols(&self) -> usize {
        self.cols
    }
    pub fn data(&self) -> &Vec<T> {
        &self.data
    }
    pub fn at(&self, col: usize, row: usize) -> T
    where
        T: Clone,
    {
        let i = self.index(col, row);
        self.data[i].clone()
    }
    pub fn set(&mut self, col: usize, row: usize, t: T) {
        let i = self.index(col, row);
        self.data[i] = t;
    }
}

/// Return a list of neighbors to (x, y)
pub trait Neighbors {
    fn rows(&self) -> usize;
    fn cols(&self) -> usize;
    fn neighbors(&self, x: usize, y: usize) -> Vec<(usize, usize, usize)> {
        let mut out = Vec::new();
        if x < self.cols() - 1 {
            out.push((0, x + 1, y));
        }
        if y > 0 {
            out.push((1, x, y - 1));
        }
        if x > 0 {
            out.push((2, x - 1, y));
        }
        if y < self.rows() - 1 {
            out.push((3, x, y + 1));
        }
        out
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    type UMatrix = Matrix<usize>;

    #[test]
    fn construction() {
        let a = UMatrix::new(1, 1);
        let b = UMatrix::new(1, 2);
        let c = UMatrix::new(2, 2);
        assert_eq!(a.data().len(), 1);
        assert_eq!(b.data().len(), 2);
        assert_eq!(c.data().len(), 4);
    }
    #[test]
    fn col_api() {
        let a = UMatrix::new(1, 2);
        let b = UMatrix::new(2, 1);
        assert_eq!(a.cols(), 1);
        assert_eq!(b.cols(), 2);
    }
    #[test]
    fn row_api() {
        let a = UMatrix::new(1, 2);
        let b = UMatrix::new(2, 1);
        assert_eq!(a.rows(), 2);
        assert_eq!(b.rows(), 1);
    }
    #[test]
    fn read_write() {
        let mut a = UMatrix::new(1, 2);
        let mut b = UMatrix::new(2, 2);
        let mut c = UMatrix::new(3, 1);

        assert_eq!(a.at(0, 0), 0);
        assert_eq!(a.at(0, 1), 0);
        assert_eq!(b.at(1, 1), 0);
        assert_eq!(b.at(1, 0), 0);

        a.set(0, 0, 0);
        a.set(0, 1, 1);

        b.set(1, 1, 3);
        b.set(1, 0, 1);
        b.set(0, 1, 2);

        c.set(0, 0, 0);
        c.set(1, 0, 1);
        c.set(2, 0, 2);

        assert_eq!(a.data, vec![0, 1]);
        assert_eq!(b.data, vec![0, 1, 2, 3]);
    }
}
