# Industrial Energy Management System

Industrial Energy Management System is an enterprise-grade, microservice-based platform designed to monitor, analyze, and optimize heavy industrial energy consumption. Built with a strict focus on sustainability and data privacy, the system features a real-time IoT telemetry pipeline, carbon footprint tracking, and a completely localized, air-gapped Artificial Intelligence engine capable of answering operational queries and drafting ISO 50001 compliance reports.

This project was developed at the Vidyalankar Institute of Technology (VIT), Mumbai as a capstone engineering demonstration of sustainable technology and localized machine learning pipelines.

---

## ✨ Core Features (The 6-Pillar Dashboard)

### 🏭 Command Center
- Real-time monitoring of live factory power load  
- Active anomaly detection  
- Machine thermal health tracking  

### 📊 Analytics & Trends
- Interactive historical data visualization using Pandas  
- Dynamic Timeframe Filters:
  - 1 Hour  
  - 24 Hours  
  - All Data  
- Identify top power consumers and thermal outliers without distortion  

### 💰 Cost & ROI Calculator
- Maps energy load to grid pricing  
- Projects savings from anomaly prevention  

### 🌱 Sustainability Tracker
- ESG score (percentage-based)  
- Live "Tree Equivalent" offset calculations (rolling 60-minute window)  
- Dynamically generated actionable reduction strategies  

### 📄 Reports & Compliance
- Offline transformer model (GPT-2)  
- Generates secure ISO 50001 executive summaries  
- No external API usage (fully local processing)  

### 🤖 AI Chat Assistant (Hybrid Engine)
- 100% local, air-gapped AI consultant  
- Combines:
  - Hardcoded Advisory Engine  
  - Custom PyTorch + DistilBERT implementation  
- Extracts real-time telemetry insights  

---

## 🛠️ Architecture & Tech Stack

- **Frontend UI:** Streamlit (st.sidebar, st.columns, st.metric, st.radio)  
- **Backend API:** Python, Flask (RESTful routes)  
- **Database:** SQLite (High-frequency Time-Series IoT Simulation)  
- **Machine Learning / NLP:** Hugging Face Transformers, PyTorch  
- **Data Processing:** Pandas, NumPy, Requests, Math  

---

## 📂 Project Structure
```
OmniGreen_Energy_System/
│
├── iot_simulator.py # Simulates factory hardware and injects high-frequency data into SQLite
├── app.py # Flask API serving live calculations and historical payload routes
├── dashboard.py # Streamlit UI containing the 6-tab OmniGreen OS interface
├── report_generator.py # Local GPT-2 text generation engine for ESG reporting
├── factory_data.db # Automatically generated SQLite database (created on first run)
└── README.md # Project documentation
```
## 🚀 Installation & Setup

### 1. Prerequisites
Ensure you have **Python 3.8+** installed on your machine.  
It is highly recommended to use a virtual environment (`venv`).

---

### 2. Install Dependencies

Run the following command to install all required libraries:

```bash
pip install flask streamlit requests pandas transformers torch
```

> **Note:** The first time you run the AI features, the system will securely download the GPT-2 and DistilBERT model weights (~750MB total) into your local cache.

---

### 3. Running the Microservices

OmniGreen is **decoupled by design**. You must start the microservices in **three separate terminal windows** so they can communicate seamlessly.

#### 🖥️ Terminal 1: Start the Factory IoT Simulator
```bash
python iot_simulator.py
```
Leave this running in the background to continuously pump live telemetry into the database.

---

#### 🖥️ Terminal 2: Start the Backend Math & Routing Engine
```bash
python app.py
```
The Flask API will boot up and serve data at:  
http://127.0.0.1:5000

---

#### 🖥️ Terminal 3: Launch the Command Center
```bash
streamlit run dashboard.py
```
Your default web browser will automatically open the interactive OmniGreen OS.

---

## 🧠 Air-Gapped AI Implementation Notes

To guarantee **100% data privacy** for sensitive factory infrastructure, this project strictly avoids third-party API calls (such as OpenAI or Anthropic).

### 📄 Report Generation
- Uses a **local text-generation pipeline**

### 🤖 Chat Assistant
- Bypasses standard library wrappers entirely  
- Utilizes a **custom PyTorch implementation** to:
  - Manually tokenize contextual data  
  - Calculate tensor logits  
  - Extract answer coordinates directly from the neural network  
