use tokio::net::TcpStream;
use nom::{IResult, bytes::complete::take_until, combinator::map_res};
use thiserror::Error;

#[derive(Debug)]
pub enum IrcEvent {
    PrivMsg { channel: String, user: String, msg: String },
    Join { channel: String, user: String },
    Pong,
}

pub struct IrcClient {
    stream: TcpStream,
    nick: String,
}

#[derive(Error, Debug)]
pub enum IrcError {
    #[error("Parse error")]
    Parse,
    #[error("IO error")]
    Io,
}

impl IrcClient {
    pub async fn connect(server: &str, nick: &str) -> anyhow::Result<Self> {
        let stream = TcpStream::connect(server).await?;
        let mut client = Self { stream, nick: nick.to_string() };
        
        // Send initial commands
        client.send_raw(&format!("NICK {}", nick)).await?;
        client.send_raw("USER bot 0 * :PiRC Bot").await?;
        
        Ok(client)
    }

    pub async fn send_privmsg(&mut self, channel: &str, msg: &str) -> anyhow::Result<()> {
        self.send_raw(&format!("PRIVMSG {} :{}", channel, msg)).await
    }

    async fn send_raw(&mut self, cmd: &str) -> anyhow::Result<()> {
        use tokio::io::AsyncWriteExt;
        self.stream.writable().await?;
        self.stream.write_all(format!("{}\r\n", cmd).as_bytes()).await?;
        Ok(())
    }

    pub async fn next_event(&mut self) -> anyhow::Result<IrcEvent> {
        use tokio::io::AsyncBufReadExt;
        let mut line = String::new();
        self.stream.read_line(&mut line).await?;
        parse_irc_line(&line.trim())
    }
}

fn parse_irc_line(input: &str) -> anyhow::Result<IrcEvent> {
    // Simplified IRC parser (production uses nom)
    if input.starts_with("PING") {
        Ok(IrcEvent::Pong)
    } else if input.contains("PRIVMSG") {
        let parts: Vec<&str> = input.split_whitespace().collect();
        let channel = parts[2].trim_start_matches('#').to_string();
        let msg_start = input.find(':').unwrap_or(0) + 1;
        let msg = &input[msg_start..].to_string();
        Ok(IrcEvent::PrivMsg { 
            channel, 
            user: "user".to_string(), 
            msg: msg.to_string() 
        })
    } else {
        Ok(IrcEvent::Pong)
    }
}

pub mod prelude {
    pub use super::{IrcClient, IrcEvent};
}
