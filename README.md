# Multi-Agent RAG Platform

LangGraph-based platform with 4 business configs: real estate, law, logistics, medicine.

## Features
- 10 agents: Guard (DLP), Ingestor, Indexer, Retriever, Extractor, Summarizer, Answerer, Reviewer, Orchestrator, Watchdog
- Config-driven: add new business domain in 1 day
- Graceful degradation: LLM fallback → manual review
- Cost control: token tracking per query
- Self-hosted: no data leaves your infrastructure

## Quick Start
```bash
pip install langgraph langchain-core fastembed chromadb httpx pyyaml
export GROQ_API_KEY="your_key"
python run_demo.py

## Architecture
Engine: LangGraph (state graph)
Embeddings: fastembed (onnxruntime, no torch)
LLM: Groq API (GPT-OSS 20B / 120B)
Vector DB: ChromaDB (ephemeral for demo)

## Status
✅ Working demo with real estate config
🚧 Law/logistics/medicine configs ready