mod api;
mod templates;
mod metrics;
mod websocket;

use api::{agent_api, metrics_api, trading_api};
use axum::{
    extract::State,
    http::StatusCode,
    response::Html,
    routing::{get, post},
    Router,
};
use metrics::MetricsStore;
use pirc_ai_agent::{AutonomousAgent, AgentState};
use sqlx::{SqlitePool, sqlite::SqlitePoolOptions};
use std::net::SocketAddr;
use std::sync::{Arc, Mutex};
use tokio::signal;
use tower_http::cors::CorsLayer;
use tracing::{info, Level};
use websocket::broadcast_channel;

#[derive(Clone)]
pub struct AppState {
    pub metrics: Arc<MetricsStore>,
    pub agent_state: Arc<Mutex<AgentState>>,
    pub db: SqlitePool,
    pub qdrant_client: qdrant_client::QdrantClient,
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Logging
    tracing_subscriber::fmt()
        .with_max_level(Level::INFO)
        .init();

    info!("🚀 Starting PiRC AI Dashboard...");

    // Database
    let db = SqlitePoolOptions::new()
        .max_connections(10)
        .connect("sqlite://dashboard.db")
        .await?;

    sqlx::migrate!("pirc-dashboard/src/migrations")
        .run(&db)
        .await?;

    // Metrics Store
    let metrics = Arc::new(MetricsStore::new());

    // Qdrant Vector DB
    let qdrant_client = qdrant_client::QdrantClient::from_url("http://localhost:6333").build()?;

    // Agent State (shared with AI agents)
    let agent_state = Arc::new(Mutex::new(AgentState::default()));

    // App State
    let state = AppState {
        metrics,
        agent_state,
        db,
        qdrant_client,
    };

    // Background tasks
    tokio::spawn(metrics_worker(state.clone()));
    tokio::spawn(sync_agent_stats(state.clone()));

    // WebSocket broadcaster
    let (broadcast_tx, _) = broadcast_channel(100);

    // Axum Router
    let app = Router::new()
        .route("/", get(index_handler))
        .route("/dashboard", get(dashboard_handler))
        .route("/api/metrics", get(metrics_api::get_metrics))
        .route("/api/trading", get(trading_api::get_trading))
        .route("/api/agents", get(agent_api::get_agents))
        .route("/api/chat", post(api::chat_handler))
        .route("/ws", get(websocket::ws_handler))
        .layer(CorsLayer::permissive())
        .layer(tower::ServiceBuilder::new().propagate_x_request_id())
        .with_state(state);

    let addr = SocketAddr::from(([0, 0, 0, 0], 8080));
    info!("📊 Dashboard available at http://localhost:{}", 8080);

    let listener = tokio::net::TcpListener::bind(addr).await?;
    axum::serve(listener, app).with_graceful_shutdown(shutdown_signal()).await?;

    Ok(())
}

async fn index_handler(State(state): State<AppState>) -> Html<String> {
    let metrics = state.metrics.get_summary().await;
    templates::render_index(&metrics).unwrap_or_default()
}

async fn dashboard_handler(State(state): State<AppState>) -> Html<String> {
    let metrics = state.metrics.get_full().await;
    let agent_stats = state.agent_state.lock().unwrap().clone();
    templates::render_dashboard(&metrics, &agent_stats).unwrap_or_default()
}

async fn metrics_worker(state: AppState) {
    let mut interval = tokio::time::interval(tokio::time::Duration::from_secs(5));
    loop {
        interval.tick().await;
        state.metrics.update_live().await;
    }
}

async fn sync_agent_stats(state: AppState) {
    let mut interval = tokio::time::interval(tokio::time::Duration::from_secs(2));
    loop {
        interval.tick().await;
        
        // Sync with Qdrant
        if let Ok(user_count) = state.qdrant_client.collection_count("irc_memory").await {
            state.metrics.user_memory_count = user_count as u64;
        }
        
        // Simulate agent activity
        let mut agent_state = state.agent_state.lock().unwrap();
        agent_state.channel_stats.iter_mut().for_each(|(_, stats)| {
            stats.message_count += 1;
            stats.sentiment_score += 0.01;
        });
    }
}

async fn shutdown_signal() {
    let ctrl_c = async {
        signal::ctrl_c()
            .await
            .expect("failed to install Ctrl+C handler");
    };

    #[cfg(unix)]
    let terminate = async {
        signal::unix::signal(signal::unix::SignalKind::terminate())
            .expect("failed to install signal handler")
            .recv()
            .await;
    };

    #[cfg(not(unix))]
    let terminate = std::future::pending::<()>();

    tokio::select! {
        _ = ctrl_c => {},
        _ = terminate => {},
    }

    println!("signal received, starting graceful shutdown");
}
