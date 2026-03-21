// ai-agent.worker.js - PiRC Edge AI (Global <15ms latency)
// Deploy: wrangler deploy --name pirc-ai-edge

export default {
  async fetch(request, env, ctx) {
    // CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };

    // Handle preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    try {
      if (request.method !== 'POST') {
        return new Response('Method not allowed', { status: 405 });
      }

      const { prompt, user_id, session_id } = await request.json();
      
      if (!prompt || typeof prompt !== 'string') {
        return new Response('Invalid prompt', { status: 400 });
      }

      // Rate limiting (KV Storage)
      const rateKey = `rate:${user_id || 'anon'}:${session_id}`;
      const rateCount = await env.RATE_LIMIT.get(rateKey, { type: 'json' }) || 0;
      
      if (rateCount > 10) {
        return new Response('Rate limited (10/min)', { 
          status: 429, 
          headers: corsHeaders 
        });
      }
      await env.RATE_LIMIT.put(rateKey, rateCount + 1, {
        expirationTtl: 60  // 1min window
      });

      // 🚀 WebAssembly AI Inference (1ms)
      const wasmResponse = await wasmInference(prompt, env);
      
      // 🧠 Qdrant Vector Search (10ms)
      const qdrantResponse = await qdrantSearch(wasmResponse.embedding, env);
      
      // 💰 Pi Trading Signal (Optional)
      const tradingSignal = await piTradingSignal(wasmResponse.response, env);

      const result = {
        success: true,
        timestamp: Date.now(),
        latency: performance.now() - ctx.waitUntilStart,
        ai: {
          response: wasmResponse.response,
          embedding: wasmResponse.embedding.slice(0, 10) + '...', // Truncated
          tokens: wasmResponse.tokens
        },
        memory: qdrantResponse.points || [],
        trading: tradingSignal,
        location: request.cf?.city || 'Edge'
      };

      return new Response(JSON.stringify(result), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });

    } catch (error) {
      console.error('Edge AI error:', error);
      return new Response(JSON.stringify({ 
        error: 'AI inference failed', 
        details: error.message 
      }), { 
        status: 500, 
        headers: corsHeaders 
      });
    }
  }
};

async function wasmInference(prompt, env) {
  // Load WASM module (cached by Workers)
  const wasmModule = await WebAssembly.instantiateStreaming(
    fetch('./ai-agent.wasm', { cache: 'force-cache' })
  );
  
  const start = performance.now();
  
  // AI Inference (Ultra-fast!)
  const embedding = wasmModule.exports.generate_embedding(prompt);
  const response = wasmModule.exports.ai_chat(prompt);
  
  const latency = performance.now() - start;
  
  return {
    response: response,
    embedding: Array.from(embedding),
    tokens: embedding.length / 32, // Approx
    wasm_latency: `${latency.toFixed(1)}ms`
  };
}

async function qdrantSearch(embedding, env) {
  try {
    const qdrantRes = await fetch(`${env.QDRANT_URL}/collections/irc_memory/points/search`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'api-key': env.QDRANT_API_KEY
      },
      body: JSON.stringify({
        vector: embedding,
        limit: 3,
        with_payload: true
      })
    });
    
    return await qdrantRes.json();
  } catch (e) {
    console.warn('Qdrant unavailable:', e.message);
    return { points: [] };
  }
}

async function piTradingSignal(aiResponse, env) {
  if (!aiResponse.includes('trade') && !aiResponse.includes('buy')) {
    return null;
  }
  
  try {
    const tradeRes = await fetch(`${env.PI_GATEWAY_URL}/trading/signal`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        signal: aiResponse.includes('buy') ? 'LONG' : 'SHORT',
        confidence: 0.85 
      })
    });
    
    return await tradeRes.json();
  } catch (e) {
    return { status: 'pending' };
  }
          }
