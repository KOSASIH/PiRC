// api/trade-pi.js - Serverless Pi Trading
export const config = { runtime: 'edge' };

export default async function handler(req) {
  const { strategy, amount } = await req.json();
  
  // Call PiRC gRPC
  const grpcResponse = await fetch('https://pirc.yourdomain.com:50051', {
    method: 'POST',
    headers: { 'content-type': 'application/grpc-web+proto' },
    body: encodeTradeRequest(strategy, amount)
  });
  
  const trade = await grpcResponse.json();
  
  return Response.json({
    success: trade.success,
    txHash: trade.tx_hash,
    pnl: trade.pnl,
    executedAt: new Date().toISOString()
  });
}
