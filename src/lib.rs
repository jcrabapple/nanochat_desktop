use once_cell::sync::Lazy;
use pyo3::create_exception;
use pyo3::exceptions::PyRuntimeError;
use pyo3::prelude::*;
use tokio::runtime::Runtime;

pub use crate::api::client::NanoGPTClient;
pub use crate::database::sqlite::Database;
pub use crate::security::credentials::CredentialManager;
use secrecy::ExposeSecret;

pub mod api;
pub mod database;
pub mod security;
pub mod utils;

static RUNTIME: Lazy<Runtime> =
    Lazy::new(|| Runtime::new().expect("Failed to create Tokio runtime"));

create_exception!(nanogpt_core, APIError, PyRuntimeError);
create_exception!(nanogpt_core, DatabaseError, PyRuntimeError);

/// A Python-compatible wrapper for the NanoGPT API client.
#[pyclass]
struct PyNanoGPTClient {
    client: NanoGPTClient,
}

#[pyclass]
struct PyChunkIterator {
    rx: std::sync::mpsc::Receiver<String>,
}

#[pymethods]
impl PyChunkIterator {
    fn __iter__(slf: PyRef<'_, Self>) -> PyRef<'_, Self> {
        slf
    }

    fn __next__(mut slf: PyRefMut<'_, Self>) -> Option<String> {
        slf.rx.recv().ok()
    }
}

#[pymethods]
impl PyNanoGPTClient {
    /// Create a new NanoGPT client with the given API key.
    #[new]
    fn new(api_key: String) -> Self {
        Self {
            client: NanoGPTClient::new(api_key),
        }
    }

    /// Update the API key used by the client.
    fn set_api_key(&mut self, api_key: String) {
        self.client = NanoGPTClient::new(api_key);
    }

    /// Perform a synchronous chat completion request.
    /// This blocks the calling thread using the internal Tokio runtime.
    fn chat_completion_sync(
        &self,
        model: String,
        messages: Vec<(String, String)>,
        temperature: Option<f32>,
        max_tokens: Option<u32>,
    ) -> PyResult<String> {
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

        RUNTIME
            .block_on(async {
                self.client
                    .chat_completion(request)
                    .await
                    .map_err(|e| APIError::new_err(e.to_string()))
            })
            .and_then(|response| {
                if let Some(ref error) = response.error {
                    return Err(APIError::new_err(format!("API Error: {}", error.message)));
                }
                match response.choices {
                    Some(ref choices) if !choices.is_empty() => match choices.first() {
                        Some(choice) => Ok(choice.message.content.clone()),
                        None => Err(APIError::new_err("Failed to extract message content")),
                    },
                    _ => Err(APIError::new_err("Empty choices - no response from API")),
                }
            })
    }

    /// Stream a chat completion request.
    /// This returns a Python generator that yields content chunks.
    fn chat_completion_stream(
        &self,
        model: String,
        messages: Vec<(String, String)>,
        temperature: Option<f32>,
        max_tokens: Option<u32>,
    ) -> PyResult<PyObject> {
        let client = self.client.clone();
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
            stream: Some(true),
        };

