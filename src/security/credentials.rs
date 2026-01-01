use secrecy::SecretString;
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
    pub fn get_api_key() -> Result<SecretString, CredentialError> {
        pyo3::Python::with_gil(|py| {
            let module = py.import("nanogpt_chat.utils.credentials")
                .map_err(|e| CredentialError::GetError(e.to_string()))?;

            let get_key = module.getattr("SecureCredentialManager")
                .and_then(|cm| cm.getattr("get_api_key"))
                .map_err(|e| CredentialError::GetError(e.to_string()))?;

            let result = get_key.call0()
                .map_err(|e| CredentialError::GetError(e.to_string()))?;

            match result.extract::<Option<String>>() {
                Ok(Some(key)) => Ok(SecretString::from(key)),
                Ok(None) => Err(CredentialError::NotFound),
                Err(e) => Err(CredentialError::GetError(e.to_string())),
            }
        })
    }

    pub fn set_api_key(api_key: &str) -> Result<(), CredentialError> {
        pyo3::Python::with_gil(|py| {
            let module = py.import("nanogpt_chat.utils.credentials")
                .map_err(|e| CredentialError::SetError(e.to_string()))?;

            let set_key = module.getattr("SecureCredentialManager")
                .and_then(|cm| cm.getattr("set_api_key"))
                .map_err(|e| CredentialError::SetError(e.to_string()))?;

            set_key.call1((api_key,))
                .map_err(|e| CredentialError::SetError(e.to_string()))?;

            Ok(())
        })
    }

    pub fn delete_api_key() -> Result<(), CredentialError> {
        pyo3::Python::with_gil(|py| {
            let module = py.import("nanogpt_chat.utils.credentials")
                .map_err(|e| CredentialError::SetError(e.to_string()))?;

            let delete_key = module.getattr("SecureCredentialManager")
                .and_then(|cm| cm.getattr("delete_api_key"))
                .map_err(|e| CredentialError::SetError(e.to_string()))?;

            delete_key.call0()
                .map_err(|e| CredentialError::SetError(e.to_string()))?;

            Ok(())
        })
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
