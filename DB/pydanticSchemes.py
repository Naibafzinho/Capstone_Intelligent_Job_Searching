from pydantic import BaseModel, ConfigDict, field_validator
from typing import List, Optional
from enum import Enum
from bson import ObjectId

class JobType(str, Enum):
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    CONTRACT = "contract"
    TEMPORARY = "temporary"
    INTERN = "intern"
    VOLUNTEER = "volunteer"
    OTHER = "other"

class expectedSalary(str, Enum):
    ZERO_TO_30K = "0-30k"
    THIRTYK_TO_60K = "30k-60k"
    SIXTYK_TO_100K = "60k-100k"
    ONE_HUNDRED_K_TO_150K = "100k-150k"
    ONE_FIFTY_K_TO_200K = "150k-200k"
    TWO_HUNDRED_K_PLUS = "200k+"

class industry(str, Enum):
    TECH = "tech"
    FINANCE = "finance"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    MANUFACTURING = "manufacturing"
    RETAIL = "retail"
    OTHER = "other"

class experienceLevel(str, Enum):
    ENTRY_LEVEL = "entry-level"
    MID_LEVEL = "mid-level"
    SENIOR_LEVEL = "senior-level"
    MANAGER = "manager"
    DIRECTOR = "director"
    EXECUTIVE = "executive"

class remote(str, Enum):
    REMOTE = "remote"
    ON_SITE = "on-site"
    HYBRID = "hybrid"

class companySize(str, Enum):
    ONE_TO_10 = "1-10"
    ELEVEN_TO_50 = "11-50"
    FIFTY_ONE_TO_200 = "51-200"
    TWO_HUNDRED_ONE_TO_500 = "201-500"
    FIVE_HUNDRED_ONE_TO_1000 = "501-1000"
    ONE_THOUSAND_ONE_TO_5000 = "1001-5000"
    FIVE_THOUSAND_ONE_TO_10000 = "5001-10000"
    TEN_THOUSAND_PLUS = "10000+"


class UserScheme(BaseModel):
    username: str
    passwordHash: str
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

    @field_validator(
        'locationConfig', 
        'jobTypeConfig', 
        'industryConfig',
        'experienceLevelConfig',
        'remoteConfig',
        'companySizeConfig',
        'email',
        mode='before'
    )
    @classmethod
    def normalize_enums(cls, v):
        if isinstance(v, list):
            return [item.upper() if isinstance(item, str) else item for item in v]
        return v

class ResumeScheme(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    filename: str
    userId: ObjectId
    data: bytes
    uploadDate: str
    isActive: bool
    tags: Optional[List[str]] = []
    extractedKeywords: Optional[List[str]] = []
    atsScore: Optional[int] = None

    @field_validator(
        'tags', 
        'extractedKeywords',
        mode='before'
    )
    @classmethod
    def normalize_enums(cls, v):
        if isinstance(v, list):
            return [item.upper() if isinstance(item, str) else item for item in v]
        return v

class JobPostingScheme(BaseModel):
    title: str
    datePosted: Optional[str] = None
    dateExtracted: str
    dateExpiring: Optional[str] = None
    domain: str
    company: Optional[str] = None
    locationC: Optional[List[str]] = []
    salaryRangeC: Optional[List[expectedSalary]] = None
    jobTypeC: Optional[List[JobType]] = []
    industryC: Optional[List[industry]] = []
    experienceLevelC: Optional[List[experienceLevel]] = []
    remoteC: Optional[List[remote]] = []
    companySizeC: Optional[companySize] = None
    text: str
    url: str
    keywords: Optional[List[str]] = []

    @field_validator(
        'company',
        'locationC', 
        'jobTypeC', 
        'industryC',
        'experienceLevelC',
        'remoteC',
        'companySizeC',
        'keywords',
        mode='before'
    )
    @classmethod
    def normalize_enums(cls, v):
        if isinstance(v, list):
            return [item.upper() if isinstance(item, str) else item for item in v]
        return v

