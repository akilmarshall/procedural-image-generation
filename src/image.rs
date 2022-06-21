//! Image processing, contains structures and functions concerned with the ingest of processing of
//! images into structred data for image generation.
use crate::structures::matrix::{Matrix, Neighbors};
use crate::util::mkdir;
use image::{imageops, GenericImageView, RgbaImage};
use imageops::overlay;
use rand::Rng;
use serde::{Deserialize, Serialize};
use serde_json;
use std::collections::HashSet;
use std::fs::{read_dir, File};
use std::io::Write;

/// A type for directions, TODO: turn into an enum
pub type Direction = usize;

/// target type for image generation.
pub type IDMatrix = Matrix<Option<usize>>;

/// Representation of a tiled image used in the image processing part of the process.
pub struct Image {
    pub tile_width: u32,
    pub tile_height: u32,
    rows: u32,
    cols: u32,
    img: RgbaImage,
    tiles: Vec<RgbaImage>,
}

impl Neighbors for Image {
    fn shape(&self) -> (usize, usize) {
        (self.cols as usize, self.rows as usize)
    }
}

impl Image {
    pub fn new(tile_width: u32, tile_height: u32, path: String) -> Self {
        let img = image::open(path).unwrap();
        let (width, height) = img.dimensions();
        let cols = width / tile_width;
        let rows = height / tile_height;
        let mut unique_tiles = HashSet::new();
        for i in 0..cols {
            for j in 0..rows {
                let u = i * tile_width;
                let v = j * tile_height;
                let subimg = imageops::crop_imm(&img, u, v, tile_width, tile_height);
                unique_tiles.insert(subimg.to_image());
            }
        }
        Image {
            tile_width,
            tile_height,
            rows,
            cols,
            img: img.to_rgba8(),
            tiles: unique_tiles.into_iter().collect(),
        }
    }

    /// O(n) query for a tile id.
    fn tile_id(&self, tile: RgbaImage) -> Option<usize> {
        for (i, t) in self.tiles.iter().enumerate() {
            if &tile == t {
                return Some(i);
            }
        }
        None
    }
    /// Compute a slim "id" matrix representing the original tiled image.
    fn id_matrix(&self) -> IDMatrix {
        let mut out = IDMatrix::new(self.cols as usize, self.rows as usize);
        for i in 0..out.cols {
            for j in 0..out.rows {
                let u = i * self.tile_width as usize;
                let v = j * self.tile_height as usize;
                let subimg = imageops::crop_imm(
                    &self.img,
                    u as u32,
                    v as u32,
                    self.tile_width,
                    self.tile_height,
                );
                out.set(i as usize, j as usize, self.tile_id(subimg.to_image()));
            }
        }
        out
    }
    /// Compute/Return the neighbor mapping for the tiled image.
    /// tileid -> (neighbor -> [tileid])
    ///           _ 1 _                 
    /// neighbors 2 i 0                 
    /// of i      _ 3 _                 
    pub fn compute_neighborhoods(&self) -> Vec<Neighborhood> {
        let img = self.id_matrix();
        let n = self.tiles.len();
        let mut neighborhoods: Vec<Neighborhood> = (0..n).map(|_| Neighborhood::new()).collect();
        // scan the image tile by tile and process it's neighbors
        for i in 0..img.cols() {
            for j in 0..img.rows() {
                if let Some(t) = img.at(i as usize, j as usize) {
                    for (d, h, k) in self.neighbors(i as usize, j as usize) {
                        if let Some(n) = img.at(h, k) {
                            neighborhoods[t].insert(n, d);
                        }
                    }
                }
            }
        }
        neighborhoods
    }
    pub fn tiles(&self) -> &Vec<RgbaImage> {
        &self.tiles
    }
}

/// Tiled Image Data with it's tile set
#[derive(Debug, Clone)]
pub struct TIS {
    pub data: TID,
    pub tiles: Vec<RgbaImage>,
}

