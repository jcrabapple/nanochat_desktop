use reqwest::{Client, Error, StatusCode};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use std::time::Duration;
use tokio::sync::Mutex;
use tokio::time::sleep;

const BASE_URL: &str = "https://nano-gpt.com/api/v1";
const MAX_RETRIES: u32 = 3;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ErrorCategory {
    Authentication,
    RateLimit,
    Network,
    Server,
    InvalidRequest,
    Unknown,
}

impl ErrorCategory {
    pub fn from_status(status: StatusCode) -> Self {
        match status {
            StatusCode::UNAUTHORIZED | StatusCode::FORBIDDEN => Self::Authentication,
            StatusCode::TOO_MANY_REQUESTS => Self::RateLimit,
            s if s.is_client_error() => Self::InvalidRequest,
            s if s.is_server_error() => Self::Server,
            _ => Self::Unknown,
        }
    }
}

// ... rest of the structs ...

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Message {
    pub role: String,
    pub content: serde_json::Value,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DeltaMessage {
    pub role: Option<String>,
    pub content: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChatRequest {
    pub model: String,
    pub messages: Vec<Message>,
    pub temperature: Option<f32>,
    pub max_tokens: Option<u32>,
    pub top_p: Option<f32>,
    pub frequency_penalty: Option<f32>,
    pub presence_penalty: Option<f32>,
    pub stream: Option<bool>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct ApiError {
    pub message: String,
    pub r#type: Option<String>,
    pub code: Option<String>,
    pub status: Option<u32>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct ChatResponse {
    pub id: Option<String>,
    pub object: Option<String>,
    pub created: Option<u64>,
    pub model: Option<String>,
    pub choices: Option<Vec<Choice>>,
    pub usage: Option<Usage>,
    pub error: Option<ApiError>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct Choice {
    pub index: u32,
    pub message: Message,
    pub finish_reason: Option<String>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct Usage {
    pub prompt_tokens: u32,
    pub completion_tokens: u32,
    pub total_tokens: u32,
}

#[derive(Debug, Clone, Deserialize)]
pub struct StreamChunk {
    pub id: Option<String>,
    pub object: Option<String>,
    pub created: Option<u64>,
    pub model: Option<String>,
    pub choices: Vec<StreamChoice>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct StreamChoice {
    pub index: u32,
    pub delta: DeltaMessage,
    pub finish_reason: Option<String>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct ModelInfo {
    pub id: String,
    pub name: Option<String>,
    pub object: Option<String>,
    pub created: Option<u64>,
    pub owned_by: Option<String>,
    pub permission: Option<Vec<serde_json::Value>>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct ModelListResponse {
    pub data: Vec<ModelInfo>,
}

pub struct NanoGPTClient {
    pub client: Client,
    pub api_key: Arc<Mutex<String>>,
}

impl Clone for NanoGPTClient {
    fn clone(&self) -> Self {
        Self {
            client: self.client.clone(),
            api_key: self.api_key.clone(),
        }
    }
}

impl NanoGPTClient {
    pub fn new(api_key: String) -> Self {
        Self {
            client: Client::new(),
            api_key: Arc::new(Mutex::new(api_key)),
        }
    }

    async fn auth_headers(&self) -> Result<String, Error> {
        let key = self.api_key.lock().await;
        Ok(format!("Bearer {}", key))
    }

    pub async fn chat_completion(
        &self,
        request: ChatRequest,
    ) -> Result<ChatResponse, Error> {
        let auth = self.auth_headers().await?;
        let mut retries = 0;
        
        loop {
            let response = self.client
                .post(format!("{}/chat/completions", BASE_URL))
                .header("Authorization", &auth)
                .header("Content-Type", "application/json")
                .json(&request)
                .send()
                .await;

            match response {
                Ok(resp) => {
                    let status = resp.status();
                    if status.is_success() {
                        return resp.json().await;
                    }
                    
                    if status == StatusCode::TOO_MANY_REQUESTS || status.is_server_error() {
                        if retries < MAX_RETRIES {
                            retries += 1;
                            let delay = Duration::from_millis(1000 * 2u64.pow(retries - 1));
                            sleep(delay).await;
                            continue;
                        }
                    }
                    
                    return resp.json().await;
                }
                Err(e) => {
                    if e.is_timeout() || e.is_connect() {
                        if retries < MAX_RETRIES {
                            retries += 1;
                            let delay = Duration::from_millis(1000 * 2u64.pow(retries - 1));
                            sleep(delay).await;
                            continue;
                        }
                    }
                    return Err(e);
                }
            }
        }
    }

    pub async fn list_models(&self) -> Result<Vec<ModelInfo>, Error> {
        let auth = self.auth_headers().await?;
        
        let response: ModelListResponse = self.client
            .get(format!("{}/models", BASE_URL))
            .header("Authorization", auth)
            .send()
            .await?
            .json()
            .await?;
            
        Ok(response.data)
    }
}
