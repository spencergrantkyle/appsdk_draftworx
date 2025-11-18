"""
Pydantic models for Draftworx API data structures.
Ported from dtos.ts and draftworx-types.ts
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import IntEnum


# Enums from draftworx-types.ts
class AccountType(IntEnum):
    """Account type classification"""
    Unknown = 0
    BalanceSheet = 1
    IncomeStatement = 2


class AccountCategory(IntEnum):
    """Account category classification"""
    CostOfSales = 1
    CurrentAssets = 2
    CurrentLiabilities = 3
    Dividends = 4
    Equity = 5
    Expenses = 6
    Income = 7
    NonCurrentAssets = 8
    NonCurrentLiabilities = 9
    OtherIncome = 10
    Tax = 11
    Current = 12
    NonCurrent = 13
    DiscontinuedOperations = 14
    OtherComprehensiveIncome = 15


class AdjustmentType(IntEnum):
    """Journal entry adjustment type"""
    NormalAdjusting = 1
    Drafting = 2
    OversAndUnders = 3
    NotRecorded = 4
    StandingJournal = 5
    Interim = 6
    Budget = 7


# Helper function for adjustment type text
def get_adjustment_type_text(adjustment_type: AdjustmentType) -> str:
    """Convert AdjustmentType enum to human-readable text"""
    mapping = {
        AdjustmentType.NormalAdjusting: 'Normal Adjusting',
        AdjustmentType.Drafting: 'Drafting',
        AdjustmentType.OversAndUnders: 'Overs and Unders',
        AdjustmentType.NotRecorded: 'Not Recorded',
        AdjustmentType.StandingJournal: 'Standing Journal',
        AdjustmentType.Interim: 'Interim',
        AdjustmentType.Budget: 'Budget',
    }
    return mapping.get(adjustment_type, 'Unknown')


# DTOs for API responses
class PracticeDTO(BaseModel):
    """Practice entity with contact information"""
    id: str
    name: str
    telephone: Optional[str] = None
    mobile: Optional[str] = None
    email: str
    address1: Optional[str] = None
    address2: Optional[str] = None
    address3: Optional[str] = None
    address4: Optional[str] = None
    addressCode: Optional[str] = None


class ClientDTO(BaseModel):
    """Client entity basics"""
    id: str
    name: str
    taxYear: str


class FinancialYearDTO(BaseModel):
    """Financial year period"""
    id: str
    start: str
    end: str
    year: int
    current: bool


class AccountMappingDTO(BaseModel):
    """Account mapping details (simplified)"""
    map: Optional[str] = None
    details: Optional[str] = None
    accountType: Optional[int] = None
    accountCategory: Optional[int] = None


class TrialBalanceEntryDTO(BaseModel):
    """Trial balance entry with essential fields"""
    id: Optional[str] = None
    account: str
    name: Optional[str] = None
    leadReference: Optional[str] = None
    workingPaperReference: Optional[str] = None
    openingBalance: Optional[float] = None
    accountMapping: Optional[AccountMappingDTO] = None


class CashbookEntryLineDTO(BaseModel):
    """Individual cashbook entry line"""
    id: Optional[str] = None
    date: Optional[datetime] = None
    description: Optional[str] = None
    exclusive: Optional[float] = None
    tax: Optional[float] = None
    total: Optional[float] = None
    useTax: Optional[bool] = None
    order: Optional[int] = None
    account: str  # Formatted as "code - name"


class CashbookEntryDTO(BaseModel):
    """Cashbook entry with lines"""
    id: Optional[str] = None
    exclusive: Optional[float] = None
    tax: Optional[float] = None
    total: Optional[float] = None
    bankAccount: str  # Formatted as "code - name"
    taxAccount: Optional[str] = None  # Formatted as "code - name"
    lines: Optional[List[CashbookEntryLineDTO]] = None


class JournalEntryLineDTO(BaseModel):
    """Individual journal entry line"""
    id: Optional[str] = None
    date: Optional[datetime] = None
    amount: Optional[float] = None
    order: Optional[int] = None
    account: str  # Formatted as "code - name"


class JournalEntryDTO(BaseModel):
    """Journal entry with lines"""
    id: Optional[str] = None
    adjustmentType: str  # Human-readable text, not enum
    description: Optional[str] = None
    reference: Optional[str] = None
    number: Optional[str] = None
    status: Optional[str] = None
    exportSourceId: Optional[str] = None
    exportMessage: Optional[str] = None
    lines: Optional[List[JournalEntryLineDTO]] = None


# Input schemas for save operations
class TrialBalanceEntryInput(BaseModel):
    """Input model for saving trial balance entries"""
    account: str
    name: str
    leadReference: Optional[str] = None
    workingPaperReference: Optional[str] = None
    openingBalance: float


class CashbookEntryLineInput(BaseModel):
    """Input model for cashbook entry lines"""
    date: str
    description: str
    exclusive: float
    tax: float
    total: float
    useTax: bool
    order: int
    account: str
    sourceId: Optional[str] = None


class CashbookEntryInput(BaseModel):
    """Input model for saving cashbook entries"""
    exclusive: float
    tax: float
    total: float
    bankAccount: str
    taxAccount: Optional[str] = None
    lines: List[CashbookEntryLineInput]


class JournalEntryLineInput(BaseModel):
    """Input model for journal entry lines"""
    date: str
    amount: float
    order: int
    account: str


class JournalEntryInput(BaseModel):
    """Input model for saving journal entries"""
    adjustmentType: str = Field(
        ...,
        pattern="^(Normal Adjusting|Drafting|Overs and Unders|Not Recorded|Standing Journal|Interim|Budget)$"
    )
    description: str
    reference: Optional[str] = None
    number: Optional[str] = None
    status: Optional[str] = None
    lines: List[JournalEntryLineInput]
