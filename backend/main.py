"""
Dynamic Dashboard API - FastAPI Backend
Syncs with Google Sheets and provides real-time statistics
"""

import os
import json
import base64
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

# Handle service account credentials
SERVICE_ACCOUNT_FILE = "service_account.json"

# Check if service account is provided as base64 in environment (for Render/production)
if os.getenv('SERVICE_ACCOUNT_JSON'):
    try:
        service_account_json = base64.b64decode(os.getenv('SERVICE_ACCOUNT_JSON')).decode()
        with open(SERVICE_ACCOUNT_FILE, 'w') as f:
            f.write(service_account_json)
    except Exception as e:
        print(f"Warning: Could not decode SERVICE_ACCOUNT_JSON from environment: {e}")

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

# Official 47 Counties of Kenya (properly capitalized)
OFFICIAL_COUNTIES = [
    "BARINGO", "BOMET", "BUNGOMA", "BUSIA", "ELGEYO MARAKWET", "EMBU",
    "GARISSA", "HOMA BAY", "ISIOLO", "KAJIADO", "KAKAMEGA", "KERICHO",
    "KIAMBU", "KILIFI", "KIRINYAGA", "KISII", "KISUMU", "KITUI",
    "KWALE", "LAIKIPIA", "LAMU", "MACHAKOS", "MAKUENI", "MANDERA",
    "MARSABIT", "MERU", "MIGORI", "MOMBASA", "MURANGA", "NAIROBI",
    "NAKURU", "NANDI", "NAROK", "NYAMIRA", "NYANDARUA", "NYERI",
    "SAMBURU", "SIAYA", "TAITA TAVETA", "TANA RIVER", "THARAKA NITHI",
    "TRANS NZOIA", "TURKANA", "UASIN GISHU", "VIHIGA", "WAJIR", "WEST POKOT"
]

# Education level standardization
EDUCATION_LEVELS = {
    "CERTIFICATE": ["cert", "certificate", "certificates", "level 4", "level4", "4", "craft certificate", "craft", "artisan"],
    "DIPLOMA": ["dip", "diploma", "diplomas", "level 5", "level 6", "level5", "level6", "5", "6", "higher diploma"],
    "DEGREE": ["deg", "degree", "degrees", "degreee", "bachelor", "bachelors", "level 7", "level7", "7", "undergraduate"],
    "MASTERS": ["masters", "master", "msc", "ma", "mba", "level 8", "level8", "8", "postgraduate"],
    "PHD": ["phd", "doctorate", "doctoral", "level 9", "level9", "9"]
}


def normalize_county(county_input: str) -> str:
    """
    Normalize county name to match official 47 counties of Kenya
    Handles variations in spelling, case, and common typos
    Default: Returns NAIROBI for any invalid or unrecognized county
    """
    if not county_input or not isinstance(county_input, str):
        return "NAIROBI"
    
    # Clean the input
    cleaned = county_input.strip().upper()
    
    # Filter out invalid entries and default to NAIROBI
    invalid_entries = ["KENYA", "N/A", "NA", "NONE", "NULL", "-", ".", "NIL", "NOT APPLICABLE", ""]
    if cleaned in invalid_entries or cleaned.isdigit():
        return "NAIROBI"
    
    # Remove common prefixes/suffixes
    cleaned = cleaned.replace(" COUNTY", "").replace("COUNTY", "")
    cleaned = cleaned.strip()
    
    # Direct match
    if cleaned in OFFICIAL_COUNTIES:
        return cleaned
    
    # Handle common variations and typos
    county_mapping = {
        "NRBI": "NAIROBI",
        "NRB": "NAIROBI",
        "NAIROBY": "NAIROBI",
        "NAIIROBI": "NAIROBI",
        "MURANGA": "MURANGA",
        "MURANG'A": "MURANGA",
        "MURANG": "MURANGA",
        "TAITA": "TAITA TAVETA",
        "TAVETA": "TAITA TAVETA",
        "ELGEIYO MARAKWET": "ELGEYO MARAKWET",
        "ELGEYO-MARAKWET": "ELGEYO MARAKWET",
        "ELGEYO": "ELGEYO MARAKWET",
        "MARAKWET": "ELGEYO MARAKWET",
        "HOMABAY": "HOMA BAY",
        "HOMA-BAY": "HOMA BAY",
        "TRANSNZOIA": "TRANS NZOIA",
        "TRANS-NZOIA": "TRANS NZOIA",
        "THARAKA-NITHI": "THARAKA NITHI",
        "UASIN-GISHU": "UASIN GISHU",
        "UASINGISHU": "UASIN GISHU",
        "WEST-POKOT": "WEST POKOT",
        "WESTPOKOT": "WEST POKOT",
        "TANA-RIVER": "TANA RIVER",
        "TANARIVER": "TANA RIVER",
    }
    
    if cleaned in county_mapping:
        return county_mapping[cleaned]
    
    # Fuzzy matching for partial matches
    for official_county in OFFICIAL_COUNTIES:
        # Check if cleaned input is contained in or contains the official name
        if cleaned in official_county or official_county in cleaned:
            # Additional check: should be at least 60% of the length
            if len(cleaned) >= len(official_county) * 0.6:
                return official_county
    
    # If no match found, default to NAIROBI (capital city)
    return "NAIROBI"


