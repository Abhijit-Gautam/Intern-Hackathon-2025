# 📬 Email-Folder AI Agent Hackathon

Welcome to the **Email-Folder AI Agent Hackathon**! 🎉 In this challenge, you’ll build an intelligent agent that:

1. Reads customer emails from a designated folder  
2. Parses sender, subject, body text, and attachments (mostly PDFs)  
3. Invokes a document‐extraction API or model to pull structured content  
4. Generates a concise summary of both email context and extracted document details  
5. (Optional) Presents the summary on a lightweight web front‐end for user confirmation  

---

## 🏆 Challenge Overview

Many businesses receive dozens—or even hundreds—of emails per day, each potentially containing valuable documents. Your goal is to automate this pipeline end to end:

1. **Ingest**: Load raw `.eml` or `.msg` files from a given folder  
2. **Parse**: Extract metadata (sender, subject), body text, and attachments  
3. **Extract**: Feed attachments into a document‐extraction API or your own model to obtain structured data  
4. **Summarize & Confirm**: Produce a human‐readable summary (JSON or HTML) of email + document contents, ready for user confirmation via a simple web UI  
5. **Deliver**: Package your solution into a GitHub repo, complete with a flowchart and clear run instructions  

---

## 🎯 What We’re Looking For

- **Correctness & Coverage**  
  - All emails in the folder are processed reliably  
  - Attachments (PDFs, DOCX, images) are parsed and extracted  
  - Summaries include both email metadata and document content details  

- **Architecture Clarity**  
  - A clear flowchart (PNG, SVG, or Mermaid in Markdown) illustrating each stage  
  - Well‐structured README with step‐by‐step setup/run guide  

- **Code Quality & Modularity**  
  - Clean, maintainable code (Python, Node.js, Java, etc.)  
  - Robust error handling (missing fields, corrupt files, network issues)  

- **Ease of Deployment**  
  - Simple local setup instructions (`pip install`, `npm install`)  
  - Bonus: Dockerfile or `docker-compose.yml`  

- **Innovation & UX**  
  - Bonus for a lightweight web front‐end (React/Flask/Express) for manual confirmation/editing of extracted data  

---

## 🗂️ Dataset

A ZIP archive containing sample emails (included in this repo under `/emails`):

- `emails/sample1.eml`  
- `emails/sample2.eml`  
- …  

Each may include zero or more attachments (`.pdf`, `.docx`, `.jpeg`).

> **Tip:** You can generate your own test emails or leverage open‐source libraries like [mailparser](https://github.com/mscdex/mailparser) or [Apache Tika](https://tika.apache.org/) for parsing.

---

## 📦 Deliverables

1. **`README.md`** (this file)  
2. **`flowchart.*`** – Diagram (PNG/SVG/Mermaid) illustrating your end-to-end pipeline  
3. **Source code** under `/src`  
4. **Dependency & Run Instructions**, for example:  
    
        git clone https://github.com/your-org/your-repo.git
        cd your-repo
        pip install -r requirements.txt     # or npm install
        ./run_agent.sh                      # or npm start

5. **Sample outputs** for the provided emails under `/output`  
6. *(Optional)* **Dockerfile** or **`docker-compose.yml`** for containerized setup  
7. *(Optional)* **Web UI** under `/web` demonstrating manual confirmation/editing  

---

## 🚀 How to Submit

1. **Fork** this repository  
2. **Implement** your solution, add your flowchart, and update this README  
3. **Push** to your fork and open a **Pull Request** against `main`  
4. In your PR description, include:  
   - A brief overview of your approach  
   - Any special dependencies or setup steps  
   - (If applicable) Link to a live demo or screenshot  

---

## 🏅 Evaluation Criteria

| Category                 | Weight |
| ------------------------ | ------ |
| **Functionality**        | 40%    |
| **Architecture Clarity** | 25%    |
| **Code Quality**         | 15%    |
| **Ease of Deployment**   | 10%    |
| **Innovation & UX**      | 10%    |

Winners will be selected based on the combined score across these areas.

---

## 📅 Timeline

- **Kick-off:** May 30, 2025  
- **Submission Deadline:** June 10, 2025, 23:59 IST  
- **Winners Announced:** June 16, 2025  

---

## 📜 Rules & Guidelines

- Teams of **1** participants  
- All code must be original or properly attributed  
- No plagiarism—automated and manual checks will be performed  
- Keep your fork **public** until winners are announced  

---

## 📚 Resources

- [mailparser (Node.js)](https://github.com/mscdex/mailparser)  
- [Python `email` library](https://docs.python.org/3/library/email.html)  
- [Apache Tika](https://tika.apache.org/) for document parsing  
- [Mermaid](https://mermaid-js.github.io/) or [Graphviz](https://graphviz.org/) for flowcharts  

---

## ❓ Questions?

If you have any questions, please:

- Open an **issue** in this repo  
- Email us at **hr@cargoa.io**  

Good luck, and happy hacking! 🚀  
