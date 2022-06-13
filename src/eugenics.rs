//! ~~eugenics~~ I mean Genetic Algorithms
/*
use crate::genetic::{cross, Individual};
use crate::image::{IDMatrix, TID};
use priority_queue::DoublePriorityQueue;

pub struct GA {
    pub population: Vec<Individual>,
    tid: TID,
    m: usize,
    n: usize,
}
impl GA {
    pub fn average_fitness(&self) -> f64 {
        (&self.population)
            .into_iter()
            .map(|a| a.fitness(&self.tid) as f64)
            .fold(0., |a, b| a + b)
            / self.population.len() as f64
    }
    pub fn new(p: usize, m: usize, n: usize, tid: &TID) -> Self {
        GA {
            population: (0..p).map(|_| Individual::new(m, n, tid)).collect(),
            tid: tid.clone(),
            m,
            n,
        }
    }
    pub fn id_matrices(&self) -> Vec<IDMatrix> {
        (&self.population)
            .into_iter()
            .map(|a| a.to_idmatrix())
            .collect()
    }
    pub fn by_fitness(&self) -> Vec<&Individual> {
        let mut pq = DoublePriorityQueue::new();
        for p in &self.population {
            pq.push(p, p.fitness(&self.tid));
        }
        pq.into_descending_sorted_vec()
    }
    fn select(&self) -> Vec<Individual> {
        let ordered: Vec<&Individual> = self.by_fitness();
        let n = ordered.len();
        ordered[n..].into_iter().map(|a| (**a).clone()).collect()
    }
    fn step(&self) -> Vec<Individual> {
        let mut next_gen = Vec::new();
        next_gen.extend(self.select());
        let parents = self.select();
        let (a, b) = parents.split_at(next_gen.len() / 2);
        for (l, r) in a.into_iter().zip(b) {
            //
            let (child_a, child_b) = cross(l, r);
            next_gen.push(child_a.mutate(self.tid.clone()));
            next_gen.push(child_b.mutate(self.tid.clone()));
        }
        /*
        let ordered: Vec<&Individual> = self.by_fitness();
        let n = ordered.len();
        let (upper, _lower) = ordered.split_at(n / 2);
        let (a, b) = upper.split_at(upper.len() / 2);
        let mut next_gen = Vec::new();
        for (l, r) in a.into_iter().zip(b) {
            let (a, b, c, d) = cross(l, r);
            next_gen.push(a);
            next_gen.push(b);
            next_gen.push(c.mutate(self.tid.clone()));
            next_gen.push(d.mutate(self.tid.clone()));
            // let (child_a, child_b) = cross(l.clone(), r.clone());
            // next_gen.push(Individual::from_idmatrix(l.to_idmatrix()));
            // next_gen.push(Individual::from_idmatrix(r.to_idmatrix()));
            // next_gen.push(child_a.mutate(self.tid.clone()));
            // next_gen.push(child_b.mutate(self.tid.clone()));
        }
        println!("{}", next_gen.len());
        */
        next_gen
    }
    pub fn evolve(&mut self, n: usize) {
        let s = self.average_fitness();
        for _ in 0..n {
            self.population = self.step();
            let f = self.average_fitness();
            println!(
                "initial {}\tcurrent {}\t pop {}",
                s,
                f,
                self.population.len()
            );
        }
    }
}
*/
