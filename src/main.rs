mod backtrack;
mod eugenics;
mod genetic;
mod image;
mod matrix;

use crate::image::{load_tis, Image, TID, TIS};
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
                .args(&[arg!(<TIS> "coming soon")])
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
            match load_tis(path.to_string()) {
                Some(_tis) => {
                    // do some inference with tis
                }
                None => {}
            }
        }
        Some(("tiles", _args)) => {}
        _ => { /* catch all do nothing */ }
    }
}
