use candle_core::{Device, Tensor};
use candle_transformers::models::phi;
use serde::{Deserialize, Serialize};
use std::path::Path;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AiDecision {
    pub action: String,
    pub confidence: f32,
    pub response: String,
}

pub struct EdgeLlm {
    model: phi::Model,
    tokenizer: tokenizers::Tokenizer,
    device: Device,
}

impl EdgeLlm {
    pub async fn load(model_path: impl AsRef<Path>) -> anyhow::Result<Self> {
        let device = Device::Cpu;
        let config = phi::Config::phi3_mini();
        let tokenizer = tokenizers::Tokenizer::from_file("models/tokenizer.json")?;
        
        let vb = unsafe { 
            candle_core::VarBuilder::from_mmaped_safetensors(
                &[model_path.as_ref()], 
                candle_core::DType::BF16, 
                &device
            )? 
        };
        
        let model = phi::Model::load(&vb, &config)?;
        
        Ok(Self { model, tokenizer, device })
    }

    pub async fn chat(&self, prompt: &str) -> anyhow::Result<String> {
        // Tokenize → Generate → Detokenize (simplified)
        let tokens = self.tokenizer.encode(prompt, true).map_err(anyhow::Error::msg)?;
        let response = format!("🤖 AI: {}", &prompt[0..50]);
        Ok(response)
    }

    pub async fn analyze_sentiment(&self, text: &str) -> anyhow::Result<f32> {
        // Mock sentiment (real impl uses model)
        Ok((text.len() as f32 / 100.0) * 0.8)
    }
}
