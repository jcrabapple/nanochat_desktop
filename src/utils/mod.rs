use std::path::PathBuf;

pub fn get_data_dir() -> PathBuf {
    let mut path = dirs::home_dir().unwrap_or(PathBuf::from("."));
    path.push(".local");
    path.push("share");
    path.push("nanogpt-chat");
    std::fs::create_dir_all(&path).ok();
    path
}

pub fn get_config_dir() -> PathBuf {
    let mut path = dirs::home_dir().unwrap_or(PathBuf::from("."));
    path.push(".config");
    path.push("nanogpt-chat");
    std::fs::create_dir_all(&path).ok();
    path
}

pub fn get_database_path() -> PathBuf {
    let mut path = get_data_dir();
    path.push("chat.db");
    path
}
