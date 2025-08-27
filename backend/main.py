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
    title="AI Powered Company Report Assistant",
    description="AI powered report summarization and review tool",
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
    "http://192.168.1.214:3000"
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
    report_type: Optional[str] = None
    year: Optional[str] = None
    important_metrics: Dict[str, Any] = {}
    summary: str = ""
    review: str = ""
    processing_time: float = 0.0

@app.get("/")
async def root():
    return {
        "message": "Wrong Site!"
    }


@app.get("/demo")
async def get_demo_data():
    """Demo endpoint showing sample analysis results"""
    return {
        "sample_analysis": {
            "company_name": "TechFlow Solutions",
            "report_type": "Quarterly Performance Report",
            "year": "Q3 2024",
            "important_metrics": {
                "Total Revenue": "$12.4M",
                "Customer Base": "45,000 users",
                "Monthly Growth": "8.2%",
                "Customer Satisfaction": "4.3/5",
                "Team Size": "127 employees"
            },
            "summary": "TechFlow Solutions reported strong Q3 2024 performance with $12.4M revenue and 45,000 active users. The company maintained steady 8.2% monthly growth while achieving high customer satisfaction scores. The team expanded to 127 employees to support continued growth.",
            "review": "The report demonstrates solid business fundamentals with consistent growth metrics. Revenue figures align well with user acquisition data, suggesting healthy unit economics. Customer satisfaction scores above 4.0 indicate strong product-market fit. The expansion of the team appears strategic and proportional to growth. However, the report could benefit from more detailed breakdown of revenue sources and clearer projections for Q4. Overall, this represents a well-structured quarterly report with positive indicators across key business areas."
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


async def analyze_with_ai(content: str, guidelines: str = "") -> Dict[str, Any]:
    # Metrics extraction prompt
    prompt_metrics = (
            "You are an AI assistant that extracts key company report metrics and actionable insights.\n"
            "Please carefully read the company report text provided and return a valid JSON object with the following structure:\n\n"
            "{\n"
            "  \"company_name\": string or null,\n"
            "  \"year\": string or null,\n"
            "  \"target_year\": string or null,\n"
            "  \"key_metrics\": {\n"
            "      \"employees\": { ... },\n"
            "      \"investors\": { ... },\n"
            "      \"customers\": { ... },\n"
            "      ... any other relevant categories\n"
            "  },\n"
            "  \"actionable_insights\": [ list of clear, concise actionable points derived from the report ]\n"
            "}\n\n"
        )

    if guidelines:
        prompt_metrics += (
            "Also consider the following guidelines while extracting metrics and insights:\n"
            + guidelines + "\n\n"
        )

    prompt_metrics += "Report Text:\n" + content + "\n\n"
    prompt_metrics += "Important:\n"
    prompt_metrics += "- Only return valid JSON with the fields specified.\n"
    prompt_metrics += "- Include numerical values where possible.\n"
    prompt_metrics += "- Be concise and clear in the actionable_insights list."


    # Summary prompt
    summary_prompt = f"""
    Write a clear, concise summary of this report in no more than 10 sentences. 
    Focus on main findings, key data points, and conclusions.
    Write for someone who hasn't read the full report.

    {f"Follow these guidelines: {guidelines}" if guidelines else ""}

    Report: {content}
    """

    # Review prompt
    review_prompt = f"""
    Provide a thoughtful review of this report covering:
    - Quality and clarity of the data presented
    - Strengths of the analysis
    - Areas needing improvement
    - Overall assessment

    Write 4–6 sentences of constructive feedback.

    {f"Consider these guidelines: {guidelines}" if guidelines else ""}

    Report: {content}
    """

    try:
        # --- Metrics request ---
        metrics_resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Extract structured data in strict JSON format."},
                {"role": "user", "content": prompt_metrics},
            ],
            temperature=0.0,
            max_tokens=800,
        )

        metrics_text = metrics_resp.choices[0].message.content.strip()

        # Remove ``` or ```json fences if present
        metrics_text = re.sub(r"^```(?:json)?\s*|\s*```$", "", metrics_text, flags=re.MULTILINE).strip()

        parsed_metrics = None
        try:
            parsed_metrics = json.loads(metrics_text)
        except json.JSONDecodeError:
            # Fallback: extract the first {...} block
            match = re.search(r"\{[\s\S]*\}", metrics_text)
            if match:
                try:
                    parsed_metrics = json.loads(match.group(0))
                except json.JSONDecodeError:
                    parsed_metrics = {}
            else:
                parsed_metrics = {}

        # --- Summary request ---
        summary_resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Create clear, informative report summaries."},
                {"role": "user", "content": summary_prompt},
            ],
            temperature=0.2,
            max_tokens=200,
        )
        summary = summary_resp.choices[0].message.content.strip()

        # --- Review request ---
        review_resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Provide constructive reviews of reports."},
                {"role": "user", "content": review_prompt},
            ],
            temperature=0.3,
            max_tokens=300,
        )
        review = review_resp.choices[0].message.content.strip()

        return {
            "parsed_metrics": parsed_metrics,
            "summary": summary,
            "review": review,
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
            report_type=parsed_metrics.get("report_type"),
            year=parsed_metrics.get("year"),
            important_metrics=parsed_metrics.get("key_metrics", {}),
            summary=summary,
            review=analysis_result["review"],
            processing_time=processing_time
        )

        return {
            "success": True,
            "data": response.dict(),
            "meta": {
                "processing_time_seconds": processing_time,
                "has_guidelines": bool(guidelines_content)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")