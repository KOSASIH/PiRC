use pirc_core::prelude::*;
use pirc_ai_agent::AutonomousAgent;
use pirc_edge_ai::EdgeLlm;
use pirc_pi_super::PiWallet;
use tracing_subscriber;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    tracing_subscriber::fmt::init();
    
    println!("🚀 PiRC Complete AI Bot Starting...");
    println!("🤖 Autonomous Agent + Local AI + Pi Wallet");
    
    // Initialize components
    let mut irc = IrcClient::connect("irc.libera.chat:6667", "PiAIBot").await?;
    let llm = EdgeLlm::load("models/phi3-mini.safetensors").await?;
    let wallet = PiWallet::new("pi1qsuperagent");
    
    println!("📡 Connected to IRC! Join #test to chat with AI");
    println!("💰 Wallet: {:.2} PI", wallet.get_balance().await?);
    
    // Main event loop
    while let Some(event) = irc.next_event().await? {
        match event {
            IrcEvent::PrivMsg { channel, user, msg } => {
                println!("💬 {}: {}", user, msg);
                
                if msg.starts_with("!balance") {
                    let balance = wallet.get_balance().await?;
                    irc.send_privmsg(&channel, &format!("💰 Balance: {:.2} PI", balance)).await?;
                } else if msg.starts_with("!ai") {
                    let response = llm.chat(&msg[3..]).await?;
                    irc.send_privmsg(&channel, &response).await?;
                } else {
                    irc.send_privmsg(&channel, "🤖 Powered by PiRC AI! Try !balance or !ai").await?;
                }
            }
            _ => {}
        }
    }
    
    Ok(())
                                            }
