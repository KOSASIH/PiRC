use pirc_ai_agent::AutonomousAgent;
use tracing_subscriber;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::fmt::init();
    
    println!("🚀 Starting PiRC AI Autonomous Agent...");
    println!("📡 Connect to testnet.irc or your Pi Network IRC");
    
    let mut agent = AutonomousAgent::new(
        "irc.libera.chat:6667",  // Replace with Pi IRC
        "PiAIBot",
        "./models/phi3-mini.onnx",  // Download model
    ).await?;
    
    agent.run_autonomous().await?;
    
    Ok(())
}
