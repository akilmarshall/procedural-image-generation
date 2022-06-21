use std::fs::{create_dir_all, remove_dir_all};
use std::path::Path;

pub fn mkdir(p: &str) {
    // check if path exists
    // true -> recursive delete
    // make new directory at path
    let path = Path::new(p).to_path_buf();
    if path.is_dir() {
        remove_dir_all(path.clone()).ok();
    }
    create_dir_all(path).ok();
}
