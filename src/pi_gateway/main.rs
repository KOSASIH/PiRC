use std::env;
use std::sync::Arc;

use axum::{routing::{get, post}, Router, Json, extract::State};
use clap::Parser;
use pi_network::{PiClient, Wallet};
use serde::{Deserialize, Serialize};
use sqlx::{SqlitePool, Row};
use tokio::sync::Mutex;
use tracing::{info, warn};

mod trading;
use trading::TradingEngine;

#[derive(Parser, Clone)]
struct Args {
    #[arg(long, default_value = "pi1qsuperagent1234567890abcdef")]
    wallet_address: String,
    #[arg(long)]
    private_key: Option<String>,
}

#[derive(Serialize, Clone)]
struct WalletStatus {
    address: String,
    balance_pi: f64,
    balance_usd: f64,
    pending_rewards: f64,
    last_updated: String,
}

#[derive(Deserialize)]
struct TransferRequest {
    to_address: String,
    amount_pi: f64,
    memo: Option<String>,
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::fmt::init();

    let args = Args::parse();
    let pool = SqlitePool::connect("sqlite://data/pi_wallet.db").await?;
    
    // Init DB
    sqlx::query!(
        "CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY,
            tx_hash TEXT NOT NULL,
            amount_pi REAL NOT NULL,
            to_address TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )"
    )
    .execute(&pool).await?;

    let pi_client = PiClient::new();
    let wallet = Wallet::from_address(&args.wallet_address);
    let trading_engine = TradingEngine::new(pool.clone()).await?;
    
    let state = Arc::new(AppState {
        pi_client,
        wallet,
        pool,
        trading_engine,
        wallet_address: args.wallet_address,
    });

    let app = Router::new()
        .route("/health", get(health_handler))
        .route("/wallet", get(wallet_handler))
        .route("/wallet/transfer", post(transfer_handler))
        .route("/trading/start", post(start_trading))
        .route("/trading/status", get(trading_status))
        .with_state(state);

    let listener = tokio::net::TcpListener::bind("0.0.0.0:3000").await?;
    info!("💰 Pi Gateway started on :3000");

    axum::serve(listener, app).await?;
    Ok(())
}

#[derive(Clone)]
struct AppState {
    pi_client: PiClient,
    wallet: Wallet,
    pool: SqlitePool,
    trading_engine: Arc<Mutex<TradingEngine>>,
    wallet_address: String,
}

async fn health_handler() -> &'static str {
    "💰 Pi Gateway Healthy!"
}

async fn wallet_handler(State(state): State<Arc<AppState>>) -> Json<WalletStatus> {
    // Fetch real Pi balance (mocked for demo)
    let balance_pi = 1234.56;
    let balance_usd = balance_pi * 0.15; // $0.15/Pi estimate
    let pending_rewards = 45.67;

    Json(WalletStatus {
        address: state.wallet_address.clone(),
        balance_pi,
        balance_usd,
        pending_rewards,
        last_updated: chrono::Utc::now().to_rfc3339(),
    })
}

async fn transfer_handler(
    State(state): State<Arc<AppState>>,
    Json(req): Json<TransferRequest>,
) -> Result<Json<serde_json::Value>, axum::http::StatusCode> {
    info!("Transfer request: {} Pi to {}", req.amount_pi, req.to_address);

    // Simulate Pi transfer
    let tx_hash = format!("pi_tx_{}", uuid::Uuid::new_v4());

    // Log transaction
    sqlx::query!(
        "INSERT INTO transactions (tx_hash, amount_pi, to_address) VALUES (?, ?, ?)",
        tx_hash, req.amount_pi, req.to_address
    )
    .execute(&state.pool)
    .await
    .map_err(|_| axum::http::StatusCode::INTERNAL_SERVER_ERROR)?;

    Ok(Json(serde_json::json!({
        "success": true,
        "tx_hash": tx_hash,
        "amount": req.amount_pi,
        "to": req.to_address
    })))
}

async fn start_trading(State(state): State<Arc<AppState>>) -> Json<serde_json::Value> {
    let mut engine = state.trading_engine.lock().await;
    engine.start_auto_trading().await;
    
    Json(serde_json::json!({
        "status": "trading_started",
        "strategy": "pi_momentum_v1"
    }))
}

async fn trading_status(State(state): State<Arc<AppState>>) -> Json<serde_json::Value> {
    let engine = state.trading_engine.lock().await;
    Json(serde_json::json!({
        "status": engine.status(),
        "pnl": engine.pnl(),
        "position_size": engine.position_size()
    }))
}
