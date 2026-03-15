from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
from bson import ObjectId
from datetime import date, datetime, time

class JobType(str, Enum):
    FULL_TIME = "FULL-TIME"
    PART_TIME = "PART-TIME"
    CONTRACT = "CONTRACT"
    TEMPORARY = "TEMPORARY"
    INTERN = "INTERN"
    VOLUNTEER = "VOLUNTEER"
    OTHER = "OTHER"

class expectedSalary(str, Enum):
    ZERO_TO_30K = "0-30K"
    THIRTYK_TO_60K = "30K-60K"
    SIXTYK_TO_100K = "60K-100K"
    ONE_HUNDRED_K_TO_150K = "100K-150K"
    ONE_FIFTY_K_TO_200K = "150K-200K"
    TWO_HUNDRED_K_PLUS = "200K+"

class industry(str, Enum):
    TECH = "Tech"
    FINANCE = "Finance"
    HEALTHCARE = "Healthcare"
    EDUCATION = "Education"
    MANUFACTURING = "Manufacturing"
    RETAIL = "Retail"
    OTHER = "Other"

class experienceLevel(str, Enum):
    ENTRY_LEVEL = "Entry-Level"
    MID_LEVEL = "Mid-Level"
    SENIOR_LEVEL = "Senior-Level"
    MANAGER = "Manager"
    DIRECTOR = "Director"
    EXECUTIVE = "Executive"

class remote(str, Enum):
    REMOTE = "Remote"
    ON_SITE = "On-Site"
    HYBRID = "Hybrid"

class companySize(str, Enum):
    ONE_TO_10 = "1-10"
    ELEVEN_TO_50 = "11-50"
    FIFTY_ONE_TO_200 = "51-200"
    TWO_HUNDRED_ONE_TO_500 = "201-500"
    FIVE_HUNDRED_ONE_TO_1000 = "501-1000"
    ONE_THOUSAND_PLUS = "1000+"

class UserScheme(BaseModel):
    #This should not be Optional after development
    username: Optional[str] = None
    #This should not be Optional after development
    passwordHash: Optional[str] = None
    locationConfig: Optional[List[str]] = []
    expectedSalaryConfig: Optional[List[expectedSalary]] = []
    jobTypeConfig: Optional[List[JobType]] = []
    industryConfig: Optional[List[industry]] = []
    experienceLevelConfig: Optional[List[experienceLevel]] = []
    remoteConfig: Optional[List[remote]] = []
    companySizeConfig: Optional[List[companySize]] = []
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

class ResumeScheme(BaseModel):
    #This should not be Optional after development
    filename: Optional[str] = None
    #This should not be Optional after development
    userId: Optional[ObjectId] = None
    #This should not be Optional after development
    data: Optional[bytes] = None
    uploadDate: Optional[date] = None
    #This should not be Optional after development
    isActive: Optional[bool] = None
    tags: Optional[List[str]] = []
    extractedKeywords: Optional[List[str]] = []
    atsScore: Optional[int] = None

class JobPostingScheme(BaseModel):
    #This should not be Optional after development
    title: Optional[str] = None
    datePosted: Optional[date] = None
    #This should not be Optional after development
    dateExtracted: Optional[datetime] = None
    dateExpiring: Optional[date] = None
    #This should not be Optional after development
    domain: Optional[str] = None
    company: Optional[str] = None
    locationC: Optional[List[str]] = []
    salaryRangeC: Optional[expectedSalary] = None
    jobTypeC: Optional[List[JobType]] = []
    industryC: Optional[List[industry]] = []
    experienceLevelC: Optional[List[experienceLevel]] = []
    remoteC: Optional[List[remote]] = []
    companySizeC: Optional[companySize] = None
    #This should not be Optional after development
    text: Optional[str] = None
    #This should not be Optional after development
    url: Optional[str] = None
    keywords: Optional[List[str]] = []

