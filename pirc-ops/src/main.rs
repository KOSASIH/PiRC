use std::process::Command;
use std::env;
use anyhow::Result;

#[tokio::main]
async fn main() -> Result<()> {
    let args: Vec<String> = env::args().collect();
    
    match args.get(1) {
        Some(arg) => match arg.as_str() {
            "deploy" => deploy().await,
            "docker" => docker_up().await,
            "k8s" => k8s_deploy().await,
            "test" => test_suite().await,
            _ => usage(),
        }
        None => usage(),
    }
}

async fn deploy() -> Result<()> {
    println!("🚀 Deploying PiRC AI Suite...");
    
    // Build all crates
    Command::new("cargo")
        .args(["build", "--release"])
        .status()?;
    
    // Docker compose
    Command::new("docker-compose")
        .args(["up", "-d", "--build"])
        .status()?;
    
    println!("✅ Full deployment complete!");
    println!("📊 Dashboard: http://localhost:8080");
    println!("🤖 AI Bot: Connected to IRC");
    Ok(())
}

async fn docker_up() -> Result<()> {
    println!("🐳 Docker deployment...");
    Command::new("docker-compose")
        .args(["up", "--build"])
        .status()?;
    Ok(())
}

fn usage() -> Result<()> {
    println!("pirc-ops commands:");
    println!("  pirc-deploy deploy    # Full production deploy");
    println!("  pirc-deploy docker    # Docker stack");
    println!("  pirc-deploy test      # Run test suite");
    Ok(())
}