        Python::with_gil(|py| {
            let (tx, rx) = std::sync::mpsc::channel();

            // Run the streaming in background
            std::thread::spawn(move || {
                let rt = Runtime::new().expect("Failed to create thread local runtime");
                rt.block_on(async {
                    use futures_util::StreamExt;
                    let auth = format!("Bearer {}", client.api_key.lock().await);
                    let mut response = reqwest::Client::new()
                        .post("https://nano-gpt.com/api/v1/chat/completions")
                        .header("Authorization", auth)
                        .json(&request)
                        .send()
                        .await
                        .expect("Request failed")
                        .bytes_stream();

                    while let Some(item) = response.next().await {
                        if let Ok(bytes) = item {
                            let text = String::from_utf8_lossy(&bytes);
                            for line in text.lines() {
                                if line.starts_with("data: ") {
                                    let data = &line[6..];
                                    if data == "[DONE]" {
                                        break;
                                    }
                                    if let Ok(chunk) = serde_json::from_str::<api::client::StreamChunk>(data) {
                                        if let Some(choice) = chunk.choices.first() {
                                            if let Some(ref content) = choice.delta.content {
                                                if tx.send(content.clone()).is_err() {
                                                    return;
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                });
            });

            // Create a Python iterator
            let py_iter = PyChunkIterator { rx };
            Ok(py_iter.into_py(py))
        })
    }

    /// Retrieve a list of available models from the API.
    fn list_models(&self) -> PyResult<Vec<String>> {
        RUNTIME
            .block_on(async {
                self.client
                    .list_models()
                    .await
                    .map_err(|e| APIError::new_err(e.to_string()))
            })
            .map(|models| models.into_iter().map(|m| m.id).collect())
    }
}

/// A Python-compatible wrapper for the SQLite database.
#[pyclass]
struct PyDatabase {
    db: std::sync::Mutex<Database>,
}

#[pymethods]
impl PyDatabase {
    /// Open or create a new database at the specified path.
    #[new]
    fn new(db_path: String) -> PyResult<Self> {
        let path = std::path::PathBuf::from(db_path);
        let db = Database::new(path).map_err(|e| DatabaseError::new_err(e.to_string()))?;

        Ok(Self {
            db: std::sync::Mutex::new(db),
        })
    }

    /// Create a new chat session.
    fn create_session(&self, title: String, model: String, system_prompt: String, temperature: f32) -> PyResult<PySession> {
        let db = self
            .db
            .lock()
            .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
        let session = db
            .create_session(&title, &model, &system_prompt, temperature)
            .map_err(|e| DatabaseError::new_err(e.to_string()))?;
        Ok(PySession::from(session))
    }

    /// Retrieve a session by its unique ID.
    fn get_session(&self, session_id: String) -> PyResult<Option<PySession>> {
        let db = self
            .db
            .lock()
            .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
        let session = db
            .get_session(&session_id)
            .map_err(|e| DatabaseError::new_err(e.to_string()))?;

        Ok(session.map(PySession::from))
    }

    /// Get all chat sessions, ordered by most recently updated.
    fn get_all_sessions(&self) -> PyResult<Vec<PySession>> {
        let db = self
            .db
            .lock()
            .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
        let sessions = db
            .get_all_sessions()
            .map_err(|e| DatabaseError::new_err(e.to_string()))?;

        Ok(sessions.into_iter().map(PySession::from).collect())
    }

    /// Add a new message to an existing session.
    fn create_message(
        &self,
        session_id: String,
        role: String,
        content: String,
        tokens: Option<u32>,
    ) -> PyResult<String> {
        let db = self
            .db
            .lock()
            .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
        let message = db
            .create_message(&session_id, &role, &content, tokens)
            .map_err(|e| DatabaseError::new_err(e.to_string()))?;
        Ok(message.id)
    }

    /// Get all messages for a specific session.
    fn get_messages(&self, session_id: String) -> PyResult<Vec<PyMessage>> {
        let db = self
            .db
            .lock()
            .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
        let messages = db
            .get_messages(&session_id)
            .map_err(|e| DatabaseError::new_err(e.to_string()))?;

        Ok(messages.into_iter().map(PyMessage::from).collect())
    }

    /// Delete a session and all its messages.
    fn delete_session(&self, session_id: String) -> PyResult<()> {
        let db = self
            .db
            .lock()
            .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
        db.delete_session(&session_id)
            .map_err(|e| DatabaseError::new_err(e.to_string()))?;
        Ok(())
    }

    /// Delete all messages in a specific session.
    fn delete_messages(&self, session_id: String) -> PyResult<()> {
        let db = self
            .db
            .lock()
            .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
        db.delete_messages(&session_id)
            .map_err(|e| DatabaseError::new_err(e.to_string()))?;
        Ok(())
    }

    /// Update the model for a specific session.
    fn update_session_model(&self, session_id: String, model: String) -> PyResult<()> {
        let db = self
            .db
            .lock()
            .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
        db.update_session_model(&session_id, &model)
            .map_err(|e| DatabaseError::new_err(e.to_string()))?;
        Ok(())
    }

    /// Update parameters for a specific session.
    fn update_session_params(&self, session_id: String, system_prompt: String, temperature: f32) -> PyResult<()> {
        let db = self
            .db
            .lock()
            .map_err(|e| PyRuntimeError::new_err(e.to_string()))?;
        db.update_session_params(&session_id, &system_prompt, temperature)
            .map_err(|e| DatabaseError::new_err(e.to_string()))?;
        Ok(())
    }
}

/// A Python-compatible wrapper for a chat session.
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
    system_prompt: String,
    #[pyo3(get)]
    temperature: f32,
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
            system_prompt: session.system_prompt,
            temperature: session.temperature,
            created_at: session.created_at.timestamp(),
            updated_at: session.updated_at.timestamp(),
        }
    }
}

/// A Python-compatible wrapper for a chat message.
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

/// A Python-compatible wrapper for the credential manager.
#[pyclass]
struct PyCredentialManager;

#[pymethods]
impl PyCredentialManager {
    /// Retrieve the stored API key.
    #[staticmethod]
    fn get_api_key() -> PyResult<Option<String>> {
        match CredentialManager::get_api_key() {
            Ok(key) => Ok(Some(key.expose_secret().clone())),
            Err(security::credentials::CredentialError::NotFound) => Ok(None),
            Err(e) => Err(PyRuntimeError::new_err(e.to_string())),
        }
    }

    /// Store a new API key.
    #[staticmethod]
    fn set_api_key(api_key: String) -> PyResult<()> {
        CredentialManager::set_api_key(&api_key)
            .map_err(|e| PyRuntimeError::new_err(e.to_string()))
    }

    /// Delete the stored API key.
    #[staticmethod]
    fn delete_api_key() -> PyResult<()> {
        CredentialManager::delete_api_key()
            .map_err(|e| PyRuntimeError::new_err(e.to_string()))
    }

    /// Check if an API key is stored.
    #[staticmethod]
    fn has_api_key() -> bool {
        CredentialManager::has_api_key()
    }

    /// Perform a basic validation of the API key format.
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
