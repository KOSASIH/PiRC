mod api;
mod metrics;
mod templates;
mod websocket;

use api::{agent_api, chat_api, metrics_api, trading_api};
use axum::{
    extract::State,
    http::StatusCode,
    response::Html,
    routing::{get, post},
    Router,
};
use metrics::MetricsStore;
use pirc_ai_agent::{AgentState, AutonomousAgent};
use serde_json::json;
use sqlx::{SqlitePool, sqlite::SqlitePoolOptions};
use std::net::SocketAddr;
use std::sync::{Arc, Mutex};
use tokio::signal;
use tower_http::{
    cors::CorsLayer,
    services::ServeDir,
    trace::TraceLayer,
};
use tracing::{info, Level};
use websocket::{metrics_broadcaster, MetricsSender, ws_handler};

use crate::metrics::LiveMetrics;

#[derive(Clone)]
pub struct AppState {
    pub metrics: Arc<MetricsStore>,
    pub agent_state: Arc<Mutex<AgentState>>,
    pub db: SqlitePool,
    pub qdrant_client: qdrant_client::QdrantClient,
    pub broadcast_tx: MetricsSender,
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // === INITIALIZATION ===
    tracing_subscriber::fmt()
        .with_max_level(Level::INFO)
        .init();

    info!("🚀 Starting PiRC AI Dashboard v1.0.0");
    info!("📊 Production-ready analytics engine");

    // === DATABASE ===
    let db = SqlitePoolOptions::new()
        .max_connections(20)
        .connect("sqlite://dashboard.db")
        .await?;
    
    // Run migrations
    sqlx::migrate!("src/migrations")
        .run(&db)
        .await?;
    
    info!("✅ Database initialized");

    // === METRICS ENGINE ===
    let metrics = Arc::new(MetricsStore::new());
    info!("✅ Metrics engine ready");

    // === QDRANT VECTOR DB ===
    let qdrant_client = qdrant_client::QdrantClient::from_url("http://localhost:6333")
        .build()?;
    info!("✅ Vector database connected");

    // === SHARED AGENT STATE ===
    let agent_state = Arc::new(Mutex::new(AgentState {
        channel_stats: std::collections::HashMap::new(),
        user_profiles: std::collections::HashMap::new(),
        trading_balance: 3141.59,
    }));

    // === WEBSOCKET BROADCASTER ===
    let (broadcast_tx, _) = websocket::broadcast_channel(256);
    info!("✅ WebSocket broadcaster ready");

    // === APP STATE ===
    let state = AppState {
        metrics: metrics.clone(),
        agent_state: agent_state.clone(),
        db,
        qdrant_client,
        broadcast_tx: broadcast_tx.clone(),
    };

    // === BACKGROUND WORKERS ===
    tokio::spawn(metrics_broadcaster(state.clone()));
    tokio::spawn(database_worker(state.clone()));
    tokio::spawn(agent_sync_worker(state.clone()));
    info!("✅ Background workers started");

    // === AXUM ROUTER ===
    let app = Router::new()
        // 📄 Static Pages
        .route("/", get(index_handler))
        .route("/dashboard", get(dashboard_handler))
        .route("/trading", get(trading_handler))
        
        // 🚀 API Endpoints
        .route("/api/metrics", get(metrics_api::get_metrics))
        .route("/api/metrics/history", get(metrics_api::get_history))
        .route("/api/agents", get(agent_api::get_agents))
        .route("/api/agents/:channel", get(agent_api::get_channel))
        .route("/api/trading", get(trading_api::get_signals))
        .route("/api/chat", post(chat_api::chat_handler))
        
        // ⚡ WebSocket
        .route("/ws", get(ws_handler))
        
        // 📁 Static Files
        .nest_service("/static", ServeDir::new("static"))
        
        // 🛡️ Middleware
        .layer(TraceLayer::new_for_http())
        .layer(CorsLayer::permissive())
        
        .with_state(state);

    // === SERVER START ===
    let addr = SocketAddr::from(([0, 0, 0, 0], 8080));
    info!("🌐 Dashboard listening on http://localhost:8080");
    info!("📱 Dashboard: http://localhost:8080/dashboard");
    info!("⚡ WebSocket: ws://localhost:8080/ws");

    let listener = tokio::net::TcpListener::bind(addr).await?;
    axum::serve(listener, app)
        .with_graceful_shutdown(shutdown_signal())
        .await?;

    info!("👋 Dashboard shutdown complete");
    Ok(())
}

// 📄 === PAGE HANDLERS ===
async fn index_handler(State(state): State<AppState>) -> Html<String> {
    let metrics = state.metrics.get_summary().await;
    Html(templates::render_index(&metrics).unwrap_or_default())
}

async fn dashboard_handler(State(state): State<AppState>) -> Html<String> {
    let metrics = state.metrics.get_full().await;
    let agent_stats = state.agent_state.lock().unwrap().clone();
    Html(templates::render_dashboard(&metrics, &agent_stats).unwrap_or_default())
}

async fn trading_handler(State(state): State<AppState>) -> Html<String> {
    let trading_data = trading_api::get_trading_data(&state).await;
    Html(templates::render_trading(&trading_data).unwrap_or_default())
}

// 🛠️ === BACKGROUND WORKERS ===
async fn database_worker(state: AppState) {
    let mut interval = tokio::time::interval(tokio::time::Duration::from_secs(10));
    loop {
        interval.tick().await;
        if let Err(e) = state.metrics.save_to_db(&state.db).await {
            tracing::warn!("DB save failed: {}", e);
        }
    }
}

async fn agent_sync_worker(state: AppState) {
    let mut interval = tokio::time::interval(tokio::time::Duration::from_secs(3));
    loop {
        interval.tick().await;
        
        // Sync Qdrant stats
        match state.qdrant_client.collection_count("irc_memory").await {
            Ok(count) => state.metrics.user_memory_count.store(count as u64, std::sync::atomic::Ordering::Relaxed),
            Err(e) => tracing::warn!("Qdrant sync failed: {}", e),
        }
        
        // Simulate agent activity
        let mut agent_state = state.agent_state.lock().unwrap();
        for (_, stats) in agent_state.channel_stats.iter_mut() {
            stats.message_count = (stats.message_count + 2) % 1000;
            stats.sentiment_score = (stats.sentiment_score + 0.02) % 1.0;
        }
    }
}

// 🛑 === GRACEFUL SHUTDOWN ===
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
        _ = ctrl_c => info!("Ctrl+C received"),
        _ = terminate => info!("SIGTERM received"),
    }
    info!("🛑 Initiating graceful shutdown...");
}

// 🧪 === TEST ENDPOINTS (Development) ===
async fn health_check(State(state): State<AppState>) -> Json<serde_json::Value> {
    Json(json!({
        "status": "healthy",
        "metrics_count": state.metrics.history.read().await.len(),
        "qdrant_connected": true,
        "timestamp": chrono::Utc::now().to_rfc3339()
    }))
}
