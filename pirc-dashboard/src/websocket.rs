use axum::{
    extract::ws::{WebSocketUpgrade, WebSocket, Message},
    response::IntoResponse,
    Error,
};
use axum::extract::State;
use futures_util::{sink::SinkExt, stream::StreamExt};
use futures::stream::Stream;
use pirc_dashboard::AppState;
use serde_json::json;
use std::sync::Arc;
use tokio::sync::broadcast::{self, Sender};
use tokio_stream::wrappers::BroadcastStream;
use tracing::{info, error};

pub type MetricsSender = Sender<serde_json::Value>;

pub fn broadcast_channel(capacity: usize) -> (MetricsSender, impl Stream<Item = serde_json::Value> + Send) {
    let (tx, rx) = broadcast::channel(capacity);
    let stream = BroadcastStream::new(rx);
    (tx, stream)
}

pub async fn ws_handler(
    ws: WebSocketUpgrade,
    State(state): State<AppState>,
) -> impl IntoResponse {
    ws.on_upgrade(move |socket| {
        handle_socket(socket, state.clone())
    })
}

async fn handle_socket(socket: WebSocket, state: AppState) {
    let (mut sender, mut receiver) = socket.split();

    // Send initial metrics
    let initial_metrics = state.metrics.get_summary().await;
    if let Err(e) = sender.send(Message::Text(serde_json::to_string(&initial_metrics).unwrap())).await {
        error!("Failed to send initial metrics: {}", e);
        return;
    }

    // Client → Server messages
    let mut recv_task = tokio::spawn(async move {
        while let Some(Ok(msg)) = receiver.next().await {
            match msg {
                Message::Text(text) => {
                    info!("Client sent: {}", text);
                    // Handle chat, commands, etc.
                }
                Message::Close(_) => break,
                _ => {}
            }
        }
    });

    // Server → Client metrics broadcast
    let mut interval = tokio::time::interval(tokio::time::Duration::from_secs(1));
    loop {
        tokio::select! {
            _ = interval.tick() => {
                // Live metrics update
                let metrics = state.metrics.get_summary().await;
                let msg = json!({
                    "type": "metrics_update",
                    "data": metrics,
                    "timestamp": chrono::Utc::now().to_rfc3339()
                });

                if let Err(e) = sender.send(Message::Text(msg.to_string())).await {
                    error!("WebSocket send error: {}", e);
                    break;
                }
            }
            _ = recv_task => break,
        }
    }
}

// Background broadcaster task
pub async fn metrics_broadcaster(state: AppState, tx: MetricsSender) {
    let mut interval = tokio::time::interval(tokio::time::Duration::from_millis(500));
    
    loop {
        interval.tick().await;
        
        // Agent state sync
        let agent_state = state.agent_state.lock().unwrap();
        let metrics = state.metrics.get_summary().await;
        
        let broadcast_msg = json!({
            "type": "live_update",
            "metrics": metrics,
            "agents": {
                "channels": agent_state.channel_stats.len(),
                "users": agent_state.user_profiles.len(),
                "balance": agent_state.trading_balance
            },
            "trading": {
                "pnl": metrics.trading_pnl,
                "sentiment": metrics.sentiment_score
            }
        });

        if let Err(e) = tx.send(broadcast_msg) {
            tracing::warn!("Failed to broadcast metrics: {}", e);
        }
    }
}
