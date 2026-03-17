use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Tool {
    ExecuteTrade(crate::llm::TradeSignal),
    ModerateUser { channel: String, user: String },
    QueryPiStats,
    GenerateMeme,
}

impl std::fmt::Display for Tool {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Tool::ExecuteTrade(_) => write!(f, "💹 Execute Trade"),
            Tool::ModerateUser { channel, user } => write!(f, "🚫 Moderate {} in {}", user, channel),
            _ => write!(f, "⚙️ Tool"),
        }
    }
}
