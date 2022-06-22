use crate::image::TIS;
use crate::structures::node::{Node, Tile};
use crate::util::mkdir;

pub fn center(t: usize, tis: TIS) {
    assert!(t < tis.data.n);
    let mut out = Vec::new();
    let A = tis.data.neighborhood(t, 0);
    let B = tis.data.neighborhood(t, 1);
    let C = tis.data.neighborhood(t, 2);
    let D = tis.data.neighborhood(t, 3);
    for a in &A {
        for b in &B {
            for c in &C {
                for d in &D {
                    let Ea = tis.data.neighborhood(*a, 1);
                    let Eb = tis.data.neighborhood(*b, 0);
                    let Fa = tis.data.neighborhood(*b, 2);
                    let Fb = tis.data.neighborhood(*c, 1);
                    let Ga = tis.data.neighborhood(*c, 3);
                    let Gb = tis.data.neighborhood(*d, 2);
                    let Ha = tis.data.neighborhood(*d, 0);
                    let Hb = tis.data.neighborhood(*a, 3);
                    for e in Ea.intersection(&Eb) {
                        for f in Fa.intersection(&Fb) {
                            for g in Ga.intersection(&Gb) {
                                for h in Ha.intersection(&Hb) {
                                    let mut img = Node::new(3, 3);
                                    img.set(1, 1, Tile::This(Some(t)));
                                    img.set(2, 1, Tile::This(Some(*a)));
                                    img.set(1, 0, Tile::This(Some(*b)));
                                    img.set(0, 1, Tile::This(Some(*c)));
                                    img.set(1, 2, Tile::This(Some(*d)));
                                    img.set(2, 0, Tile::This(Some(*e)));
                                    img.set(0, 0, Tile::This(Some(*f)));
                                    img.set(0, 2, Tile::This(Some(*g)));
                                    img.set(2, 2, Tile::This(Some(*h)));
                                    out.push(img.to_idmatrix());
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    let path = format!("CENTER/{}", t);
    mkdir(&path);
    for (i, img) in out.into_iter().enumerate() {
        tis.decode(img).save(format!("{}/{}.png", path, i)).ok();
    }
}

pub fn side(t: usize, tis: TIS) {
    assert!(t < tis.data.n);
    let mut out = Vec::new();
    let A = tis.data.neighborhood(t, 0);
    let B = tis.data.neighborhood(t, 2);
    let C = tis.data.neighborhood(t, 3);
    for a in &A {
        for b in &B {
            for c in &C {
                let Da = tis.data.neighborhood(*b, 3);
                let Db = tis.data.neighborhood(*c, 2);
                let Ea = tis.data.neighborhood(*a, 3);
                let Eb = tis.data.neighborhood(*c, 0);
                for d in Da.intersection(&Db) {
                    for e in Ea.intersection(&Eb) {
                        for f in tis.data.neighborhood(*c, 3) {
                            let Ha = tis.data.neighborhood(*d, 3);
                            let Hb = tis.data.neighborhood(f, 2);
                            let Ga = tis.data.neighborhood(f, 0);
                            let Gb = tis.data.neighborhood(*e, 2);
                            for h in Ha.intersection(&Hb) {
                                for g in Ga.intersection(&Gb) {
                                    let mut img = Node::new(3, 3);
                                    img.set(1, 0, Tile::This(Some(t)));
                                    img.set(2, 0, Tile::This(Some(*a)));
                                    img.set(0, 0, Tile::This(Some(*b)));
                                    img.set(1, 1, Tile::This(Some(*c)));
                                    img.set(0, 1, Tile::This(Some(*d)));
                                    img.set(2, 1, Tile::This(Some(*e)));
                                    img.set(1, 2, Tile::This(Some(f)));
                                    img.set(2, 2, Tile::This(Some(*g)));
                                    img.set(0, 2, Tile::This(Some(*h)));
                                    out.push(img.to_idmatrix());
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    let path = format!("SIDE/{}", t);
    mkdir(&path);
    for (i, img) in out.into_iter().enumerate() {
        tis.decode(img).save(format!("{}/{}.png", path, i)).ok();
    }
}
pub fn corner(t: usize, tis: TIS) {
    assert!(t < tis.data.n);
    let mut out = Vec::new();
    let A = tis.data.neighborhood(t, 2);
    let B = tis.data.neighborhood(t, 1);
    for a in A {
        for b in &B {
            let Ca = tis.data.neighborhood(*b, 0);
            let Cb = tis.data.neighborhood(a, 3);
            for c in Ca.intersection(&Cb) {
                let D = tis.data.neighborhood(*c, 0);
                let E = tis.data.neighborhood(*c, 3);
                for d in D {
                    for e in &E {
                        let Fa = tis.data.neighborhood(a, 0);
                        let Fb = tis.data.neighborhood(d, 1);
                        let Ga = tis.data.neighborhood(d, 3);
                        let Gb = tis.data.neighborhood(*e, 0);
                        let Ha = tis.data.neighborhood(*b, 3);
                        let Hb = tis.data.neighborhood(*e, 2);
                        for f in Fa.intersection(&Fb) {
                            for g in Ga.intersection(&Gb) {
                                for h in Ha.intersection(&Hb) {
                                    let mut img = Node::new(3, 3);
                                    img.set(0, 0, Tile::This(Some(t)));
                                    img.set(1, 0, Tile::This(Some(a)));
                                    img.set(0, 1, Tile::This(Some(*b)));
                                    img.set(1, 1, Tile::This(Some(*c)));
                                    img.set(2, 1, Tile::This(Some(d)));
                                    img.set(1, 2, Tile::This(Some(*e)));
                                    img.set(2, 0, Tile::This(Some(*f)));
                                    img.set(2, 2, Tile::This(Some(*g)));
                                    img.set(0, 2, Tile::This(Some(*h)));
                                    out.push(img.to_idmatrix());
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    let path = format!("CORNER/{}", t);
    mkdir(&path);
    for (i, img) in out.into_iter().enumerate() {
        tis.decode(img).save(format!("{}/{}.png", path, i)).ok();
    }
}
