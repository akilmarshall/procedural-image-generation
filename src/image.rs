use image::{imageops, GenericImageView, RgbaImage};
use imageops::overlay;
use rand::Rng;
use serde::{Deserialize, Serialize};
use serde_json;
use std::collections::HashSet;
use std::fs;
use std::fs::{read_dir, DirBuilder, File};
use std::io::Write;

/// Counter object specialized to usize.
/// Provides an interface to increase and query statistics about the group.
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct Counter {
    n: usize,
    data: Vec<usize>,
}

impl Counter {
    /// New Counter object to track n items.
    pub fn new(n: usize) -> Self {
        Counter {
            n,
            data: (0..n).map(|_| 0).collect(),
        }
    }
    /// Is i valid with respect to the instance.
    fn valid(&self, i: usize) -> bool {
        i < self.n
    }
    /// Attempt to insert i into the group.
    pub fn insert(&mut self, i: usize) {
        if self.valid(i) {
            self.data[i] += 1;
        }
    }
    /// What is the population of i?
    pub fn raw_query(&self, i: usize) -> Option<usize> {
        if self.valid(i) {
            return Some(self.data[i]);
        }
        None
    }
    /// What is the population of the group?
    fn total(&self) -> usize {
        self.data.iter().fold(0, |a, b| a + b)
    }
    /// What proportion of the group does i represent? Returns in [0, 1).
    pub fn query(&self, i: usize) -> Option<f32> {
        if self.valid(i) {
            let a = self.raw_query(i).unwrap() as f32;
            let b = self.total() as f32;
            return Some(a / b);
        }
        None
    }
}

/// target type for image generation.
pub type IDMatrix = Vec<Vec<Option<usize>>>;

/// Representation of a tiled image used in the image processing part of the process.
pub struct Image {
    pub tile_width: u32,
    pub tile_height: u32,
    rows: u32,
    cols: u32,
    img: RgbaImage,
    tiles: Vec<RgbaImage>,
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
        let mut out = Vec::new();
        for i in 0..self.cols {
            let mut row = Vec::new();
            for j in 0..self.rows {
                let u = i * self.tile_width;
                let v = j * self.tile_height;
                let subimg = imageops::crop_imm(&self.img, u, v, self.tile_width, self.tile_height);
                row.push(self.tile_id(subimg.to_image()));
            }
            out.push(row);
        }
        out
    }
    /// Return a list of neighbors to (x, y)
    fn neighbor(&self, x: usize, y: usize) -> Vec<(usize, usize, usize)> {
        let mut out = Vec::new();
        if x < (self.cols - 1) as usize {
            out.push((0, x + 1, y));
        }
        if y > 1 {
            out.push((1, x, y - 1));
        }
        if x > 1 {
            out.push((2, x - 1, y));
        }
        if y < (self.rows - 1) as usize {
            out.push((3, x, y + 1));
        }
        out
    }
    /// Compute/Return the neighbor mapping for the tiled image.
    /// tileid -> (neighbor -> [tileid])
    ///           _ 1 _                 
    /// neighbors 2 i 0                 
    /// of i      _ 3 _                 
    pub fn compute_mapping(&self) -> Vec<Vec<Counter>> {
        let img = self.id_matrix();
        let mut mapping = Vec::new();
        let n = self.tiles.len();
        for _ in 0..n {
            mapping.push(Vec::from([
                Counter::new(n),
                Counter::new(n),
                Counter::new(n),
                Counter::new(n),
            ]));
        }
        for i in 0..self.cols {
            for j in 0..self.rows {
                if let Some(t) = img[i as usize][j as usize] {
                    for (nid, h, k) in self.neighbor(i as usize, j as usize) {
                        mapping[t as usize][nid].insert(img[h][k].unwrap());
                    }
                }
            }
        }
        mapping
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
        fs::create_dir(&path).ok();
        let mut i: u32 = 0;
        for tile in &self.tiles {
            tile.save(format!("{}/{}.png", &path, i)).ok();
            i += 1;
        }
    }
    pub fn save_all(&self, path: String) {
        let flat_data = serde_json::to_string(&self.data).unwrap();
        DirBuilder::new().recursive(true).create(&path).unwrap();
        self.save_tilesheet(String::from(format!("{}/tiles", path)));
        match File::create(format!("{}/TIS.json", path)) {
            Ok(mut file) => {
                file.write_all(flat_data.as_bytes()).ok();
            }
            _ => {}
        }
    }
    /// Use TIS to "decode" an image matrix into an RgbaImage
    pub fn decode(self, image: IDMatrix) -> RgbaImage {
        let width: u32 = image.len() as u32 * self.data.width;
        let height: u32 = image[0].len() as u32 * self.data.height;
        let mut img = RgbaImage::new(width, height);

        for i in 0..width / self.data.width {
            for j in 0..height / self.data.height {
                let x = i * self.data.width;
                let y = j * self.data.height;
                if let Some(id) = image[i as usize][j as usize] {
                    let tile = &self.tiles[id];
                    overlay(&mut img, tile, i64::from(x), i64::from(y));
                }
            }
        }
        img
    }
}

/// Tiled Image Data
/// Minimum required data to describe an image, intended for use in inference.
/// Employs builder methods.
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct TID {
    pub mapping: Vec<Vec<Counter>>,
    pub n: usize,
    pub width: u32,
    pub height: u32,
}

impl TID {
    pub fn new() -> Self {
        TID {
            mapping: Vec::new(),
            n: 0,
            width: 0,
            height: 0,
        }
    }
    pub fn mapping(&mut self, mapping: Vec<Vec<Counter>>) -> &mut Self {
        self.mapping = mapping;
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
        for i in 0..image.len() {
            for j in 0..image[0].len() {
                image[i][j] = Some(rng.gen_range(0..=self.n));
            }
        }
        image
    }
}

/// generate an empty image representation
pub fn empty(n: usize, m: usize) -> IDMatrix {
    (0..n).map(|_| (0..m).map(|_| None).collect()).collect()
}

fn load_tiles(dir: String) -> Vec<RgbaImage> {
    let mut tiles = Vec::new();
    for s in read_dir(format!("{}/tiles", dir)).unwrap() {
        if let Ok(tile_path) = s {
            let tile = ::image::open(tile_path.path()).unwrap();
            tiles.push(tile.to_rgba8());
        }
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
            return Some(TIS {
                data,
                tiles: load_tiles(dir),
            })
        }
        _ => {}
    }
    None
}
