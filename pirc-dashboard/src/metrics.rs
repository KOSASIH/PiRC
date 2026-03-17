use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::sync::RwLock;
use chrono::{DateTime, Utc};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LiveMetrics {
    pub timestamp: DateTime<Utc>,
    pub messages_per_sec: f64,
    pub active_channels: usize,
    pub total_users: usize,
    pub sentiment_score: f64,
    pub trading_pnl: f64,
    pub ai_response_time: f64,
    pub user_memory_count: u64,
}

#[derive(Debug, Clone)]
pub struct MetricsStore {
    live: Arc<RwLock<LiveMetrics>>,
    history: Arc<RwLock<Vec<LiveMetrics>>>,
}

impl MetricsStore {
    pub fn new() -> Self {
        Self {
            live: Arc::new(RwLock::new(LiveMetrics::default())),
            history: Arc::new(RwLock::new(vec![])),
        }
    }

    pub async fn get_summary(&self) -> LiveMetrics {
        self.live.read().await.clone()
    }

    pub async fn get_full(&self) -> Vec<LiveMetrics> {
        self.history.read().await.clone()
    }

    pub async fn update_live(&self) {
        let mut live = self.live.write().await;
        
        // Simulate real metrics (replace with agent telemetry)
        live.timestamp = Utc::now();
        live.messages_per_sec = (rand::random::<f64>() * 15.0) + 5.0;
        live.active_channels = ((rand::random::<f64>() * 10.0) + 5.0) as usize;
        live.total_users = ((rand::random::<f64>() * 200.0) + 50.0) as usize;
        live.sentiment_score = (rand::random::<f64>() * 20.0) - 10.0;
        live.trading_pnl = (rand::random::<f64>() * 500.0) - 250.0;
        live.ai_response_time = rand::random::<f64>() * 50.0 + 20.0;
        live.user_memory_count += 3;
        
        // Keep last 100 points
        let mut history = self.history.write().await;
        history.push(live.clone());
        if history.len() > 100 {
            history.remove(0);
        }
    }
}

impl Default for LiveMetrics {
    fn default() -> Self {
        Self {
            timestamp: Utc::now(),
            messages_per_sec: 8.2,
            active_channels: 7,
            total_users: 124,
            sentiment_score: 6.4,
            trading_pnl: 124.50,
            ai_response_time: 28.3,
            user_memory_count: 456,
        }
    }
}
