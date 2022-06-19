mod image;
mod procedures;
mod structures;
mod util;

use crate::image::{load_tis, Image, TID, TIS};
use crate::procedures::backtrack::search;
use crate::structures::node::Node;
use crate::util::mkdir;
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
            Command::new("all")
                .about("Use Tiled Image Statistics to generate a large amount of new images of specific dimension.")
                .args(&[arg!(<TIS> "TIS"), arg!(<COL> "columns"), arg!(<ROW> "rows")])
                .arg_required_else_help(true),
        )
        .subcommand(
            Command::new("fragment")
                .about("Generate Fragments (3x3 tiled images) using a specific algorithm")
                .arg_required_else_help(true)
                .args(&[arg!(<TIS> "TIS")])
                .subcommand(
                    Command::new("center")
                        .about("The CENTER algorithm for Fragment computation, seeded with tile-id")
                        .args(&[arg!(<TILE> "tile-id")])
                        .arg_required_else_help(true)
                )
                .subcommand(
                    Command::new("side")
                        .about("The SIDE algorithm for Fragment computation, seeded with tile-id")
                        .args(&[arg!(<TILE> "tile-id")])
                        .arg_required_else_help(true)
                )
                .subcommand(
                    Command::new("corner")
                        .about("The CORNER algorithm for Fragment computation, seeded with tile-id")
                        .args(&[arg!(<TILE> "tile-id")])
                        .arg_required_else_help(true)
                )
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
        Some(("all", args)) => {
            let path = args.value_of("TIS").unwrap();
            let rows = args.value_of("ROW").unwrap().parse::<usize>().unwrap();
            let cols = args.value_of("COL").unwrap().parse::<usize>().unwrap();
            match load_tis(path.to_string()) {
                Some(tis) => {
                    // do some inference with tis
                    let seed = Node::empty(cols, rows, tis.data.n);
                    for (i, gimg) in search(seed, tis.data.clone()).into_iter().enumerate() {
                        tis.decode(gimg).save(format!("out/{}.png", i)).ok();
                    }
                }
                None => {}
            }
        }
        Some(("fragment", args)) => {
            let path = args.value_of("TIS").unwrap();
            if let Some(tis) = load_tis(path.to_string()) {
                match args.subcommand().unwrap() {
                    ("center", args) => {
                        let t = args.value_of("TILE").unwrap().parse::<usize>().unwrap();
                        if t < tis.data.n {
                            println!("CENTER with {} coming soon", t);
                        } else {
                            println!("invalid id, must be in [0, {}) not {}.", tis.data.n, t);
                        }
                    }
                    ("corner", args) => {
                        let t = args.value_of("TILE").unwrap().parse::<usize>().unwrap();
                        if t < tis.data.n {
                            println!("CORNER with {} coming soon", t);
                        } else {
                            println!("invalid id, must be in [0, {}) not {}.", tis.data.n, t);
                        }
                    }
                    ("side", args) => {
                        let t = args.value_of("TILE").unwrap().parse::<usize>().unwrap();
                        if t < tis.data.n {
                            println!("SIDE with {} coming soon", t);
                        } else {
                            println!("invalid id, must be in [0, {}) not {}.", tis.data.n, t);
                        }
                    }
                    _ => {}
                }
            }
        }
        _ => { /* catch all do nothing */ }
    }
}
