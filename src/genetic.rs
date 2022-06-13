//! API for ~~eugenics~~ I mean Genetic Algorithms
/*
use crate::image::{IDMatrix, TID};
use rand::Rng;

/// An Individual for genetic algorithm for some mxn (row major) image.
/// dna represents the tile in a "flat" format
#[derive(Hash, Eq, PartialEq, Clone)]
pub struct Individual {
    m: usize,
    n: usize,
    dna: Vec<usize>,
}

impl Individual {
    /// Create a new random Individual.
    pub fn new(m: usize, n: usize, tid: &TID) -> Self {
        let mut rng = rand::thread_rng();
        Individual {
            m,
            n,
            dna: (0..m * n).map(|_| rng.gen_range(0..=tid.n - 1)).collect(),
        }
    }
    pub fn mutate(&self, tid: TID) -> Self {
        let mut rng = rand::thread_rng();
        let x = rng.gen_range(0..=self.dna.len() - 1);
        let d = rng.gen_range(0..=tid.n - 1);
        let mut dna: Vec<usize> = Vec::new();
        for (i, a) in self.dna.iter().enumerate() {
            if i == x {
                dna.push(d);
            } else {
                dna.push(*a);
            }
        }
        Individual {
            m: self.m,
            n: self.n,
            dna,
        }
    }
    /// Convert IDMatrix to Individual
    pub fn from_idmatrix(i: IDMatrix) -> Self {
        Individual {
            m: i.len(),
            n: i[0].len(),
            dna: idmatrix_to_dna(i),
        }
    }
    /// Convert this instance to IDMatrix
    pub fn to_idmatrix(&self) -> IDMatrix {
        self.dna
            .chunks_exact(self.n)
            .into_iter()
            .map(|row| row.into_iter().map(|a| Some(a.clone())).collect())
            .collect()
    }
    /// Compute the fitness of this Individual with respect to TID.
    pub fn fitness(&self, tid: &TID) -> usize {
        fitness(self.to_idmatrix(), tid)
    }
}

/// Generic fitness measure for IDMatrix and TID.
/// (it is easier to implement on IDMatrix than it's flat representation with repsect to TID)
pub fn fitness(i: IDMatrix, tid: &TID) -> usize {
    let neighbors = |h: usize, k: usize| -> Vec<(usize, usize, usize)> {
        let mut out = Vec::new();
        if h < i.len() - 1 {
            out.push((0, h + 1, k));
        }
        if k < i[0].len() - 1 {
            out.push((1, h, k + 1));
        }
        if k > 0 {
            out.push((2, h, k - 1));
        }
        if h > 0 {
            out.push((3, h - 1, k));
        }
        out
    };
    let mut score: usize = 0;
    for x in 0..i.len() {
        for y in 0..i[0].len() {
            if let Some(t) = i[x][y] {
                for (nid, h, k) in neighbors(x, y) {
                    if let Some(n) = i[h][k] {
                        if let Some(pop) = tid.mapping[t][nid].raw_query(n) {
                            if pop > 0 {
                                score += 1;
                            }
                        }
                    }
                }
            }
        }
    }
    score
}
/// Mutation Operator.
/// Given an IDMatrix, mutate it at single position.
fn mutate(mut i: IDMatrix, tid: TID) -> IDMatrix {
    let mut rng = rand::thread_rng();
    let x = rng.gen_range(0..=i.len() - 1);
    let y = rng.gen_range(0..=i[0].len() - 1);
    let d = rng.gen_range(0..=tid.n - 1);
    i[x][y] = Some(d);
    i
}

/// Cross over two individuals and return a pair of mixed childern.
// pub fn cross(a: &Individual, b: &Individual) -> (Individual, Individual, Individual, Individual) {
pub fn cross(a: &Individual, b: &Individual) -> (Individual, Individual) {
    let split = a.m / 2;
    let (a_head, a_tail) = a.dna.split_at(split);
    let (b_head, b_tail) = b.dna.split_at(split);
    let mut stub_dna_a: Vec<usize> = a_head.to_vec();
    let mut stub_dna_b: Vec<usize> = b_head.to_vec();
    stub_dna_a.extend(b_tail);
    stub_dna_b.extend(a_tail);
    (
        // Individual {
        //     m: a.m,
        //     n: a.n,
        //     dna: a.dna.clone(),
        // },
        // Individual {
        //     m: b.m,
        //     n: b.n,
        //     dna: b.dna.clone(),
        // },
        Individual {
            m: a.m,
            n: a.n,
            dna: stub_dna_a,
        },
        Individual {
            m: a.m,
            n: a.n,
            dna: stub_dna_b,
        },
    )
}
fn idmatrix_to_dna(i: IDMatrix) -> Vec<usize> {
    i.concat()
        .into_iter()
        .map(|a| {
            if let Some(data) = a {
                return data;
            }
            usize::MAX
        })
        .collect()
}
*/
