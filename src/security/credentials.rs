use secrecy::{ExposeSecret, SecretString};
use thiserror::Error;

#[derive(Error, Debug)]
pub enum CredentialError {
    #[error("Failed to get credential: {0}")]
    GetError(String),
    #[error("Failed to set credential: {0}")]
    SetError(String),
    #[error("Credential not found")]
    NotFound,
}

pub struct CredentialManager;

impl CredentialManager {
    const SERVICE: &'static str = "nanogpt-chat";
    const KEY_API_KEY: &'static str = "api_key";

    pub fn get_api_key() -> Result<SecretString, CredentialError> {
        use std::fs;
        
        let config_dir = std::env::var("XDG_CONFIG_HOME")
            .map(|p| std::path::PathBuf::from(p).join("nanogpt-chat"))
            .ok()
            .or_else(|| {
                home::home_dir().map(|p| p.join(".config").join("nanogpt-chat"))
            })
            .unwrap_or(std::path::PathBuf::from(".config/nanogpt-chat"));

        let key_path = config_dir.join("api_key");

        if !key_path.exists() {
            return Err(CredentialError::NotFound);
        }

        match fs::read_to_string(&key_path) {
            Ok(key) => {
                let key = key.trim().to_string();
                if key.is_empty() {
                    Err(CredentialError::NotFound)
                } else {
                    Ok(SecretString::from(key))
                }
            }
            Err(e) => Err(CredentialError::GetError(e.to_string())),
        }
    }

    pub fn set_api_key(api_key: &str) -> Result<(), CredentialError> {
        use std::fs;
        
        let config_dir = std::env::var("XDG_CONFIG_HOME")
            .map(|p| std::path::PathBuf::from(p).join("nanogpt-chat"))
            .ok()
            .or_else(|| {
                home::home_dir().map(|p| p.join(".config").join("nanogpt-chat"))
            })
            .unwrap_or(std::path::PathBuf::from(".config/nanogpt-chat"));

        fs::create_dir_all(&config_dir)
            .map_err(|e| CredentialError::SetError(e.to_string()))?;

        fs::write(config_dir.join("api_key"), api_key)
            .map_err(|e| CredentialError::SetError(e.to_string()))?;

        Ok(())
    }

    pub fn delete_api_key() -> Result<(), CredentialError> {
        use std::fs;
        
        let config_dir = std::env::var("XDG_CONFIG_HOME")
            .map(|p| std::path::PathBuf::from(p).join("nanogpt-chat"))
            .ok()
            .or_else(|| {
                home::home_dir().map(|p| p.join(".config").join("nanogpt-chat"))
            })
            .unwrap_or(std::path::PathBuf::from(".config/nanogpt-chat"));

        let key_path = config_dir.join("api_key");

        if key_path.exists() {
            fs::remove_file(&key_path)
                .map_err(|e| CredentialError::SetError(e.to_string()))?;
        }

        Ok(())
    }

    pub fn has_api_key() -> bool {
        Self::get_api_key().is_ok()
    }

    pub fn validate_api_key(api_key: &str) -> bool {
        if api_key.len() < 10 {
            return false;
        }
        true
    }
}
