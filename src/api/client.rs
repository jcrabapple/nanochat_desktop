use reqwest::{Client, Error};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::sync::Mutex;

const BASE_URL: &str = "https://nano-gpt.com/api/v1";

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Message {
    pub role: String,
    pub content: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChatRequest {
    pub model: String,
    pub messages: Vec<Message>,
    pub temperature: Option<f32>,
    pub max_tokens: Option<u32>,
    pub top_p: Option<f32>,
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
    pub id: String,
    pub object: String,
    pub created: u64,
    pub model: String,
    pub choices: Vec<StreamChoice>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct StreamChoice {
    pub index: u32,
    pub delta: Message,
    pub finish_reason: Option<String>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct ModelInfo {
    pub id: String,
    pub name: String,
    pub object: Option<String>,
    pub created: Option<u64>,
    pub owned_by: Option<String>,
    pub permission: Option<Vec<serde_json::Value>>,
}

pub struct NanoGPTClient {
    client: Client,
    api_key: Arc<Mutex<String>>,
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
        
        let response = self.client
            .post(&format!("{}/chat/completions", BASE_URL))
            .header("Authorization", auth)
            .header("Content-Type", "application/json")
            .json(&request)
            .send()
            .await?;

        response.json().await
    }

    pub async fn list_models(&self) -> Result<Vec<ModelInfo>, Error> {
        let auth = self.auth_headers().await?;
        
        self.client
            .get(&format!("{}/models", BASE_URL))
            .header("Authorization", auth)
            .send()
            .await?
            .json()
            .await
    }
}
