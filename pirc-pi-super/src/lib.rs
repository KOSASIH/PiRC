use reqwest::Client;
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct PiWallet {
    pub address: String,
    pub balance: f64,
    client: Client,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct PiTransaction {
    pub hash: String,
    pub amount: f64,
    pub to: String,
}

impl PiWallet {
    pub fn new(address: &str) -> Self {
        Self {
            address: address.to_string(),
            balance: 3141.59,
            client: Client::new(),
        }
    }

    pub async fn get_balance(&self) -> anyhow::Result<f64> {
        // Mock Pi Network API
        Ok(self.balance + rand::random::<f64>() * 10.0)
    }

    pub async fn send_pi(&self, to: &str, amount: f64) -> anyhow::Result<PiTransaction> {
        println!("💸 Sending {} PI to {}", amount, to);
        Ok(PiTransaction {
            hash: hex::encode(rand::random::<[u8; 32]>()),
            amount,
            to: to.to_string(),
        })
    }

    pub async fn get_price(&self) -> anyhow::Result<f64> {
        // Mock Pi/USD price
        Ok(0.045 + (rand::random::<f64>() * 0.01))
    }
}
