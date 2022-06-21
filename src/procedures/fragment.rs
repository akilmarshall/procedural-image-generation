use crate::image::TIS;
use crate::structures::node::{Node, Tile};
use crate::util::mkdir;

pub fn core(t: usize, tis: TIS) {
    assert!(t < tis.data.n);
    let mut out = Vec::new();
    for a in tis.data.neighborhood(t, 0) {
        for b in tis.data.neighborhood(t, 1) {
            for c in tis.data.neighborhood(t, 2) {
                for d in tis.data.neighborhood(t, 3) {
                    let mut img = Node::new(3, 3);
                    img.set(1, 1, Tile::This(Some(t)));
                    img.set(2, 1, Tile::This(Some(a)));
                    img.set(1, 0, Tile::This(Some(b)));
                    img.set(0, 1, Tile::This(Some(c)));
                    img.set(1, 2, Tile::This(Some(d)));
                    out.push(img.to_idmatrix());
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
