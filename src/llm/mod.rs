use std::sync::Arc;
use candle_core::{Device, Tensor};
use candle_nn::VarBuilder;
use candle_transformers::models::mistral::{Config, Model as Mistral};
use candle_transformers::generation::LogitsProcessor;
use reqwest::Client;
use serde::{Deserialize, Serialize};
use thiserror::Error;
use tokio::sync::Mutex;
use tracing::{info, warn};

pub struct LLMEngine {
    groq_client: Client,
    local_model: Option<Arc<Mutex<Mistral>>>,
    api_key: String,
}

#[derive(Error, Debug)]
pub enum LLMError {
    #[error("Groq API error: {0}")]
    Groq(String),
    #[error("Local inference error: {0}")]
    Local(String),
    #[error("No model available")]
    NoModel,
}

#[derive(Serialize)]
struct GroqRequest {
    model: String,
    messages: Vec<Message>,
    max_tokens: Option<usize>,
    temperature: Option<f32>,
}

#[derive(Deserialize)]
struct GroqResponse {
    choices: Vec<Choice>,
}

#[derive(Deserialize)]
struct Choice {
    message: Message,
}

#[derive(Serialize, Deserialize, Clone)]
struct Message {
    role: String,
    content: String,
}

impl LLMEngine {
    pub async fn new(api_key: String) -> anyhow::Result<Self> {
        let groq_client = Client::new();
        
        // Try load local Mistral 7B (optional)
        let local_model = match Self::load_local_model().await {
            Ok(model) => {
                info!("✅ Local Mistral 7B loaded");
                Some(Arc::new(Mutex::new(model)))
            }
            Err(e) => {
                warn!("⚠️ Local model failed: {}. Using Groq only.", e);
                None
            }
        };

        Ok(Self {
            groq_client,
            local_model,
            api_key,
        })
    }

    pub async fn chat(&self, prompt: &str, context: Option<&str>) -> Result<String, LLMError> {
        if let Some(model) = &self.local_model {
            // Try local first (offline)
            match self.generate_local(model, prompt, context).await {
                Ok(response) => return Ok(response),
                Err(_) => info!("Local LLM failed, falling back to Groq"),
            }
        }

        // Fallback to Groq
        self.generate_groq(prompt, context).await
    }

    async fn generate_groq(&self, prompt: &str, context: Option<&str>) -> Result<String, LLMError> {
        let messages = vec![
            Message {
                role: "system".to_string(),
                content: "You are PiRC AI - expert IRC bot + Pi Network trader.".to_string(),
            },
            Message {
                role: "user".to_string(),
                content: format!("Context: {:?}\n\n{}", context, prompt),
            },
        ];

        let request = GroqRequest {
            model: "llama3-8b-8192".to_string(),
            messages,
            max_tokens: Some(512),
            temperature: Some(0.7),
        };

        let response = self.groq_client
            .post("https://api.groq.com/openai/v1/chat/completions")
            .header("Authorization", format!("Bearer {}", self.api_key))
            .header("Content-Type", "application/json")
            .json(&request)
            .send()
            .await
            .map_err(|e| LLMError::Groq(e.to_string()))?;

        let groq_resp: GroqResponse = response.json().await
            .map_err(|e| LLMError::Groq(e.to_string()))?;

        Ok(groq_resp.choices[0].message.content.clone())
    }

    async fn generate_local(
        &self,
        model: &Arc<Mutex<Mistral>>,
        prompt: &str,
        _context: Option<&str>,
    ) -> Result<String, LLMError> {
        let model = model.lock().await;
        let device = Device::Cpu;

        // Tokenize + Generate (simplified)
        let tokens = self.tokenizer.encode(prompt, true).map_err(|e| LLMError::Local(e.to_string()))?;
        let mut logits_processor = LogitsProcessor::new(1337, Some(0.8), None);

        let mut output = String::new();
        let mut tokens_iter = tokens.into_iter();

        // Generate loop
        while let Some(next_token_id) = tokens_iter.next() {
            let logits = model.forward(&[next_token_id], &device).map_err(|e| LLMError::Local(e.to_string()))?;
            let next_token_id = logits_processor.sample(&logits).map_err(|e| LLMError::Local(e.to_string()))?;
            let token = self.tokenizer.decode(&[next_token_id]).map_err(|e| LLMError::Local(e.to_string()))?;
            output.push_str(&token);
        }

        Ok(output)
    }

    async fn load_local_model() -> anyhow::Result<Mistral> {
        let config = Config::mistral_7b();
        let vb = unsafe { VarBuilder::from_mmaped_safetensors(&["models/mistral-7b.gguf"], candle_core::DType::F16, &Device::Cpu)? };
        Ok(Mistral::load(&vb, &config)?)
    }
}
