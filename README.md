# ============================================================
# Smart College Assistant — README
# AI-powered College Information & Student Support Platform
# ============================================================

<div align="center">

# 🎓 Smart College Assistant

**Enterprise-Grade AI-Powered College Information & Student Support Platform**

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-green?logo=flask)](https://flask.palletsprojects.com)
[![IBM Granite](https://img.shields.io/badge/IBM-Granite%20AI-0f62fe?logo=ibm)](https://www.ibm.com/watsonx)
[![LangChain](https://img.shields.io/badge/LangChain-0.2-orange)](https://langchain.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Testing](#testing)
- [Docker Deployment](#docker-deployment)

---

## 🔍 Overview

Smart College Assistant is a production-ready, enterprise-grade AI platform that helps college students and faculty with admissions, academics, placements, policies, and more — all through a modern AI chatbot powered by **IBM watsonx.ai Granite** foundation models and a **LangChain RAG pipeline**.

---

## ✨ Features

| Category | Features |
|---|---|
| 🤖 **AI Chatbot** | IBM Granite LLM, Multi-Agent System, Conversation Memory |
| 🔍 **RAG Search** | FAISS Vector Store, Sentence Transformers, Source Citations |
| 🔐 **Authentication** | Student/Faculty/Admin Login, RBAC, Session Security |
| 🎓 **Academics** | Timetable, Attendance Tracker, Marks, CGPA Calculator |
| 📋 **Admission** | Application Form, Documents, Fee Structure, Scholarships |
| 💼 **Placement** | Drive Calendar, Eligibility Checker, Resume Analyzer |
| 📢 **Notifications** | Real-time Updates, Priority Alerts, Category Filtering |
| 🛡️ **Policies** | Attendance, Library, Hostel, Anti-Ragging |
| 📊 **Dashboard** | Student Dashboard with Charts, Admin Analytics |
| 🔧 **Smart Tools** | CGPA Calc, Attendance Calc, Exam Countdown |

---

## 🏗️ Architecture

```
Smart College Assistant
├── 🧠 AI Layer
│   ├── IBM watsonx.ai (Granite LLM)
│   ├── FAISS Vector Store (RAG)
│   ├── Sentence Transformers (Embeddings)
│   └── LangChain Pipelines
│
├── 🤖 Multi-Agent System
│   ├── CoordinatorAgent (Router)
│   ├── AdmissionAgent
│   ├── ExamAgent
│   ├── PlacementAgent
│   ├── PolicyAgent
│   ├── TimetableAgent
│   ├── FAQAgent
│   └── RAGAgent
│
├── 🌐 REST API (Flask)
│   ├── /api/auth      Authentication
│   ├── /api/chat      AI Chatbot
│   ├── /api/student   Student Data
│   ├── /api/admission Admissions
│   ├── /api/exam      Examinations
│   ├── /api/placement Placements
│   ├── /api/policy    Policies
│   └── /api/search    RAG Search
│
└── 💻 Frontend
    ├── 11 UI Pages (HTML5 + Bootstrap 5)
    ├── Dark/Light Theme
    ├── Chart.js Dashboards
    └── Responsive Design
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Language** | Python 3.11 |
| **Framework** | Flask 3.0 + Flask-Session |
| **AI LLM** | IBM watsonx.ai (Granite-13b) |
| **AI Framework** | LangChain 0.2 |
| **Vector Store** | FAISS |
| **Embeddings** | Sentence Transformers |
| **Database** | SQLite + SQLAlchemy |
| **Frontend** | HTML5 + Bootstrap 5 + Chart.js |
| **Security** | bcrypt, Session CSRF |
| **Deployment** | Docker + Gunicorn |

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
# Clone repository
git clone https://github.com/yourorg/smart-college-assistant.git
cd smart-college-assistant

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your IBM watsonx.ai credentials
```

### 3. Initialize & Run

```bash
# Initialize database with sample data
python database/seed_data.py

# Start the application
python app.py
```

### 4. Open in Browser

```
http://localhost:5000
```

**Demo Credentials:**
| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `Admin@123` |
| Student | `cs001` | `Student@123` |
| Faculty | `fac001` | `Faculty@123` |

---

## ⚙️ Configuration

Copy `.env.example` to `.env` and set:

```env
# IBM watsonx.ai (for full AI functionality)
WATSONX_API_KEY=your_ibm_cloud_api_key
WATSONX_PROJECT_ID=your_watsonx_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com

# Flask
FLASK_SECRET_KEY=your-strong-secret-key
FLASK_DEBUG=False

# Database
DATABASE_URL=sqlite:///data/smart_college.db
```

> **Note:** Without watsonx.ai credentials, the system uses `MockLLM` and still demonstrates all features.

---

## 📡 API Reference

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/login` | User login |
| POST | `/api/auth/logout` | User logout |
| GET | `/api/auth/me` | Current user |
| POST | `/api/auth/change-password` | Change password |

### AI Chatbot
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/chat/message` | Send message |
| GET | `/api/chat/suggestions` | Quick suggestions |
| POST | `/api/chat/clear` | Clear history |

### Calculators
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/exam/cgpa-calculator` | Calculate CGPA |
| POST | `/api/exam/attendance-calculator` | Check attendance |
| POST | `/api/placement/eligibility-check` | Placement eligibility |

### RAG Search
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/upload/document` | Upload & index doc |
| POST | `/api/search/` | Semantic search |

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage report
pytest tests/ --cov=. --cov-report=html
```

---

## 🐳 Docker Deployment

```bash
# Build and start
docker-compose up --build -d

# View logs
docker-compose logs -f smart-college

# Stop
docker-compose down
```

---

## 📁 Project Structure

```
smart college/
├── agents/          # Multi-agent system
├── api/             # REST API blueprints
├── config/          # App configuration
├── database/        # SQLAlchemy models & seeds
├── embeddings/      # Sentence Transformer service
├── loaders/         # PDF & document loaders
├── models/          # IBM watsonx.ai wrapper
├── prompts/         # System & few-shot prompts
├── rag/             # RAG pipeline & chunker
├── services/        # Business logic
├── tools/           # AI agent tools
├── ui/              # Frontend templates & static
├── utils/           # Logger, validators, helpers
├── vectorstore/     # FAISS persistence
├── workflows/       # Agent orchestration
├── tests/           # Test suite
├── app.py           # Flask application factory
└── requirements.txt
```

---

## 📜 License

MIT License — © 2026 Smart Engineering College AI Team

---

<div align="center">
Made with ❤️ using IBM Granite AI · LangChain · FAISS · Flask
</div>
