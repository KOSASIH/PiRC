use axum::{
    extract::{State, Json, Query},
    http::StatusCode,
    response::Json as AxumJson,
    Form,
};
use pirc_dashboard::AppState;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

pub async fn get_metrics(State(state): State<AppState>) -> Result<AxumJson<serde_json::Value>, StatusCode> {
    let metrics = state.metrics.get_summary().await;
    Ok(AxumJson(serde_json::json!(metrics)))
}

pub async fn get_agents(State(state): State<AppState>) -> Result<AxumJson<serde_json::Value>, StatusCode> {
    let agent_state = state.agent_state.lock().unwrap();
    Ok(AxumJson(serde_json::json!({
        "channels": agent_state.channel_stats.len(),
        "users": agent_state.user_profiles.len(),
        "trading_balance": agent_state.trading_balance
    })))
}

pub async fn chat_handler(
    State(state): State<AppState>,
    Form(payload): Form<ChatRequest>,
) -> Result<AxumJson<ChatResponse>, StatusCode> {
    // Simulate AI response (integrate with real LLM)
    let response = format!("🤖 AI Reply to '{}': Pi sentiment +{}%", 
        payload.message, rand::random::<f32>() * 100.0);
    
    Ok(AxumJson(ChatResponse {
        id: Uuid::new_v4(),
        response,
        timestamp: chrono::Utc::now(),
    }))
}

#[derive(Deserialize)]
pub struct ChatRequest {
    pub message: String,
}

#[derive(Serialize)]
pub struct ChatResponse {
    pub id: Uuid,
    pub response: String,
    pub timestamp: chrono::DateTime<chrono::Utc>,
}
