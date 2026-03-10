# PiRC-101 Sovereign Monetary Standard

## Overview
PiRC-101 is a proposed decentralized monetary standard designed for the Pi Network ecosystem. It enables a robust, non-inflationary 10,000,000:1 internal credit expansion, allowing Pi to be utilized as the backing asset for a stable internal sovereign credit. It features dynamic liquidity guardrails ($\Phi$) to maintain insolvency protection under heterogeneous participant behavior.

## Core Thesis
The protocol separates Pi's external value volatility from its internal utility.

## 🛠️ Execution Environment & Architectural Note
**Important:** Pi Network consensus is based on the Stellar Consensus Protocol (SCP) and does not natively execute Ethereum Virtual Machine (EVM) bytecode.

The Solidity contract in this repository (`PiRC101Vault.sol`) serves strictly as a **Turing-complete Economic Reference Model**. It defines the deterministic state transitions and mathematical invariants of the "Justice Engine." It is not intended for native Pi L1 deployment in its current form. Production deployment would require either (1) an EVM-compatible sidechain (L2) anchored to Pi, or (2) a port of this logic to Soroban (Rust).

## 🚀 Repository Content
- `/contracts`: Normative solidity reference model.
- `/simulator`: Stochastic Agent-Based Model (ABM) and HTML interactive visualizer.
- `/docs`: Whitepaper specification and developer guides.

## License
MIT

