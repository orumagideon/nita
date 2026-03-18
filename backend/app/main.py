"""
Dynamic Dashboard API - FastAPI Backend
Syncs with Google Sheets and provides real-time statistics
"""

import os
import json
import base64
import re
import unicodedata
from difflib import get_close_matches
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


def get_quarter(date_str: str) -> str:
    """
    Get quarter from date string
    Q1: July-September (07-09)
    Q2: October-December (10-12)
    Q3: January-March (01-03)
    Q4: April-June (04-06)
    
    Supports various date formats: YYYY-MM-DD, MM/DD/YYYY, etc.
    Returns "Unknown" if date cannot be parsed
    """
    if not date_str or not isinstance(date_str, str):
        return "Unknown"
    
    try:
        # Normalize and handle noisy values like "F", "N/A", etc.
        raw_value = date_str.strip()
        cleaned_value = raw_value.replace("  ", " ").strip()
        if not cleaned_value or cleaned_value.upper() in {"F", "N/A", "NA", "NULL", "NONE", "-"}:
            return "Unknown"

        month = None

        # Parse common datetime/date formats from Google Forms / Sheets
        supported_formats = [
            '%m/%d/%Y %H:%M:%S',
            '%m/%d/%Y %H:%M',
            '%m/%d/%Y %I:%M:%S %p',
            '%m/%d/%Y',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
            '%d/%m/%Y %H:%M:%S',
            '%d/%m/%Y',
            '%m-%d-%Y %H:%M:%S',
            '%m-%d-%Y',
            '%Y/%m/%d %H:%M:%S',
            '%Y/%m/%d',
        ]

        for fmt in supported_formats:
            try:
                month = datetime.strptime(cleaned_value, fmt).month
                break
            except ValueError:
                continue

        # Fallback: parse numeric month from first date-like token
        if month is None:
            first_token = cleaned_value.split()[0]
            if '/' in first_token:
                parts = first_token.split('/')
                if len(parts) >= 3 and parts[0].isdigit() and 1 <= int(parts[0]) <= 12:
                    month = int(parts[0])
            elif '-' in first_token:
                parts = first_token.split('-')
                if len(parts) >= 3:
                    if parts[0].isdigit() and 1 <= int(parts[0]) <= 12:
                        month = int(parts[0])
                    elif parts[1].isdigit() and 1 <= int(parts[1]) <= 12:
                        month = int(parts[1])

        if month is None:
            return "Unknown"
        
        # Categorize by quarter
        if month in [7, 8, 9]:
            return "Q1 (Jul-Sep)"
        elif month in [10, 11, 12]:
            return "Q2 (Oct-Dec)"
        elif month in [1, 2, 3]:
            return "Q3 (Jan-Mar)"
        elif month in [4, 5, 6]:
            return "Q4 (Apr-Jun)"
        else:
            return "Unknown"
    except Exception:
        return "Unknown"


