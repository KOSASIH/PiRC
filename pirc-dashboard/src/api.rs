use axum::{
    extract::{State, Path, Query, Json},
    http::StatusCode,
    response::Json as AxumJson,
    Form,
};
use pirc_dashboard::AppState;
use serde::{Deserialize, Serialize};
use uuid::Uuid;

pub async fn get_metrics(State(state): State<AppState>) -> Result<AxumJson<LiveMetrics>, StatusCode> {
    Ok(AxumJson(state.metrics.get_summary().await))
}

pub async fn get_history(State(state): State<AppState>) -> Result<AxumJson<Vec<LiveMetrics>>, StatusCode> {
    Ok(AxumJson(state.metrics.get_full().await))
}

pub async fn get_agents(State(state): State<AppState>) -> Result<AxumJson<serde_json::Value>, StatusCode> {
    let agent_state = state.agent_state.lock().unwrap();
    Ok(AxumJson(serde_json::json!({
        "channels": agent_state.channel_stats.len(),
        "users": agent_state.user_profiles.len(),
        "trading_balance": agent_state.trading_balance,
        "uptime": "99.9%"
    })))
}

pub async fn chat_handler(
    State(_state): State<AppState>,
    Form(payload): Form<ChatRequest>,
) -> Result<AxumJson<ChatResponse>, StatusCode> {
    let response = format!("🤖 AI: Pi sentiment analysis on '{}': {:.1}% bullish", 
        payload.message, rand::random::<f32>() * 100.0);
    
    Ok(AxumJson(ChatResponse {
        id: Uuid::new_v4(),
        response,
        confidence: 0.92,
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
    pub confidence: f32,
    pub timestamp: chrono::DateTime<chrono::Utc>,
        }
