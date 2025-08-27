from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os, json, re, asyncio
from openai import OpenAI
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
import time

load_dotenv()

app = FastAPI(
    title="AI Report Assistant API",
    description="Lunim Innovation Studio - AI-powered company report analysis and summarization",
    version="1.0.0"
)

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise HTTPException(status_code=500, detail="OpenAI API key not configured")

client = OpenAI(api_key=api_key)

# Enhanced CORS for deployment
origins = [
    "http://localhost:3000",
    "http://192.168.1.214:3000",
    "https://*.vercel.app",
    "https://*.netlify.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For demo purposes - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ReportAnalysis(BaseModel):
    company_name: Optional[str] = None
    year: Optional[str] = None
    target_year: Optional[str] = None
    key_metrics: Dict[str, Any] = {}
    financial_health_score: Optional[int] = None
    actionable_insights: List[str] = []
    risk_factors: List[str] = []
    opportunities: List[str] = []
    summary: str = ""
    processing_time: float = 0.0

@app.get("/")
async def root():
    return {
        "message": "🚀 Lunim AI Report Assistant - Ready to analyze!",
        "endpoints": {
            "/analyze": "POST - Upload and analyze company reports",
            "/health": "GET - API health check",
            "/demo": "GET - Get demo data"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/demo")
async def get_demo_data():
    """Demo endpoint showing sample analysis results"""
    return {
        "sample_analysis": {
            "company_name": "TechCorp Inc.",
            "year": "2024",
            "financial_health_score": 78,
            "key_metrics": {
                "revenue": "$45.2M",
                "growth_rate": "23%",
                "profit_margin": "12.5%",
                "customer_satisfaction": "4.2/5"
            },
            "actionable_insights": [
                "Focus on expanding into emerging markets for 25% growth potential",
                "Optimize operational costs to improve profit margins by 3-5%",
                "Invest in customer retention programs to boost satisfaction scores"
            ],
            "summary": "Strong growth trajectory with solid fundamentals and clear expansion opportunities."
        }
    }

def extract_pdf_text(pdf_bytes: bytes) -> str:
    """Enhanced PDF text extraction with better error handling"""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page_num, page in enumerate(doc):
            page_text = page.get_text()
            if page_text.strip():  # Only add non-empty pages
                text += f"\n--- Page {page_num + 1} ---\n{page_text}"
        doc.close()
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PDF processing failed: {str(e)}")

def calculate_health_score(metrics: Dict[str, Any]) -> int:
    """Simple algorithm to calculate financial health score"""
    score = 50  # Base score
    
    # Basic scoring logic (can be enhanced)
    for key, value in metrics.items():
        if isinstance(value, str) and '%' in value:
            try:
                percentage = float(value.replace('%', ''))
                if 'growth' in key.lower() and percentage > 10:
                    score += min(20, percentage)
                elif 'margin' in key.lower() and percentage > 5:
                    score += min(15, percentage)
            except ValueError:
                pass
    
    return min(100, max(0, int(score)))

async def analyze_with_ai(content: str, guidelines: str = "") -> Dict[str, Any]:
    """Enhanced AI analysis with structured prompts"""
    
    # Enhanced metrics extraction prompt
    metrics_prompt = f"""
    You are a financial analyst AI. Extract key information from this company report and return ONLY valid JSON:

    {{
        "company_name": "extracted company name or null",
        "year": "report year or null", 
        "target_year": "target/forecast year or null",
        "key_metrics": {{
            "revenue": "revenue figure with currency",
            "growth_rate": "growth percentage", 
            "profit_margin": "profit margin percentage",
            "employees": "number of employees",
            "customer_satisfaction": "satisfaction score",
            "market_share": "market share percentage"
        }},
        "actionable_insights": [
            "specific actionable insight 1",
            "specific actionable insight 2", 
            "specific actionable insight 3"
        ],
        "risk_factors": [
            "identified risk 1",
            "identified risk 2"
        ],
        "opportunities": [
            "growth opportunity 1",
            "growth opportunity 2"
        ]
    }}

    Guidelines to consider: {guidelines}

    Report content: {content[:8000]}  # Limit content for token management
    """

    # Summary prompt
    summary_prompt = f"""
    Create a concise 3-sentence executive summary of this company report focusing on:
    1. Overall performance/status
    2. Key achievements or challenges  
    3. Future outlook

    Guidelines: {guidelines}
    
    Report: {content[:4000]}
    """

    try:
        # Run both requests concurrently for speed
        tasks = [
            client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a financial analysis expert. Return only valid JSON."},
                    {"role": "user", "content": metrics_prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            ),
            client.chat.completions.create(
                model="gpt-4o-mini", 
                messages=[
                    {"role": "system", "content": "You are a business analyst creating executive summaries."},
                    {"role": "user", "content": summary_prompt}
                ],
                temperature=0.2,
                max_tokens=200
            )
        ]

        # Wait for both responses
        metrics_resp, summary_resp = await asyncio.gather(*[
            asyncio.create_task(asyncio.to_thread(lambda: task)) for task in tasks
        ])

        # Process metrics response
        metrics_text = metrics_resp.choices[0].message.content.strip()
        
        # Clean up JSON response
        if metrics_text.startswith('```json'):
            metrics_text = metrics_text.split('```json')[1].split('```')[0]
        elif metrics_text.startswith('```'):
            metrics_text = "\n".join(metrics_text.split('\n')[1:-1])

        parsed_metrics = {}
        try:
            parsed_metrics = json.loads(metrics_text)
        except json.JSONDecodeError:
            # Fallback: try to extract JSON from text
            json_match = re.search(r'\{[\s\S]*\}', metrics_text)
            if json_match:
                try:
                    parsed_metrics = json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    parsed_metrics = {"error": "Could not parse metrics"}

        # Get summary
        summary = summary_resp.choices[0].message.content.strip()

        return {
            "parsed_metrics": parsed_metrics,
            "summary": summary
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

@app.post("/analyze", response_model=Dict[str, Any])
async def analyze_report(
    text: Optional[str] = Form(None),
    guidelines_text: Optional[str] = Form(None),
    report_file: Optional[UploadFile] = File(None),
    guidelines_file: Optional[UploadFile] = File(None)
):
    """
    Analyze company reports with AI-powered insights extraction
    Supports both text input and PDF file uploads
    """
    start_time = time.time()
    
    try:
        # Extract report content
        report_content = ""
        
        if report_file:
            if not report_file.filename.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail="Only PDF files supported for report uploads")
            
            pdf_bytes = await report_file.read()
            report_content = extract_pdf_text(pdf_bytes)
            
        elif text:
            report_content = text
        else:
            raise HTTPException(status_code=400, detail="Please provide report content (text or PDF file)")

        if len(report_content.strip()) < 100:
            raise HTTPException(status_code=400, detail="Report content too short for meaningful analysis")

        # Extract guidelines
        guidelines_content = ""
        if guidelines_file:
            if not guidelines_file.filename.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail="Only PDF files supported for guidelines")
            
            pdf_bytes = await guidelines_file.read()
            guidelines_content = extract_pdf_text(pdf_bytes)
        elif guidelines_text:
            guidelines_content = guidelines_text

        # Perform AI analysis
        analysis_result = await analyze_with_ai(report_content, guidelines_content)
        
        parsed_metrics = analysis_result["parsed_metrics"]
        summary = analysis_result["summary"]

        # Calculate processing time
        processing_time = round(time.time() - start_time, 2)

        # Build response
        response = ReportAnalysis(
            company_name=parsed_metrics.get("company_name"),
            year=parsed_metrics.get("year"),
            target_year=parsed_metrics.get("target_year"),
            key_metrics=parsed_metrics.get("key_metrics", {}),
            financial_health_score=calculate_health_score(parsed_metrics.get("key_metrics", {})),
            actionable_insights=parsed_metrics.get("actionable_insights", []),
            risk_factors=parsed_metrics.get("risk_factors", []),
            opportunities=parsed_metrics.get("opportunities", []),
            summary=summary,
            processing_time=processing_time
        )

        return {
            "success": True,
            "data": response.dict(),
            "meta": {
                "processing_time_seconds": processing_time,
                "content_length": len(report_content),
                "has_guidelines": bool(guidelines_content)
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)