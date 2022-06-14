use serde::{Deserialize, Serialize};

/// Generic 2D  matrix
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct Matrix<T> {
    pub rows: usize,
    pub cols: usize,
    pub data: Vec<T>,
}

impl<T> Matrix<T> {
    pub fn new(rows: usize, cols: usize) -> Matrix<T>
    where
        T: Default,
    {
        Matrix {
            rows,
            cols,
            data: (0..rows * cols).map(|_| T::default()).collect(),
        }
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
    pub fn at(&self, row: usize, col: usize) -> &T {
        &self.data[col + row * self.cols]
    }
    pub fn set(&mut self, col: usize, row: usize, t: T) {
        assert!(row < self.rows && col < self.cols);
        self.data[col + row * self.cols] = t;
    }
}

/// Return a list of neighbors to (x, y)
pub trait Neighbors {
    fn rows(&self) -> usize;
    fn cols(&self) -> usize;
    fn neighbors(&self, x: usize, y: usize) -> Vec<(usize, usize, usize)> {
        let mut out = Vec::new();
        if x < (self.cols() - 1) {
            out.push((0, x + 1, y));
        }
        if y > 1 {
            out.push((1, x, y - 1));
        }
        if x > 1 {
            out.push((2, x - 1, y));
        }
        if y < (self.rows() - 1) {
            out.push((3, x, y + 1));
        }
        out
    }
}
