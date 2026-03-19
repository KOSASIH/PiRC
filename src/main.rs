use std::collections::HashMap;
use std::env;
use std::sync::Arc;

use axum::{routing::get, Router, Server};
use clap::Parser;
use futures::StreamExt;
use prometheus::{Encoder, TextEncoder};
use qdrant_client::qdrant::{PointStruct, VectorParams, VectorsConfig};
use redis::AsyncCommands;
use tokio::sync::Mutex;
use tokio_tungstenite::{connect_async, tungstenite::protocol::Message};
use tracing::{info, warn, error};

mod metrics;
use metrics::*;

#[derive(Parser, Clone)]
struct Args {
    #[arg(long, default_value = "irc.libera.chat:6667")]
    irc_server: String,
    #[arg(long, default_value = "PiAIBot")]
    irc_nick: String,
    #[arg(long, default_value = "#pirc-ai")]
    irc_channels: String,
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Initialize tracing
    tracing_subscriber::fmt()
        .with_env_filter(tracing::Level::INFO)
        .init();

    let args = Args::parse();
    let state = Arc::new(AppState::new(args).await?);

    // Start metrics server
    let metrics_router = Router::new()
        .route("/metrics", get(metrics_handler))
        .route("/health", get(health_handler));

    let server = axum::Server::bind(&"0.0.0.0:8081".parse()?)
        .serve(metrics_router.into_make_service())
        .with_graceful_shutdown(shutdown_signal());

    // Start IRC client
    let irc_task = tokio::spawn(irc_client(state.clone()));

    info!("🚀 PiRC AI Agent v2.0 started on :8081");
    tokio::select! {
        result = server => result?,
        result = irc_task => result??,
    }

    Ok(())
}

#[derive(Clone)]
struct AppState {
    redis: redis::Client,
    qdrant: qdrant_client::QdrantClient,
    irc_clients: Arc<Mutex<HashMap<String, tokio_tungstenite::WebSocketStream<tokio_tungstenite::MaybeTlsStream<tokio::net::TcpStream>>>>>,
    args: Args,
}

impl AppState {
    async fn new(args: Args) -> anyhow::Result<Self> {
        let redis_url = env::var("REDIS_URL").unwrap_or_else(|_| "redis://localhost:6379/1".to_string());
        let qdrant_url = env::var("QDRANT_URL").unwrap_or_else(|_| "http://localhost:6333".to_string());

        let redis = redis::Client::open(redis_url)?;
        let qdrant = qdrant_client::QdrantClient::from_url(&qdrant_url).build()?;

        // Create Qdrant collection
        qdrant
            .create_collection(
                "irc_memory",
                None,
                None,
                VectorsConfig::Vector(VectorsConfigVector {
                    size: 768,
                    distance: qdrant_client::qdrant::Distance::Cosine,
                    multivector_config: None,
                    config: Some(Box::new(VectorParams {
                        on_disk: Some(true),
                    })),
                }),
            )
            .await?;

        Ok(Self {
            redis: redis,
            qdrant,
            irc_clients: Arc::new(Mutex::new(HashMap::new())),
            args,
        })
    }
}

async fn irc_client(state: Arc<AppState>) {
    let url = format!("irc://{}", state.args.irc_server);
    
    loop {
        match connect_async(&url).await {
            Ok((ws_stream, _)) => {
                info!("Connected to IRC: {}", state.args.irc_server);
                process_irc(ws_stream, state.clone()).await;
            }
            Err(e) => {
                error!("IRC connection failed: {}", e);
                tokio::time::sleep(tokio::time::Duration::from_secs(5)).await;
            }
        }
    }
}

async fn process_irc(mut ws: tokio_tungstenite::WebSocketStream<tokio_tungstenite::MaybeTlsStream<tokio::net::TcpStream>>, state: Arc<AppState>) {
    // IRC Handshake
    ws.send(Message::Text("NICK PiAIBot\r\n".to_string())).await.ok();
    ws.send(Message::Text("USER PiAI 8 * :PiRC AI Agent\r\n".to_string())).await.ok();
    ws.send(Message::Text("JOIN #pirc-ai\r\n".to_string())).await.ok();

    while let Some(msg) = ws.next().await {
        match msg {
            Ok(Message::Text(text)) => {
                if text.contains("PRIVMSG") {
                    if let Some(response) = analyze_message(&text, &state).await {
                        ws.send(Message::Text(format!("PRIVMSG #pirc-ai :{}\r\n", response))).await.ok();
                    }
                }
            }
            Err(e) => {
                warn!("IRC message error: {}", e);
                break;
            }
            _ => {}
        }
    }
}

async fn analyze_message(text: &str, state: &Arc<AppState>) -> Option<String> {
    // Simple AI analysis - store in Qdrant + generate response
    let user = extract_user(text);
    let content = extract_content(text);

    // Store memory
    let embedding = get_embedding(&content).await; // Mock LLM embedding
    let point = PointStruct::new(
        uuid::Uuid::new_v4().to_string(),
        vec![embedding],
        HashMap::new(),
    );
    
    if let Err(e) = state.qdrant.upsert_points("irc_memory", None, vec![point], None).await {
        error!("Qdrant upsert failed: {}", e);
    }

    // Rate limit check
    let mut conn = state.redis.get_async_connection().await.ok()?;
    let key = format!("rate:{}", user);
    let count: i64 = redis::cmd("INCR").arg(&key).query_async(&mut conn).await.unwrap_or(0);
    if count == 1 {
        redis::cmd("EXPIRE").arg(&key).arg(60).query_async(&mut conn).await.ok();
    }
    if count > 5 {
        return Some(format!("@{user} Rate limited. Try again in 60s."));
    }

    // AI Response logic
    Some(format!("@{user} 🤖 AI analyzed: '{}'. Stored in vector memory!", content))
}

async fn get_embedding(_text: &str) -> Vec<f32> {
    // Mock OpenAI embedding - replace with real LLM
    vec![0.1; 768]
}

fn extract_user(text: &str) -> String {
    text.split_whitespace()
        .nth(2)
        .unwrap_or("unknown")
        .trim_start_matches(':')
        .split('!').next()
        .unwrap_or("unknown")
        .to_string()
}

fn extract_content(text: &str) -> String {
    text.split(':').nth(2).unwrap_or("").trim().to_string()
}

async fn metrics_handler() -> String {
    let encoder = TextEncoder::new();
    let metric_families = prometheus::gather();
    encoder.encode_to_string(&metric_families).unwrap()
}

async fn health_handler() -> &'static str {
    "OK"
}

async fn shutdown_signal() {
    tokio::signal::ctrl_c().await.ok();
}