def normalize_education_level(level_input: str) -> str:
    """
    Normalize education level to standard categories
    """
    if not level_input or not isinstance(level_input, str):
        return ""
    
    cleaned = level_input.strip().lower()
    
    # Remove common words
    cleaned = cleaned.replace("level", "").replace("of training", "").strip()
    
    # Check against standard categories
    for standard_level, variations in EDUCATION_LEVELS.items():
        if cleaned in variations or any(cleaned.startswith(var) for var in variations):
            return standard_level
        # Check if the standard level name is in the input
        if standard_level.lower() in cleaned:
            return standard_level
    
    # Return cleaned uppercase version if no match
    return cleaned.upper() if cleaned else ""


def normalize_company_name(company_input: str) -> str:
    """
    Normalize company names for consistency
    """
    if not company_input or not isinstance(company_input, str):
        return ""
    
    # Clean the input
    cleaned = company_input.strip()
    
    # Remove common suffixes (but preserve them in a standardized way)
    company_suffixes = [
        ("LIMITED", "LTD"),
        ("LTD.", "LTD"),
        ("LTD", "LTD"),
        ("INC.", "INC"),
        ("INCORPORATED", "INC"),
        ("CORPORATION", "CORP"),
        ("CORP.", "CORP"),
        ("CO.", "CO"),
        ("COMPANY", "CO"),
    ]
    
    # Convert to uppercase for consistency
    cleaned_upper = cleaned.upper()
    
    # Common abbreviations and full names mapping
    company_mappings = {
        "KEBS": "KENYA BUREAU OF STANDARDS",
        "KBS": "KENYA BUREAU OF STANDARDS",
        "KENYA BUREAU OF STANDARD": "KENYA BUREAU OF STANDARDS",
        "KRA": "KENYA REVENUE AUTHORITY",
        "KPLC": "KENYA POWER AND LIGHTING COMPANY",
        "KPLC": "KENYA POWER",
        "KENYA POWER & LIGHTING": "KENYA POWER",
        "SAFARICOM PLC": "SAFARICOM",
        "SAFARICOM LIMITED": "SAFARICOM",
        "CO-OPERATIVE BANK": "COOPERATIVE BANK",
        "COOP BANK": "COOPERATIVE BANK",
        "KCB": "KENYA COMMERCIAL BANK",
        "EQUITY BANK": "EQUITY BANK",
        "NHIF": "NATIONAL HOSPITAL INSURANCE FUND",
        "NSSF": "NATIONAL SOCIAL SECURITY FUND",
        "KWS": "KENYA WILDLIFE SERVICE",
        "KFS": "KENYA FOREST SERVICE",
        "KEMRI": "KENYA MEDICAL RESEARCH INSTITUTE",
        "KALRO": "KENYA AGRICULTURAL AND LIVESTOCK RESEARCH ORGANIZATION",
        "KENYATTA NATIONAL HOSPITAL": "KENYATTA NATIONAL HOSPITAL",
        "KNH": "KENYATTA NATIONAL HOSPITAL",
        "MOH": "MINISTRY OF HEALTH",
    }
    
    # Check for exact mapping
    if cleaned_upper in company_mappings:
        return company_mappings[cleaned_upper]
    
    # Check for partial matches
    for abbr, full_name in company_mappings.items():
        if abbr in cleaned_upper or cleaned_upper in abbr:
            return full_name
    
    # Title case for professional appearance
    return cleaned.title() if cleaned else ""


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
            # Get all values including headers
            all_values = self.worksheet.get_all_values()
            
            if not all_values or len(all_values) < 2:
                return []
            
            # Get headers and handle duplicates by adding suffix
            headers = all_values[0]
            header_counts = {}
            unique_headers = []
            
            for header in headers:
                if header in header_counts:
                    header_counts[header] += 1
                    unique_headers.append(f"{header}_{header_counts[header]}")
                else:
                    header_counts[header] = 0
                    unique_headers.append(header)
            
            # Convert rows to dictionaries and apply normalization
            records = []
            for row in all_values[1:]:
                # Pad row if it's shorter than headers
                padded_row = row + [''] * (len(unique_headers) - len(row))
                record = dict(zip(unique_headers, padded_row))
                
                # Apply data normalization
                if "YOUR COUNTY" in record:
                    record["YOUR COUNTY"] = normalize_county(record["YOUR COUNTY"])
                if "REGION/COUNTY" in record:
                    record["REGION/COUNTY"] = normalize_county(record["REGION/COUNTY"])
                if "Your Level of Training (e.g. Deg, Dip, Cert)" in record:
                    record["Your Level of Training (e.g. Deg, Dip, Cert)"] = normalize_education_level(record["Your Level of Training (e.g. Deg, Dip, Cert)"])
                
                # Normalize gender to standard values
                if "GENDER" in record and record["GENDER"]:
                    gender = record["GENDER"].strip().lower()
                    if gender in ["m", "male", "man", "boy"]:
                        record["GENDER"] = "Male"
                    elif gender in ["f", "female", "woman", "girl", "lady"]:
                        record["GENDER"] = "Female"
                    elif gender:
                        record["GENDER"] = "Other"
                
                records.append(record)
            
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
            "health": "/health",
            "metadata": "/metadata",
            "counties": "/counties",
            "levels": "/levels",
            "search": "/search"
        }
    }


