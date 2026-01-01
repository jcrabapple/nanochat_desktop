use crate::database::sqlite::Database;
use tempfile::NamedTempFile;

#[test]
fn test_database_creation() {
    let tmp_file = NamedTempFile::new().unwrap();
    let db = Database::new(tmp_file.path().to_path_buf()).unwrap();
    
    let sessions = db.get_all_sessions().unwrap();
    assert_eq!(sessions.len(), 0);
}
