"""
Dynamic Dashboard API - FastAPI Backend
Syncs with Google Sheets and provides real-time statistics
"""

import os
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from collections import Counter
from functools import lru_cache

import gspread
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from oauth2client.service_account import ServiceAccountCredentials

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Dynamic Dashboard API",
    description="Real-time dashboard API synced with Google Sheets",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Google Sheets Configuration
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

SPREADSHEET_ID = "1Iay4dQmuLycikpjtHO-ATpc0cqkMSxiP_UBlAHX5-ns"
SERVICE_ACCOUNT_FILE = "service_account.json"


class GoogleSheetsClient:
    """Manages Google Sheets connection and data fetching"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize Google Sheets client"""
        if not os.path.exists(SERVICE_ACCOUNT_FILE):
            raise FileNotFoundError(
                f"{SERVICE_ACCOUNT_FILE} not found. "
                "Please create it via Google Cloud Console."
            )
        
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                SERVICE_ACCOUNT_FILE, SCOPE
            )
            self.client = gspread.authorize(creds)
            self.spreadsheet = self.client.open_by_key(SPREADSHEET_ID)
            self.worksheet = self.spreadsheet.sheet1
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Google Sheets client: {str(e)}")
    
    def fetch_all_records(self) -> List[Dict[str, Any]]:
        """Fetch all records from the worksheet"""
        try:
            records = self.worksheet.get_all_records()
            return records
        except Exception as e:
            raise RuntimeError(f"Failed to fetch records from Google Sheets: {str(e)}")


def get_sheets_client() -> GoogleSheetsClient:
    """Get or initialize Google Sheets client"""
    return GoogleSheetsClient()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Dynamic Dashboard API",
        "endpoints": {
            "data": "/data",
            "stats": "/stats",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        client = get_sheets_client()
        client.fetch_all_records()
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/data")
async def get_data(
    limit: Optional[int] = Query(None, gt=0),
    offset: Optional[int] = Query(0, ge=0)
):
    """
    Fetch all records from Google Sheet
    
    - **limit**: Maximum number of records to return
    - **offset**: Number of records to skip
    """
    try:
        client = get_sheets_client()
        records = client.fetch_all_records()
        
        # Apply offset and limit
        if offset:
            records = records[offset:]
        if limit:
            records = records[:limit]
        
        return {
            "total": len(records),
            "count": len(records),
            "data": records,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats(county: Optional[str] = Query(None), level: Optional[str] = Query(None)):
    """
    Get aggregated statistics from the sheet
    
    Query Parameters:
    - **county**: Filter by county (optional)
    - **level**: Filter by level of training (optional)
    """
    try:
        client = get_sheets_client()
        records = client.fetch_all_records()
        
        # Apply filters
        if county:
            records = [r for r in records if r.get("Your County", "").lower() == county.lower()]
        if level:
            records = [r for r in records if r.get("Level of Training", "").lower() == level.lower()]
        
        if not records:
            return {
                "total_registrations": 0,
                "gender_ratio": {},
                "education_breakdown": {},
                "top_courses": [],
                "geographic_distribution": [],
                "preferred_companies": [],
                "filtered": bool(county or level)
            }
        
        # Calculate statistics
        stats = calculate_statistics(records)
        stats["filtered"] = bool(county or level)
        stats["timestamp"] = datetime.now().isoformat()
        
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/counties")
async def get_counties():
    """Get list of all unique counties"""
    try:
        client = get_sheets_client()
        records = client.fetch_all_records()
        
        counties = sorted(set(r.get("Your County", "") for r in records if r.get("Your County")))
        return {"counties": counties}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/levels")
async def get_levels():
    """Get list of all unique training levels"""
    try:
        client = get_sheets_client()
        records = client.fetch_all_records()
        
        levels = sorted(set(r.get("Level of Training", "") for r in records if r.get("Level of Training")))
        return {"levels": levels}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def calculate_statistics(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate all statistics from records"""
    
    # Total registrations
    total_registrations = len(records)
    
    # Gender ratio
    genders = [r.get("Gender", "").strip() for r in records if r.get("Gender")]
    gender_counter = Counter(genders)
    gender_ratio = {
        "Male": round(gender_counter.get("Male", 0) / total_registrations * 100, 2) if total_registrations else 0,
        "Female": round(gender_counter.get("Female", 0) / total_registrations * 100, 2) if total_registrations else 0,
        "Other": round(gender_counter.get("Other", 0) / total_registrations * 100, 2) if total_registrations else 0,
    }
    
    # Education level breakdown
    education_levels = [r.get("Level of Training", "").strip() for r in records if r.get("Level of Training")]
    education_counter = Counter(education_levels)
    education_breakdown = {level: count for level, count in education_counter.most_common()}
    
    # Top 5 courses
    courses = [r.get("Course of Study", "").strip() for r in records if r.get("Course of Study")]
    course_counter = Counter(courses)
    top_courses = [
        {"name": course, "count": count}
        for course, count in course_counter.most_common(5)
    ]
    
    # Geographic distribution (Top 5 counties)
    counties = [r.get("Your County", "").strip() for r in records if r.get("Your County")]
    county_counter = Counter(counties)
    geographic_distribution = [
        {"county": county, "count": count}
        for county, count in county_counter.most_common(5)
    ]
    
    # Top 10 preferred companies
    companies = []
    for r in records:
        # Handle multiple companies separated by comma
        company_str = r.get("Preferred Companies", "").strip()
        if company_str:
            company_list = [c.strip() for c in company_str.split(",")]
            companies.extend(company_list)
    
    company_counter = Counter(companies)
    preferred_companies = [
        {"name": company, "count": count}
        for company, count in company_counter.most_common(10)
    ]
    
    # Calculate placement rate (if "Placement" field exists)
    placements = [r for r in records if r.get("Placement") and r.get("Placement").lower() == "yes"]
    placement_rate = round(len(placements) / total_registrations * 100, 2) if total_registrations else 0
    
    return {
        "total_registrations": total_registrations,
        "placement_rate": placement_rate,
        "gender_ratio": gender_ratio,
        "education_breakdown": education_breakdown,
        "top_courses": top_courses,
        "geographic_distribution": geographic_distribution,
        "preferred_companies": preferred_companies
    }


@app.get("/search")
async def search(
    query: str = Query(..., min_length=1),
    field: Optional[str] = Query(None)
):
    """
    Search records by query
    
    - **query**: Search term
    - **field**: Specific field to search in (optional)
    """
    try:
        client = get_sheets_client()
        records = client.fetch_all_records()
        
        query_lower = query.lower()
        
        if field:
            results = [r for r in records if query_lower in str(r.get(field, "")).lower()]
        else:
            results = [
                r for r in records
                if any(query_lower in str(v).lower() for v in r.values())
            ]
        
        return {
            "query": query,
            "count": len(results),
            "data": results[:50]  # Limit to 50 results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
