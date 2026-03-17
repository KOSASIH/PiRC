use qdrant_client::{QdrantClient, prelude::*};
use tokio::sync::RwLock;
use std::sync::Arc;

pub struct VectorMemory {
    client: Arc<RwLock<QdrantClient>>,
}

impl VectorMemory {
    pub async fn new_local() -> anyhow::Result<Self> {
        let client = QdrantClient::from_url("http://localhost:6333").build()?;
        
        // Create collection
        client
            .create_collection(&CreateCollection {
                collection_name: "irc_memory".into(),
                vectors_config: Some( VectorsConfig::PlainConfig(PlainVectorsConfig {
                    size: 384,  // Sentence-transformer dim
                })),
                ..Default::default()
            })
            .await?;
            
        Ok(Self {
            client: Arc::new(RwLock::new(client)),
        })
    }

    pub async fn store_vector(&self, id: &str, embedding: Vec<f32>) -> anyhow::Result<()> {
        let client = self.client.read().await;
        client
            .upsert_points("irc_memory", None, points![
                PointStruct::new(
                    id.to_string(),
                    Payload::new(json!({
                        "type": "user",
                        "timestamp": chrono::Utc::now().to_rfc3339()
                    })),
                    vec![embedding.into()],
                )
            ])
            .await?;
        Ok(())
    }

    pub async fn search_similar(&self, query: &str, limit: usize) -> anyhow::Result<Vec<String>> {
        // Embed query + search (use sentence-transformers in prod)
        let client = self.client.read().await;
        let results = client
            .search_points(&SearchPoints {
                collection_name: "irc_memory".into(),
                vector: vec![vec![0.1f32; 384]],  // Mock embedding
                limit: limit as u64,
                ..Default::default()
            })
            .await?;
            
        Ok(results.into_iter().map(|p| p.payload.get("id").unwrap().as_str().unwrap().to_string()).collect())
    }
}
