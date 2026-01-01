pub mod api;
pub mod database;
pub mod security;
pub mod utils;

use pyo3::prelude::*;
use secrecy::ExposeSecret;

use crate::api::client::NanoGPTClient;
use crate::database::sqlite::Database;
use crate::security::credentials::CredentialManager;

#[pyclass]
struct PyNanoGPTClient {
    client: NanoGPTClient,
}

#[pymethods]
impl PyNanoGPTClient {
    #[new]
    fn new(api_key: String) -> Self {
        Self {
            client: NanoGPTClient::new(api_key),
        }
    }

    fn set_api_key(&mut self, api_key: String) {
        self.client = NanoGPTClient::new(api_key);
    }

    fn chat_completion_sync(
        &self,
        model: String,
        messages: Vec<(String, String)>,
        temperature: Option<f32>,
        max_tokens: Option<u32>,
        _stream: Option<bool>,
    ) -> PyResult<String> {
        let rt = tokio::runtime::Runtime::new().map_err(|e| {
            pyo3::exceptions::PyRuntimeError::new_err(e.to_string())
        })?;

        let messages: Vec<api::client::Message> = messages
            .into_iter()
            .map(|(role, content)| api::client::Message { role, content })
            .collect();

        let request = api::client::ChatRequest {
            model,
            messages,
            temperature,
            max_tokens,
            top_p: None,
            stream: Some(false),
        };

        rt.block_on(async {
            self.client.chat_completion(request)
                .await
                .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))
        }).and_then(|response| {
            eprintln!("DEBUG: Got response, error field: {:?}", response.error);
            eprintln!("DEBUG: choices field: {:?}", response.choices);
            if let Some(ref error) = response.error {
                return Err(pyo3::exceptions::PyRuntimeError::new_err(
                    format!("API Error: {}", error.message)
                ));
            }
            match response.choices {
                Some(ref choices) if !choices.is_empty() => {
                    eprintln!("DEBUG: First choice: {:?}", choices.first());
                    let first = choices.first();
                    eprintln!("DEBUG: First is Some: {}", first.is_some());
                    match first {
                        Some(choice) => {
                            let content = choice.message.content.clone();
                            eprintln!("DEBUG: Content: {:?}", content);
                            eprintln!("DEBUG: Content length: {}", content.len());
                            Ok(content)
                        }
                        None => Err(pyo3::exceptions::PyRuntimeError::new_err("Failed to extract message content"))
                    }
                }
                _ => Err(pyo3::exceptions::PyRuntimeError::new_err("Empty choices - no response from API"))
            }
        })
    }

    fn list_models(&self) -> PyResult<Vec<String>> {
        let rt = tokio::runtime::Runtime::new().map_err(|e| {
            pyo3::exceptions::PyRuntimeError::new_err(e.to_string())
        })?;

        rt.block_on(async {
            self.client.list_models()
                .await
                .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))
        }).map(|models| {
            models.into_iter().map(|m| m.id).collect()
        })
    }
}

#[pyclass]
struct PyDatabase {
    db: std::sync::Mutex<Database>,
}

#[pymethods]
impl PyDatabase {
    #[new]
    fn new(db_path: String) -> PyResult<Self> {
        let path = std::path::PathBuf::from(db_path);
        let db = Database::new(path)
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
        
        Ok(Self {
            db: std::sync::Mutex::new(db),
        })
    }

    fn create_session(&self, title: String, model: String) -> PyResult<PySession> {
        let db = self.db.lock().unwrap();
        let session = db.create_session(&title, &model)
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
        Ok(PySession::from(session))
    }

    fn get_session(&self, session_id: String) -> PyResult<Option<PySession>> {
        let db = self.db.lock().unwrap();
        let session = db.get_session(&session_id)
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
        
        Ok(session.map(PySession::from))
    }

    fn get_all_sessions(&self) -> PyResult<Vec<PySession>> {
        let db = self.db.lock().unwrap();
        let sessions = db.get_all_sessions()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
        
        Ok(sessions.into_iter().map(PySession::from).collect())
    }

    fn create_message(
        &self,
        session_id: String,
        role: String,
        content: String,
        tokens: Option<u32>,
    ) -> PyResult<String> {
        let db = self.db.lock().unwrap();
        let message = db.create_message(&session_id, &role, &content, tokens)
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
        Ok(message.id)
    }

    fn get_messages(&self, session_id: String) -> PyResult<Vec<PyMessage>> {
        let db = self.db.lock().unwrap();
        let messages = db.get_messages(&session_id)
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
        
        Ok(messages.into_iter().map(PyMessage::from).collect())
    }

    fn delete_session(&self, session_id: String) -> PyResult<()> {
        let db = self.db.lock().unwrap();
        db.delete_session(&session_id)
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
        Ok(())
    }

    fn delete_messages(&self, session_id: String) -> PyResult<()> {
        let db = self.db.lock().unwrap();
        db.delete_messages(&session_id)
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))?;
        Ok(())
    }
}

#[pyclass]
#[derive(Clone)]
struct PySession {
    #[pyo3(get)]
    id: String,
    #[pyo3(get)]
    title: String,
    #[pyo3(get)]
    model: String,
    #[pyo3(get)]
    created_at: i64,
    #[pyo3(get)]
    updated_at: i64,
}

impl PySession {
    fn from(session: database::sqlite::ChatSession) -> Self {
        Self {
            id: session.id,
            title: session.title,
            model: session.model,
            created_at: session.created_at.timestamp(),
            updated_at: session.updated_at.timestamp(),
        }
    }
}

#[pyclass]
#[derive(Clone)]
struct PyMessage {
    #[pyo3(get)]
    id: String,
    #[pyo3(get)]
    session_id: String,
    #[pyo3(get)]
    role: String,
    #[pyo3(get)]
    content: String,
    #[pyo3(get)]
    created_at: i64,
    #[pyo3(get)]
    tokens: Option<u32>,
}

impl PyMessage {
    fn from(message: database::sqlite::ChatMessage) -> Self {
        Self {
            id: message.id,
            session_id: message.session_id,
            role: message.role,
            content: message.content,
            created_at: message.created_at.timestamp(),
            tokens: message.tokens,
        }
    }
}

#[pyclass]
struct PyCredentialManager;

#[pymethods]
impl PyCredentialManager {
    #[staticmethod]
    fn get_api_key() -> PyResult<Option<String>> {
        match CredentialManager::get_api_key() {
            Ok(key) => Ok(Some(key.expose_secret().clone())),
            Err(security::credentials::CredentialError::NotFound) => Ok(None),
            Err(e) => Err(pyo3::exceptions::PyRuntimeError::new_err(e.to_string())),
        }
    }

    #[staticmethod]
    fn set_api_key(api_key: String) -> PyResult<()> {
        CredentialManager::set_api_key(&api_key)
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))
    }

    #[staticmethod]
    fn delete_api_key() -> PyResult<()> {
        CredentialManager::delete_api_key()
            .map_err(|e| pyo3::exceptions::PyRuntimeError::new_err(e.to_string()))
    }

    #[staticmethod]
    fn has_api_key() -> bool {
        CredentialManager::has_api_key()
    }

    #[staticmethod]
    fn validate_api_key(api_key: String) -> bool {
        CredentialManager::validate_api_key(&api_key)
    }
}

#[pymodule]
fn nanogpt_core(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<PyNanoGPTClient>()?;
    m.add_class::<PyDatabase>()?;
    m.add_class::<PySession>()?;
    m.add_class::<PyMessage>()?;
    m.add_class::<PyCredentialManager>()?;
    Ok(())
}
