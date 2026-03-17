use crate::{llm::EdgeLLM, memory::VectorMemory, pi_wallet::PiWallet, tools::Tool};
use pirc::client::{IrcClient, IrcEvent};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use tokio::sync::mpsc;
use tracing::{info, warn, error};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentState {
    pub channel_stats: HashMap<String, ChannelStats>,
    pub user_profiles: HashMap<String, UserProfile>,
    pub trading_balance: f64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChannelStats {
    pub message_count: u64,
    pub sentiment_score: f32,
    pub active_users: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UserProfile {
    pub reputation: f32,
    pub pi_balance: Option<f64>,
    pub is_whale: bool,
}

pub struct AutonomousAgent {
    irc: IrcClient,
    llm: EdgeLLM,
    memory: VectorMemory,
    wallet: PiWallet,
    state: AgentState,
    tool_rx: mpsc::Receiver<Tool>,
    tool_tx: mpsc::Sender<Tool>,
}

impl AutonomousAgent {
    pub async fn new(
        irc_server: &str,
        nick: &str,
        llm_path: &str,
    ) -> anyhow::Result<Self> {
        let irc = IrcClient::connect(irc_server, nick).await?;
        let llm = EdgeLLM::load(llm_path).await?;
        let memory = VectorMemory::new_local().await?;
        let wallet = PiWallet::new().await?;
        
        let (tool_tx, tool_rx) = mpsc::channel(100);
        
        Ok(Self {
            irc,
            llm,
            memory,
            wallet,
            state: AgentState {
                channel_stats: HashMap::new(),
                user_profiles: HashMap::new(),
                trading_balance: 0.0,
            },
            tool_tx,
            tool_rx,
        })
    }

    pub async fn run_autonomous(&mut self) -> anyhow::Result<()> {
        info!("🤖 Autonomous AI Agent starting...");
        
        // Spawn tool workers
        tokio::spawn(self.clone().tool_worker());
        tokio::spawn(self.clone().trading_worker());
        
        while let Some(event) = self.irc.next_event().await {
            self.process_event(event).await?;
        }
        
        Ok(())
    }

    async fn process_event(&mut self, event: IrcEvent) -> anyhow::Result<()> {
        match event {
            IrcEvent::PrivMsg { channel, user, msg } => {
                info!("💬 {} in {}: {}", user, channel, msg);
                
                // Update stats
                self.update_channel_stats(&channel, &user).await;
                
                // AI Decision making
                let decision = self.llm.make_decision(&channel, &user, &msg).await?;
                
                match decision.action.as_str() {
                    "respond" => {
                        let response = self.llm.generate_response(&channel, &user, &msg).await?;
                        self.irc.send_privmsg(&channel, &response).await?;
                    }
                    "moderate" => self.execute_moderation(&channel, &user).await?,
                    "trade" => {
                        let trade_signal = decision.trade_signal.unwrap();
                        self.tool_tx.send(Tool::ExecuteTrade(trade_signal)).await?;
                    }
                    "wallet_query" => {
                        let balance = self.wallet.get_balance().await?;
                        self.irc.send_privmsg(&channel, &format!("💰 My Pi balance: {:.4}", balance)).await?;
                    }
                    _ => {}
                }
            }
            IrcEvent::Join { channel, user } => {
                self.irc.send_privmsg(&channel, &format!("👋 Welcome {}! I'm your AI assistant powered by PiRC!", user)).await?;
            }
            _ => {}
        }
        
        Ok(())
    }

    async fn update_channel_stats(&mut self, channel: &str, user: &str) {
        // Vector memory update
        let embedding = self.llm.embed_text(user).await.unwrap();
        self.memory.store_vector(user, embedding).await.unwrap();
        
        // Update state
        self.state.channel_stats
            .entry(channel.to_string())
            .or_insert(ChannelStats {
                message_count: 0,
                sentiment_score: 0.0,
                active_users: 0,
            })
            .message_count += 1;
    }

    async fn tool_worker(mut self) {
        while let Some(tool) = self.tool_rx.recv().await {
            match tool {
                Tool::ExecuteTrade(signal) => {
                    info!("💹 Executing trade: {:?}", signal);
                    // self.wallet.execute_trade(signal).await.unwrap();
                }
                Tool::ModerateUser { channel, user } => {
                    self.irc.send_cmd(&format!("KICK {} {}", channel, user)).await.unwrap();
                }
            }
        }
    }

    async fn trading_worker(mut self) {
        loop {
            // Analyze sentiment across all channels
            let global_sentiment = self.llm.analyze_global_sentiment().await.unwrap();
            
            if global_sentiment > 0.7 {
                info!("📈 Bullish sentiment detected! Preparing buy signal...");
                // Trigger buy
            }
            
            tokio::time::sleep(tokio::time::Duration::from_secs(30)).await;
        }
    }
}