def parse_application_date(date_str: str) -> Dict[str, Any]:
    """
    Parse application date and return both year and quarter.
    Returns: {"year": int | None, "quarter": str}
    """
    if not date_str or not isinstance(date_str, str):
        return {"year": None, "quarter": "Unknown"}

    try:
        raw_value = date_str.strip()
        cleaned_value = raw_value.replace("  ", " ").strip()
        if not cleaned_value or cleaned_value.upper() in {"F", "N/A", "NA", "NULL", "NONE", "-"}:
            return {"year": None, "quarter": "Unknown"}

        parsed_date = None
        supported_formats = [
            '%m/%d/%Y %H:%M:%S',
            '%m/%d/%Y %H:%M',
            '%m/%d/%Y %I:%M:%S %p',
            '%m/%d/%Y',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
            '%d/%m/%Y %H:%M:%S',
            '%d/%m/%Y',
            '%m-%d-%Y %H:%M:%S',
            '%m-%d-%Y',
            '%Y/%m/%d %H:%M:%S',
            '%Y/%m/%d',
        ]

        for fmt in supported_formats:
            try:
                parsed_date = datetime.strptime(cleaned_value, fmt)
                break
            except ValueError:
                continue

        if parsed_date is None:
            first_token = cleaned_value.split()[0]
            if '/' in first_token:
                parts = first_token.split('/')
                if len(parts) >= 3 and parts[0].isdigit() and parts[2].isdigit():
                    month = int(parts[0])
                    year = int(parts[2])
                    if 1 <= month <= 12 and 1900 <= year <= 2100:
                        quarter = get_quarter(first_token)
                        return {"year": year, "quarter": quarter}
            elif '-' in first_token:
                parts = first_token.split('-')
                if len(parts) >= 3:
                    if len(parts[0]) == 4 and parts[0].isdigit() and parts[1].isdigit():
                        year = int(parts[0])
                        month = int(parts[1])
                    elif parts[2].isdigit() and parts[0].isdigit():
                        year = int(parts[2])
                        month = int(parts[0])
                    else:
                        return {"year": None, "quarter": "Unknown"}

                    if 1 <= month <= 12 and 1900 <= year <= 2100:
                        quarter = get_quarter(first_token)
                        return {"year": year, "quarter": quarter}

            return {"year": None, "quarter": "Unknown"}

        return {
            "year": parsed_date.year,
            "quarter": get_quarter(cleaned_value),
        }
    except Exception:
        return {"year": None, "quarter": "Unknown"}


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

    # Early reject obvious invalid values
    raw_value = level_input.strip()
    if not raw_value:
        return ""
    if "@" in raw_value:
        return ""

    # Normalize unicode and clean symbols (handles styled text like 𝑫𝑰𝑷𝑳𝑶𝑴𝑨)
    normalized = unicodedata.normalize("NFKD", raw_value)
    normalized = normalized.encode("ascii", "ignore").decode("ascii")
    cleaned = normalized.upper().strip()
    cleaned = cleaned.replace("LEVEL", " ").replace("OF TRAINING", " ")
    cleaned = re.sub(r"[^A-Z0-9\s]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    if not cleaned:
        return ""

    # Remove known noisy placeholders
    invalid_values = {
        "N A", "NA", "NIL", "NONE", "NULL", "UNKNOWN", "Z", "B", "KI", "FOUR", "THIRD YEAR"
    }
    if cleaned in invalid_values:
        return ""

    # Direct category names
    if cleaned in EDUCATION_LEVELS.keys():
        return cleaned

    # Level number mapping (Kenyan framework)
    level_match = re.search(r"\bL?\s*([4-9])\b", cleaned)
    if level_match:
        level_number = level_match.group(1)
        if level_number == "4":
            return "CERTIFICATE"
        if level_number in {"5", "6"}:
            return "DIPLOMA"
        if level_number == "7":
            return "DEGREE"
        if level_number == "8":
            return "MASTERS"
        if level_number == "9":
            return "PHD"

    # Common keyword-based mapping
    if any(token in cleaned for token in ["CERT", "ARTISAN", "CRAFIT", "CRAFT", "GRADE", "TRADE TEST", "GRADE THREE", "GRADE 3", "GRADE2", "GRADE 2", "GRADE1", "GRADE 1"]):
        return "CERTIFICATE"

    if any(token in cleaned for token in ["DIP", "DIPL", "DEPLOMA", "DOPLOMA", "DEPL"]):
        return "DIPLOMA"

    if any(token in cleaned for token in ["DEG", "BACHELOR", "UNDERGRAD", "BTECH", "BSC", "BA ", "B A "]):
        return "DEGREE"

    if any(token in cleaned for token in ["MAST", "POSTGRAD", "MSC", "MBA", "M A", "MSC"]):
        return "MASTERS"

    if any(token in cleaned for token in ["PHD", "DOCTOR", "DOCTORATE"]):
        return "PHD"

    # Fuzzy correction for common misspellings (certificate/diploma/degree/etc.)
    words = cleaned.split()
    candidate_tokens = words + [cleaned]
    vocabulary = [
        "CERTIFICATE", "DIPLOMA", "DEGREE", "MASTERS", "PHD",
        "CERT", "DIP", "DEG", "ARTISAN"
    ]

    for token in candidate_tokens:
        match = get_close_matches(token, vocabulary, n=1, cutoff=0.75)
        if not match:
            continue

        matched = match[0]
        if matched in {"CERTIFICATE", "CERT", "ARTISAN"}:
            return "CERTIFICATE"
        if matched in {"DIPLOMA", "DIP"}:
            return "DIPLOMA"
        if matched in {"DEGREE", "DEG"}:
            return "DEGREE"
        if matched == "MASTERS":
            return "MASTERS"
        if matched == "PHD":
            return "PHD"

    # If value is not confidently classifiable, drop it to keep charts clean
    return ""


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


def normalize_school_name(school_input: str) -> str:
    """
    Normalize school names for consistency
    """
    if not school_input or not isinstance(school_input, str):
        return ""
    
    # Clean the input
    cleaned = school_input.strip()
    
    # Convert to uppercase for consistency
    cleaned_upper = cleaned.upper()
    
    # Common school abbreviations and variations
    school_mappings = {
        "UON": "UNIVERSITY OF NAIROBI",
        "U.O.N": "UNIVERSITY OF NAIROBI",
        "NAIROBI UNIVERSITY": "UNIVERSITY OF NAIROBI",
        "KU": "KENYATTA UNIVERSITY",
        "K.U": "KENYATTA UNIVERSITY",
        "MOI UNIVERSITY": "MOI UNIVERSITY",
        "JKUAT": "JOMO KENYATTA UNIVERSITY OF AGRICULTURE AND TECHNOLOGY",
        "J.K.U.A.T": "JOMO KENYATTA UNIVERSITY OF AGRICULTURE AND TECHNOLOGY",
        "JKUAT": "JOMO KENYATTA UNIVERSITY OF AGRICULTURE AND TECHNOLOGY",
        "EGERTON": "EGERTON UNIVERSITY",
        "EGERTON UNIVERSITY": "EGERTON UNIVERSITY",
        "STRATHMORE": "STRATHMORE UNIVERSITY",
        "STRATHMORE UNIVERSITY": "STRATHMORE UNIVERSITY",
        "USIU": "UNITED STATES INTERNATIONAL UNIVERSITY",
        "USIU-AFRICA": "UNITED STATES INTERNATIONAL UNIVERSITY",
        "KCA": "KCA UNIVERSITY",
        "KCA UNIVERSITY": "KCA UNIVERSITY",
        "MULTIMEDIA UNIVERSITY": "MULTIMEDIA UNIVERSITY OF KENYA",
        "MMU": "MULTIMEDIA UNIVERSITY OF KENYA",
        "MOUNT KENYA UNIVERSITY": "MOUNT KENYA UNIVERSITY",
        "MKU": "MOUNT KENYA UNIVERSITY",
        "TECHNICAL UNIVERSITY OF KENYA": "TECHNICAL UNIVERSITY OF KENYA",
        "TUK": "TECHNICAL UNIVERSITY OF KENYA",
        "KENYA POLYTECHNIC": "TECHNICAL UNIVERSITY OF KENYA",
        "KABETE NATIONAL POLYTECHNIC": "KABETE NATIONAL POLYTECHNIC",
        "KABETE POLY": "KABETE NATIONAL POLYTECHNIC",
        "MOMBASA POLYTECHNIC": "MOMBASA POLYTECHNIC UNIVERSITY COLLEGE",
        "MPC": "MOMBASA POLYTECHNIC UNIVERSITY COLLEGE",
    }
    
    # Check for exact mapping
    if cleaned_upper in school_mappings:
        return school_mappings[cleaned_upper]
    
    # Check for partial matches for universities
    for abbr, full_name in school_mappings.items():
        if abbr in cleaned_upper:
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
                
                # Normalize school name
                if "The name of your school" in record:
                    record["The name of your school"] = normalize_school_name(record["The name of your school"])
                
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
            "schools": "/schools",
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
            "courses": "Course names are converted to title case",
            "schools": "School names are normalized for consistency"
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
async def get_stats(
    county: Optional[str] = Query(None),
    level: Optional[str] = Query(None),
    school: Optional[str] = Query(None)
):
    """
    Get aggregated statistics from the sheet
    
    Query Parameters:
    - **county**: Filter by county (optional)
    - **level**: Filter by level of training (optional)
    - **school**: Filter by institution/school (optional)
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
        if school:
            normalized_school = normalize_school_name(school)
            records = [
                r for r in records
                if r.get("The name of your school", "") == normalized_school
            ]
        
        if not records:
            return {
                "total_registrations": 0,
                "placement_rate": 0,
                "gender_ratio": {},
                "education_breakdown": {},
                "top_courses": [],
                "geographic_distribution": [],
                "preferred_companies": [],
                "top_schools": [],
                "filtered": bool(county or level or school),
                "timestamp": datetime.now().isoformat()
            }
        
        # Calculate statistics
        stats = calculate_statistics(records)
        stats["filtered"] = bool(county or level or school)
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


@app.get("/schools")
async def get_schools():
    """Get list of all unique schools"""
    try:
        client = get_sheets_client()
        records = client.fetch_all_records()
        
        # Get all schools from the data
        schools_in_data = set(r.get("The name of your school", "").strip() for r in records if r.get("The name of your school", "").strip())
        schools = sorted(schools_in_data)
        
        return {
            "schools": schools,
            "total": len(schools)
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
    education_levels = [
        r.get("Your Level of Training (e.g. Deg, Dip, Cert)", "").strip()
        for r in records
        if r.get("Your Level of Training (e.g. Deg, Dip, Cert)")
        and r.get("Your Level of Training (e.g. Deg, Dip, Cert)", "").strip() in EDUCATION_LEVELS.keys()
    ]
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
    
    # Top 10 schools
    schools = [r.get("The name of your school", "").strip() for r in records if r.get("The name of your school", "").strip()]
    school_counter = Counter(schools)
    top_schools = [
        {"name": school, "count": count}
        for school, count in school_counter.most_common(10)
    ]
    
    # Quarter breakdown - extract from application timestamp/date column
    quarter_counter = Counter()
    year_quarter_counter = Counter()

    # Pick the best date/time field by parsing success rate in a sample of records
    all_keys = list(records[0].keys())
    candidate_fields = [
        key for key in all_keys
        if any(token in key.lower() for token in [
            'timestamp', 'time', 'date', 'appl', 'submit', 'created'
        ])
    ]

    # Some sheets use short headers (e.g., "F") for timestamp column
    if 'F' in all_keys and 'F' not in candidate_fields:
        candidate_fields.append('F')

    # Fallback to all fields if no obvious candidate exists
    if not candidate_fields:
        candidate_fields = all_keys

    sample_records = records[: min(len(records), 300)]
    timestamp_field = None
    best_score = 0

    for field in candidate_fields:
        valid_quarters = 0
        for row in sample_records:
            value = str(row.get(field, '')).strip()
            if value and get_quarter(value) != 'Unknown':
                valid_quarters += 1

        if valid_quarters > best_score:
            best_score = valid_quarters
            timestamp_field = field

    if timestamp_field:
        for r in records:
            ts = str(r.get(timestamp_field, "")).strip()
            parsed_date = parse_application_date(ts)
            quarter = parsed_date.get("quarter", "Unknown")
            year = parsed_date.get("year")
            if quarter != "Unknown":
                quarter_counter[quarter] += 1
                if year is not None:
                    year_quarter_counter[(year, quarter)] += 1

    quarter_order = ["Q1 (Jul-Sep)", "Q2 (Oct-Dec)", "Q3 (Jan-Mar)", "Q4 (Apr-Jun)"]
    quarter_total = sum(quarter_counter.values())
    quarter_breakdown = [
        {
            "quarter": quarter,
            "count": quarter_counter.get(quarter, 0),
            "percentage": round((quarter_counter.get(quarter, 0) / quarter_total) * 100, 2) if quarter_total else 0
        }
        for quarter in quarter_order
    ]

    years = sorted({year for year, _ in year_quarter_counter.keys()})
    quarter_breakdown_by_year = [
        {
            "year": year,
            "quarters": [
                {
                    "quarter": quarter,
                    "count": year_quarter_counter.get((year, quarter), 0)
                }
                for quarter in quarter_order
            ]
        }
        for year in years
    ]
    
    return {
        "total_registrations": total_registrations,
        "placement_rate": placement_rate,
        "gender_ratio": gender_ratio,
        "education_breakdown": education_breakdown,
        "top_courses": top_courses,
        "geographic_distribution": geographic_distribution,
        "preferred_companies": preferred_companies,
        "top_schools": top_schools,
        "quarter_breakdown": quarter_breakdown,
        "quarter_breakdown_by_year": quarter_breakdown_by_year
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
