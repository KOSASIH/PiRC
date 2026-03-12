See [PiRC1: Pi Ecosystem Token Design](./PiRC1/ReadMe.md)


# PiRC Research Extensions

This repository contains experimental proposals and research
extensions for the Pi Requests for Comment (PiRC) framework.

## Research Proposals

- PiRC-101 — Adaptive Utility Allocation
- PiRC-102 — Engagement Oracle Protocol

These proposals explore mechanisms for improving reward allocation,
engagement measurement, and protocol security in the Pi ecosystem.

## Goals

• deterministic reward allocation  
• engagement verification  
• sybil-resistant participation metrics  
• protocol-level incentive modeling


## PiRC Proposals

- PiRC-101: Adaptive Utility Allocation
- PiRC-102: Engagement Oracle Protocol


# PiRC Economic Architecture

Research and simulation framework for the PiRC reward coordination system.

This repository explores the economic structure behind PiRC including liquidity incentives, reward distribution models, and long-term ecosystem stability.

---

# Overview

PiRC introduces a liquidity-aware reward system connecting:

• Pioneer mining supply  
• External liquidity providers  
• Utility-driven transactions  
• Fee generation  

These components create a reflexive economic loop designed to stabilize the Pi ecosystem.

---

# Architecture

Pioneer Supply  
↓  
Liquidity Contribution Engine  
↓  
Economic Activity  
↓  
Fee Generation  
↓  
Reward Distribution  

---

# Repository Structure

contracts/  
Prototype contracts modeling reward and liquidity logic.

economics/  
Mathematical models of the PiRC economic system.

simulations/  
Agent-based simulations of ecosystem behavior.

docs/  
Protocol architecture and system design.

automation/  
Automated simulation runs using GitHub Actions.

---

# Research Goals

• Simulate liquidity growth  
• Analyze reward fairness  
• Test economic stability  
• Evaluate governance parameter bounds

---

# License

MIT License

## PiRC Architecture Overview

PiRC (Pi Requests for Comment) menggabungkan ekosistem token, treasury, governance, DEX executor, reward engine, dan liquidity controller dalam satu loop ekonomi terintegrasi.

### Diagram Arsitektur
![PiRC Architecture](diagrams/a_flowchart_diagram_illustrates_the_pirc_ecosystem.png)

> Diagram di atas menggambarkan alur interaksi antara:
> - **PiRC Token** (mint-on-demand)
> - **Treasury Vault**
> - **Governance Contract**
> - **Liquidity Controller**
> - **DEX Executor** (Free-Fault DEX)
> - **Reward Engine**
> - **Bootstrapper & GitHub Actions**
>
> Setiap modul berkontribusi pada loop ekonomi yang reflexive dan sybil-resistant.

### Dokumen Pendukung
Untuk penjelasan lebih lengkap mengenai tiap modul dan interaksi kontrak, lihat dokumen arsitektur:
[PiRC Architecture Overview](diagrams/pirc_architecture_overview.md)

---

**Catatan:**
- Simpan **gambar diagram** di folder `diagrams/` pada repo.
- Simpan **dokumen arsitektur** (`.md`) di folder yang sama supaya link internal tetap valid.
- Update diagram dan dokumen seiring perubahan kontrak atau alur ekonomi.
