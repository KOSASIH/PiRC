// Add to main.rs imports:
mod llm;
use llm::LLMEngine;

// Update analyze_message function:
async fn analyze_message(text: &str, state: &Arc<AppState>) -> Option<String> {
    let user = extract_user(text);
    let content = extract_content(text);

    // LLM Analysis 🚀
    let llm = LLMEngine::new("gsk_your_groq_key".to_string()).await.unwrap();
    let context = format!("IRC user: {}, previous context: ...", user);
    
    match llm.chat(&content, Some(&context)).await {
        Ok(ai_response) => {
            // Store in Qdrant
            let embedding = get_embedding(&content).await;
            // ... Qdrant upsert ...
            
            Some(format!("PRIVMSG #pirc-ai :🤖 {}\r\n", ai_response))
        }
        Err(e) => {
            warn!("LLM error: {}", e);
            Some(format!("PRIVMSG #pirc-ai :🤖 Interesting! Processing...\r\n"))
        }
    }
}
