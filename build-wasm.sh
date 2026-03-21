#!/bin/bash
cargo install wasm-bindgen-cli
rustup target add wasm32-unknown-unknown
cargo build --target wasm32-unknown-unknown --release --features wasm
wasm-bindgen target/wasm32-unknown-unknown/release/pirc-ai-agent.wasm \
  --out-dir src/wasm --target web