impl TIS {
    pub fn new(data: TID, tiles: Vec<RgbaImage>) -> Self {
        TIS { data, tiles }
    }
    pub fn save_tilesheet(&self, path: String) {
        mkdir(&path);
        let mut i: u32 = 0;
        for tile in &self.tiles {
            tile.save(format!("{}/{}.png", &path, i)).ok();
            i += 1;
        }
    }
    pub fn save_all(&self, path: String) {
        let flat_data = serde_json::to_string(&self.data).unwrap();
        // DirBuilder::new().recursive(true).create(&path).unwrap();
        mkdir(&path);
        self.save_tilesheet(String::from(format!("{}/tiles", path)));
        match File::create(format!("{}/TIS.json", path)) {
            Ok(mut file) => {
                file.write_all(flat_data.as_bytes()).ok();
            }
            _ => {}
        }
    }
    /// Use TIS to "decode" an image matrix into an RgbaImage
    pub fn decode(&self, image: IDMatrix) -> RgbaImage {
        let width: u32 = image.cols() as u32 * self.data.width;
        let height: u32 = image.rows() as u32 * self.data.height;
        let mut img = RgbaImage::new(width, height);

        for i in 0..width / self.data.width {
            for j in 0..height / self.data.height {
                let x = i * self.data.width;
                let y = j * self.data.height;
                if let Some(id) = image.at(i as usize, j as usize) {
                    let tile = &self.tiles[id];
                    overlay(&mut img, tile, i64::from(x), i64::from(y));
                }
            }
        }
        img
    }
}

type Hood = [HashSet<usize>; 4];

#[derive(Serialize, Deserialize, Clone, Debug)]
pub struct Neighborhood {
    neighbors: Hood,
}

impl Neighborhood {
    pub fn new() -> Self {
        Neighborhood {
            neighbors: [
                HashSet::new(),
                HashSet::new(),
                HashSet::new(),
                HashSet::new(),
            ],
        }
    }
    /// Builder syntax to quickly define the neighborhood
    pub fn neighbors(&mut self, neighbors: Hood) -> &mut Self {
        self.neighbors = neighbors;
        self
    }
    pub fn insert(&mut self, u: usize, d: Direction) {
        if d < 4 {
            self.neighbors[d].insert(u);
        }
    }
    pub fn neighborhood(&self, d: Direction) -> HashSet<usize> {
        self.neighbors[d].clone()
    }
}

/// Tiled Image Data
/// Minimum required data to describe an image, intended for use in inference.
/// Employs builder methods.
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct TID {
    neighborhoods: Vec<Neighborhood>,
    pub n: usize,
    pub width: u32,
    pub height: u32,
}

impl TID {
    pub fn new() -> Self {
        TID {
            neighborhoods: Vec::new(),
            n: 0,
            width: 0,
            height: 0,
        }
    }
    pub fn mapping(&mut self, neighborhoods: Vec<Neighborhood>) -> &mut Self {
        self.neighborhoods = neighborhoods;
        self
    }
    pub fn n(&mut self, n: usize) -> &mut Self {
        self.n = n;
        self
    }
    pub fn width(&mut self, width: u32) -> &mut Self {
        self.width = width;
        self
    }
    pub fn height(&mut self, height: u32) -> &mut Self {
        self.height = height;
        self
    }
    /// generate a random image representation
    pub fn rng(&self, mut image: IDMatrix) -> IDMatrix {
        let mut rng = rand::thread_rng();
        for i in 0..image.rows() {
            for j in 0..image.cols() {
                image.set(i, j, Some(rng.gen_range(0..=self.n)));
            }
        }
        image
    }
    /// Neighborhood function
    /// return a HashSet of the directional neighbors of t
    pub fn neighborhood(&self, t: usize, d: Direction) -> HashSet<usize> {
        self.neighborhoods[t].neighborhood(d)
    }
}

fn load_tiles(dir: String, n: usize) -> Vec<RgbaImage> {
    let mut tiles = Vec::new();
    for i in 0..n {
        let path = format!("{}/tiles/{}.png", dir, i);
        let tile = ::image::open(path).unwrap();
        tiles.push(tile.to_rgba8());
    }
    tiles
}
fn load_tid(path: String) -> Option<TID> {
    let dir = format!("{}/TIS.json", path);
    match File::open(&dir) {
        Ok(file) => match serde_json::from_reader(file) {
            Ok(tid) => return Some(tid),
            Err(e) => {
                println!("something bad happened when decoding {}\n{}", &dir, e)
            }
        },
        Err(e) => {
            println!("something bad happened opening {}, FILE IO\n{}", &dir, e)
        }
    }
    None
}
pub fn load_tis(dir: String) -> Option<TIS> {
    match load_tid(dir.to_string()) {
        Some(data) => {
            let tiles = load_tiles(dir, data.n);
            return Some(TIS { data, tiles });
        }
        _ => {}
    }
    None
}

#[cfg(test)]
mod tests {
    use super::*;

    // #[test]
    // fn
}
