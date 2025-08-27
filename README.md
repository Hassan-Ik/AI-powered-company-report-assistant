# AI-Powered Company Reports Assistant

An intelligent web application that helps users analyze and understand complex company reports. Using AI, this tool provides key metrics, summaries, insights, and reviews on financial and business reports, turning jargon-heavy documents into actionable information.  

The project consists of:  
- **Backend:** Built with **FastAPI**, handling AI processing, metrics extraction, and insights generation.  
- **Frontend:** Built with **Next.js**, providing a modern, responsive interface for uploading reports and viewing AI-generated insights.  

---

## Features

- **Automatic Report Summarization:** Generate concise summaries of lengthy company reports.  
- **Key Metrics Extraction:** Highlight important financial and business metrics for quick understanding.  
- **Insightful Analysis:** AI-powered insights and review of the report, helping users make informed decisions.  
- **Jargon Simplification:** Converts complex business and financial terminology into easy-to-understand language.  
- **Interactive Frontend:** User-friendly interface for uploading reports and navigating insights.  

---

## Tech Stack

- **Backend:** FastAPI, Python, OpenAI API (or custom AI models), Pydantic, Uvicorn  
- **Frontend:** Next.js, React, Tailwind CSS (optional for styling)  
- **Deployment:** Vercel for Frontend and Render for backend  

---

## Installation

### Backend

```
bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

Also create a .env file and store OpenAI key in it.

### Frontend
```
cd frontend
cd ai-company-report-assistant
npm install
npm run dev
```

### Usage

* Start the backend server (FastAPI)
* Start the frontend development server (Next.js)
* Open http://localhost:3000 in your browser
* Upload a company report (PDF, DOCX, or TXT)
* Optional Upload company related guidlines or your own custom guidelines (PDF, or TXT)
* View AI-generated summary, key metrics, insights, and review


Demo Frontend Link: https://ai-powered-company-report-assistant-plum.vercel.app/



