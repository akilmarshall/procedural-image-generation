mod eugenics;
mod genetic;
mod image;
mod matrix;
mod node;
mod procedure;

use crate::image::{load_tis, Image, TID, TIS};
use crate::node::Node;
use crate::procedure::backtrack_search;
use clap::{arg, Command};

fn cli() -> Command<'static> {
    Command::new("tit")
        .about("the Tiled Image Tool.")
        .subcommand_required(true)
        .arg_required_else_help(true)
        .subcommand(
            Command::new("compute")
                .about("Compute Tiled Image Statistics (TIS).")
                .args(&[
                    arg!(<WIDTH> "width of the tiles"),
                    arg!(<HEIGHT> "height of the tiles"),
                    arg!(<PATH> "path of the image"),
                    arg!([OUT] "option name of the directory to place TIS in")
                        .long("out")
                        .short('o'),
                ])
                .arg_required_else_help(true),
        )
        .subcommand(
            Command::new("inference")
                .about("Use Tiled Image Statistics to generate new images.")
                .args(&[arg!(<TIS> "TIS"), arg!(<COL> "columns"), arg!(<ROW> "rows")])
                .arg_required_else_help(true),
        )
}

fn main() {
    let matches = cli().get_matches();
    match matches.subcommand() {
        Some(("compute", args)) => {
            let path = args.value_of("PATH").unwrap().to_string();
            let img = Image::new(
                args.value_of("WIDTH").unwrap().parse::<u32>().unwrap(),
                args.value_of("HEIGHT").unwrap().parse::<u32>().unwrap(),
                String::from(&path),
            );
            let mut tid = TID::new();
            tid.mapping(img.compute_neighborhoods())
                .n(img.tiles().len())
                .width(img.tile_width)
                .height(img.tile_height);
            let tis = TIS::new(tid, img.tiles().to_vec());
            let dir = args.value_of("OUT").unwrap_or("TIS");
            tis.save_all(dir.to_string());
        }
        Some(("inference", args)) => {
            let path = args.value_of("TIS").unwrap();
            let rows = args.value_of("ROW").unwrap().parse::<usize>().unwrap();
            let cols = args.value_of("COL").unwrap().parse::<usize>().unwrap();
            match load_tis(path.to_string()) {
                Some(tis) => {
                    // do some inference with tis
                    let seed = Node::empty(cols, rows, tis.data.n);
                    // seed.set(0, 0, Tile::This(Some(1)));
                    // tis.decode(seed.to_idmatrix()).save("blank.png").ok();
                    for (i, gimg) in backtrack_search(seed, tis.data.clone())
                        .into_iter()
                        .enumerate()
                    {
                        tis.decode(gimg).save(format!("out/{}.png", i)).ok();
                    }
                }
                None => {}
            }
        }
        Some(("tiles", _args)) => {}
        _ => { /* catch all do nothing */ }
    }
}
// impl Neighbors for Matrix<usize> {
//     fn rows(&self) -> usize {
//         self.rows()
//     }
//     fn cols(&self) -> usize {
//         self.cols()
//     }
// }
// fn main() {
//     let mut m = Matrix::<usize>::new(3, 1);
//     println!("{:?}", m.data);
//     println!("{:?}", m.neighbors(1, 0));
// }
