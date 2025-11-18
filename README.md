<div align="center">

<img src="./PAKTON Framework/Frontend/v0.2/static/PAKTON_logo.png" alt="PAKTON Logo" width="300" style="margin: 20px 0;">

# PAKTON: A Multi-Agent Framework for Question Answering in Long Legal Agreements

**[Petros Raptopoulos](https://petrosraptopoulos.com/), Giorgos Filandrianos, Maria Lymperaiou, Giorgos Stamou**

**Making Contract Review Accessible to Everyone Through AI**

[![Paper](https://img.shields.io/badge/arXiv-2506.00608-b31b1b.svg)](https://arxiv.org/abs/2506.00608) [![Demo](https://img.shields.io/badge/Demo-pakton.site-blue.svg)](https://pakton.site) [![License](https://img.shields.io/badge/License-Apache_v2.0-green.svg)](./LICENSE)

[![Venue](https://img.shields.io/badge/Venue-Accepted%20and%20Presented%20Orally%20at%20the%20Main%20Conference%20of%20EMNLP%202025-red.svg)](https://aclanthology.org/2025.emnlp-main.403/)

[**Try PAKTON**](https://pakton.site) | [**View Evaluation and Experiments**](https://pakton.site/evaluation/) | [**Read Paper**](https://aclanthology.org/2025.emnlp-main.403/) | [**View Poster**](./Docs/EMNLP%202025_Poster.pdf) | [**View Recording**](https://drive.google.com/file/d/1xiVGc8zVxImFo4aX-bTOh1BcEN7pdFm5/view) | [**Underline**](https://underline.io/lecture/130155-pakton-a-multi-agent-framework-for-question-answering-in-long-legal-agreements)

</div>

---

## 🎯 About PAKTON

Reviewing contracts is often slow, complex, and requires expert legal knowledge. Legal language can be vague and open to interpretation, making it hard for non-experts to understand. On top of that, contracts are usually private, which limits the use of proprietary AI tools and calls for open-source solutions.

**PAKTON** solves these problems with an open-source, end-to-end framework for automated contract review. It uses a team of LLM agents working together, along with smart retrieval tools (RAG), to make legal document analysis easier, more private, and customizable.

<div align="center">

<img src="./PAKTON Framework/Frontend/v0.2/static/PAKTON_overview.png" alt="PAKTON Overview" style="border-radius: 12px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12); border: 1px solid rgba(0, 0, 0, 0.08); margin: 20px 0; max-width: 50%; height: auto;">

*PAKTON user flow: legal query submission followed by comprehensive report generation*

</div>

## 🚀 Live Demo

**Current Deployment**: [pakton.site](https://pakton.site)

> **⚠️ Important Note**: The current deployed version is customized for the EU AI Act document and was created during a hackathon. It does not include all PAKTON capabilities. Questions are forwarded directly to the "Interrogator" agent (not the Archivist), so please provide well-defined questions without chitchat.

<div align="center">

<img src="./PAKTON Framework/Frontend/v0.2/static/PAKTON_UI_0.png" alt="PAKTON UI - Current Interface" style="border-radius: 12px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12); border: 1px solid rgba(0, 0, 0, 0.08); margin: 10px 0; max-width: 100%; height: auto;">

*Current PAKTON frontend with limited capabilities*

</div>

## ⏭️ Coming Soon: Full PAKTON Frontend

The complete PAKTON experience with full multi-agent capabilities is coming soon:

<div align="center">

<img src="./PAKTON Framework/Frontend/v0.2/static/PAKTON_UI_1.png" alt="PAKTON UI - Main Interface" style="border-radius: 12px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12); border: 1px solid rgba(0, 0, 0, 0.08); margin: 10px 0; max-width: 100%; height: auto;">

*Main PAKTON interface - Coming Soon*

<img src="./PAKTON Framework/Frontend/v0.2/static/PAKTON_UI_2.png" alt="PAKTON UI - Advanced Features" style="border-radius: 12px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12); border: 1px solid rgba(0, 0, 0, 0.08); margin: 10px 0; max-width: 100%; height: auto;">

*Document upload and chat interface - Coming Soon*

</div>

## 🏗️ Architecture

PAKTON employs a sophisticated multi-agent architecture that orchestrates specialized AI agents to handle different aspects of contract analysis. The framework leverages collaborative agent workflows combined with advanced retrieval-augmented generation (RAG) to provide comprehensive, accurate, and explainable contract review.

<div align="center">

<img src="./PAKTON Framework/Frontend/v0.2/static/PAKTON_architecture.png" alt="PAKTON Architecture" style="border-radius: 12px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12); border: 1px solid rgba(0, 0, 0, 0.08); margin: 20px 0; max-width: 100%; height: auto;">

*Detailed PAKTON architecture showing the multi-agent workflow and RAG component integration*

</div>

## 🧪 Evaluation and Experiments

We evaluated PAKTON using both qualitative and quantitative methods to ensure its effectiveness in real-world legal tasks. You can explore all experiment results and details at:
🔗 https://pakton.site/evaluation

### 📈 Complete Evaluation Framework
- **[Experiments Overview](./Experiments%20and%20Evaluation/README.md)** - Complete evaluation framework and methodology

### Qualitative Evaluation
- **[Human Evaluation](./Experiments%20and%20Evaluation/Qualitative/Human%20Evaluation/README.md)** - Human assessment methodology and results
- **[GEVAL Assessment](./Experiments%20and%20Evaluation/Qualitative/LLM%20as%20a%20judge%20-%20GEVAL/README.md)** - Automated qualitative evaluation using LLM-as-a-judge
- **[Statistical Agreement](./Experiments%20and%20Evaluation/Qualitative/Statistical%20Agreement/README.md)** - Statistical validation of alignment between LLM and human evaluations

### Quantitative Evaluation
- **[ContractNLI Classification](./Experiments%20and%20Evaluation/Quantitative/Classification%20Performance%20-%20ContractNLI/README.md)** - Classification Performance
- **[LegalBenchRAG Performance](./Experiments%20and%20Evaluation/Quantitative/RAG%20Performance%20-%20LegalBenchRAG/README.md)** - Retrieval ability Performance

## ❓ Why PAKTON?

### **Proven Performance**

- **Superior Generation Quality**: Outperforms baseline methods on the ContractNLI dataset
- **State-of-the-Art Retrieval**: RAG component (Researcher) leads performance on LegalBenchRAG benchmark  
- **Human-Preferred**: Chosen by human evaluators over ChatGPT for contract analysis—especially for **Explainability** and **Completeness**.
- **LLM Validation**: GEVAL evaluations show consistent preference for PAKTON over GPT-4o
- **Statistical Validation**: Strong statistical agreement (cosine similarity 0.88-0.92) between automated and human evaluation methods confirms reliability of assessment results

### **Robust, Open, and Adaptable**

- **Privacy-First**: Fully open-source with on-premise deployment capabilities
- **Robust**: According to our robustness analysis, it bridges performance gaps between small and large LLMs, enabling smaller open-source models to rival larger proprietary ones
- **Plug-and-Play**: Modular architecture for seamless extension and custom workflow integration  
- **Transparent Design**: Explainable outputs that contrast with typical black-box AI models

## 📁 Repository Structure

```
PAKTON/
├── LICENSE                                             # License information
├── README.md                                           # This file
├── CONTRIBUTING.md                                     # Contributing Guidelines
├── Docs/                                               # Documentation and research papers
│   └── Preprint_May_25.pdf                             # Research preprint
├── PAKTON Framework/                                   # Core framework implementation
├── Experiments and Evaluation/                         # All experimental work and evaluation
│   ├── Qualitative/                                    # Qualitative evaluation methods
│   │   ├── Human Evaluation/                           # Human assessment results
│   │   ├── LLM as a judge - GEVAL/                     # Automated evaluation using GEVAL
│   │   └── Statistical Agreement/                      # Statistical validation between LLM and human evaluations
│   └── Quantitative/                                   # Quantitative performance evaluation
│       ├── Classification Performance - ContractNLI/   # ContractNLI experiments
│       └── RAG Performance - LegalBenchRAG/            # LegalBenchRAG experiments
└── Machine Learning Experimentation/                   # Additional ML experiments (not mentioned in the paper)
```

## 🤝 Contributing

PAKTON is dedicated to making contractual obligations clearer and more accessible to everyone. We welcome your ideas, code, and feedback to help us make PAKTON even better!

To get started, please review our [**Contributing Guidelines**](CONTRIBUTING.md).

## License

This project is licensed under the terms specified in the [LICENSE](./LICENSE) file.

---

<div align="center">

**Democratizing contract analysis**

🌟 Star this repository if PAKTON helped you! 🌟

</div>