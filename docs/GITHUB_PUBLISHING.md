# GitHub Publishing Guide

## Suggested Repository Settings

- Repository name: `matagent-lab`
- Description: `Agentic AI pipeline for materials and chemistry discovery with RAG, screening, synthesis critique, benchmarks, and HPC job templates.`
- Visibility: public, unless you prefer to keep it private during job applications.
- Topics: `agentic-ai`, `materials-discovery`, `chemistry`, `rag`, `hpc`, `multi-agent-systems`, `computational-materials`, `llm-agents`

## Suggested GitHub About Text

Agentic AI pipeline for materials and chemistry discovery. Demonstrates literature RAG, multi-agent candidate generation, chemistry-aware screening, synthesis viability scoring, benchmarks, and Slurm templates for DFT/MD/Monte Carlo validation.

## Publish Commands

After creating an empty GitHub repository, connect and push this local repo:

```bash
git remote add origin git@github.com:ShuangLin212/matagent-lab.git
git push -u origin main
```

For HTTPS:

```bash
git remote add origin https://github.com/ShuangLin212/matagent-lab.git
git push -u origin main
```

## README Opening Pitch

MatAgent Lab demonstrates how agentic AI can compress early materials discovery by coordinating literature retrieval, candidate generation, computational screening, synthesis-aware critique, and HPC job preparation in one auditable loop. The demo focuses on two hardware-relevant domains: transparent, lightweight materials for AR glasses and sensing or actuating materials for robotics.

## Interview Summary

This project is a systems prototype for autonomous materials discovery. It uses a local multi-agent pipeline to retrieve scientific evidence, generate candidates, estimate material properties, assess synthesis risk, rank candidates, benchmark throughput, and prepare HPC jobs. The implementation is deterministic and dependency-light so it runs in CI, but the module boundaries are designed for real LLM agents, DFT, molecular dynamics, Monte Carlo, active learning, and lab automation.