@app.get("/metadata")
async def get_metadata():
    """Get metadata about data normalization and standards"""
    return {
        "official_counties": {
            "count": len(OFFICIAL_COUNTIES),
            "list": sorted(OFFICIAL_COUNTIES),
            "description": "Kenya's 47 official counties - all data is normalized to these"
        },
        "education_levels": {
            "count": len(EDUCATION_LEVELS),
            "list": sorted(EDUCATION_LEVELS.keys()),
            "description": "Standardized education levels - all variations are normalized"
        },
        "data_normalization": {
            "counties": "All county name variations are normalized to official names",
            "education": "All education level variations are standardized",
            "companies": "Company names are cleaned and standardized",
            "gender": "Gender values are normalized to Male/Female/Other",
            "courses": "Course names are converted to title case"
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
        
        # Apply filters with normalized values
        if county:
            normalized_county = normalize_county(county)
            records = [r for r in records if r.get("YOUR COUNTY", "") == normalized_county]
        if level:
            normalized_level = normalize_education_level(level)
            records = [r for r in records if r.get("Your Level of Training (e.g. Deg, Dip, Cert)", "") == normalized_level]
        
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
    """Get list of all unique counties (official 47 counties of Kenya)"""
    try:
        client = get_sheets_client()
        records = client.fetch_all_records()
        
        # Get only counties that appear in the data (from official list)
        counties_in_data = set(r.get("YOUR COUNTY", "") for r in records if r.get("YOUR COUNTY") and r.get("YOUR COUNTY") in OFFICIAL_COUNTIES)
        counties = sorted(counties_in_data)
        
        return {
            "counties": counties,
            "total": len(counties),
            "all_official_counties": sorted(OFFICIAL_COUNTIES)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/levels")
async def get_levels():
    """Get list of all unique training levels (standardized)"""
    try:
        client = get_sheets_client()
        records = client.fetch_all_records()
        
        # Get only standard education levels that appear in the data
        levels_in_data = set(r.get("Your Level of Training (e.g. Deg, Dip, Cert)", "") for r in records if r.get("Your Level of Training (e.g. Deg, Dip, Cert)"))
        # Filter to only include our standard levels
        standard_levels = [level for level in levels_in_data if level in EDUCATION_LEVELS.keys()]
        levels = sorted(standard_levels)
        
        return {
            "levels": levels,
            "total": len(levels),
            "all_standard_levels": sorted(EDUCATION_LEVELS.keys())
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def calculate_statistics(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate all statistics from records"""
    
    # Total registrations
    total_registrations = len(records)
    
    # Gender ratio - using actual Google Sheets column name
    genders = [r.get("GENDER", "").strip() for r in records if r.get("GENDER")]
    gender_counter = Counter(genders)
    gender_ratio = {
        "Male": round(gender_counter.get("Male", 0) / total_registrations * 100, 2) if total_registrations else 0,
        "Female": round(gender_counter.get("Female", 0) / total_registrations * 100, 2) if total_registrations else 0,
        "Other": round(gender_counter.get("Other", 0) / total_registrations * 100, 2) if total_registrations else 0,
    }
    
    # Education level breakdown - using actual Google Sheets column name
    education_levels = [r.get("Your Level of Training (e.g. Deg, Dip, Cert)", "").strip() for r in records if r.get("Your Level of Training (e.g. Deg, Dip, Cert)")]
    education_counter = Counter(education_levels)
    education_breakdown = {level: count for level, count in education_counter.most_common()}
    
    # Top 5 courses - using actual Google Sheets column name
    courses = []
    for r in records:
        course = r.get("Your course of study", "").strip()
        if course:
            # Normalize course names to title case for consistency
            normalized_course = course.title()
            courses.append(normalized_course)
    
    course_counter = Counter(courses)
    top_courses = [
        {"name": course, "count": count}
        for course, count in course_counter.most_common(5)
    ]
    
    # Geographic distribution (Top 5 counties) - using actual Google Sheets column name
    counties = [r.get("YOUR COUNTY", "").strip() for r in records if r.get("YOUR COUNTY")]
    county_counter = Counter(counties)
    geographic_distribution = [
        {"county": county, "count": count}
        for county, count in county_counter.most_common(5)
    ]
    
    # Top 10 preferred companies - using actual Google Sheets column name
    companies = []
    for r in records:
        # Handle multiple companies separated by comma
        company_str = r.get("Three Preferred Companies", "").strip()
        if company_str:
            company_list = [normalize_company_name(c) for c in company_str.split(",")]
            # Filter out empty strings
            companies.extend([c for c in company_list if c])
    
    company_counter = Counter(companies)
    preferred_companies = [
        {"name": company, "count": count}
        for company, count in company_counter.most_common(10)
    ]
    
    # Calculate placement rate - using actual Google Sheets column name
    # Handle various forms of "yes" - YES, Yes, yes, TRUE, True, true, Y, y, 1
    placements = []
    for r in records:
        placement_value = str(r.get("PLACED YES OR NO", "")).strip().lower()
        if placement_value in ["yes", "y", "true", "1", "placed"]:
            placements.append(r)
    
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
