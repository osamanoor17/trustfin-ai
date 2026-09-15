"""Document metadata schema for the TrustFin AI research corpus."""

import re
from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class DocumentType(str, Enum):
    """Formal taxonomy of target document categories."""

    REGULATION = "REGULATION"
    CIRCULAR = "CIRCULAR"
    PRUDENTIAL_REGULATION = "PRUDENTIAL_REGULATION"
    CONSUMER_GUIDANCE = "CONSUMER_GUIDANCE"
    ANNUAL_REPORT = "ANNUAL_REPORT"
    FINANCIAL_STATEMENT = "FINANCIAL_STATEMENT"
    MONETARY_POLICY = "MONETARY_POLICY"
    PAYMENT_SYSTEM_REPORT = "PAYMENT_SYSTEM_REPORT"
    BANKING_STATISTICS = "BANKING_STATISTICS"
    DIGITAL_BANKING_POLICY = "DIGITAL_BANKING_POLICY"
    AML_KYC_GUIDANCE = "AML_KYC_GUIDANCE"
    FINTECH_REGULATION = "FINTECH_REGULATION"
    PRODUCT_INFORMATION = "PRODUCT_INFORMATION"
    FEE_SCHEDULE = "FEE_SCHEDULE"
    TERMS_AND_CONDITIONS = "TERMS_AND_CONDITIONS"
    PUBLIC_DISCLOSURE = "PUBLIC_DISCLOSURE"


class InstitutionType(str, Enum):
    """Categories of issuing financial entities."""

    CENTRAL_BANK_REGULATOR = "CENTRAL_BANK_REGULATOR"
    COMMERCIAL_BANK = "COMMERCIAL_BANK"
    ISLAMIC_BANK = "ISLAMIC_BANK"
    DIGITAL_BANK = "DIGITAL_BANK"
    ELECTRONIC_MONEY_INSTITUTION = "ELECTRONIC_MONEY_INSTITUTION"
    PAYMENT_SERVICE_PROVIDER = "PAYMENT_SERVICE_PROVIDER"
    MICROFINANCE_BANK = "MICROFINANCE_BANK"
    GOVERNMENT_FINANCIAL_AUTHORITY = "GOVERNMENT_FINANCIAL_AUTHORITY"
    INTERNATIONAL_FINANCIAL_INSTITUTION = "INTERNATIONAL_FINANCIAL_INSTITUTION"


class SourceTier(str, Enum):
    """Source authority hierarchy for provenance tracking."""

    TIER_1 = "TIER_1"  # Official central bank, regulator, government
    TIER_2 = "TIER_2"  # Official regulated financial institution
    TIER_3 = "TIER_3"  # Recognized international financial institution
    TIER_4 = "TIER_4"  # Secondary source / verified industry body


class LanguageCode(str, Enum):
    """Supported language codes for document classification."""

    EN = "en"
    UR = "ur"
    ROMAN_UR = "roman-ur"
    MUL = "mul"  # Multilingual / mixed


class ScriptType(str, Enum):
    """Supported script classifications."""

    LATN = "Latn"
    ARAB = "Arab"
    MIXED = "mixed"


class DocumentMetadata(BaseModel):
    """Extensible metadata schema representing a single corpus document."""

    model_config = ConfigDict(extra="ignore", use_enum_values=False)

    # Core Identifiers
    document_id: str = Field(
        ...,
        description="Deterministic identifier: [COUNTRY]-[INSTITUTION]-[DOCTYPE]-[YEAR]-[SEQ]",
        examples=["PK-SBP-CIR-2023-0001"],
    )
    title: str = Field(..., min_length=3, description="Official title of the document")
    file_name: str = Field(..., min_length=1, description="Original or standardized filename")

    # Issuing Entity & Provenance
    institution: str = Field(..., description="Issuing entity name (e.g. State Bank of Pakistan)")
    institution_type: InstitutionType = Field(..., description="Classification of the issuing entity")
    country: str = Field(default="PK", min_length=2, max_length=2, description="ISO 3166-1 alpha-2 country code")
    jurisdiction: str = Field(default="Pakistan", description="Legal jurisdiction governing the document")
    source_tier: SourceTier = Field(..., description="Authority tier in provenance hierarchy")
    source_url: HttpUrl = Field(..., description="Canonical source URL where document was published")

    # Document Classification
    document_type: DocumentType = Field(..., description="Functional category of the document")
    language: LanguageCode = Field(default=LanguageCode.EN, description="Primary language of the document")
    script: ScriptType = Field(default=ScriptType.LATN, description="Primary script representation")

    # Temporal Attributes
    publication_date: Optional[date] = Field(default=None, description="Official publication date")
    effective_date: Optional[date] = Field(default=None, description="Date document becomes legally active")
    retrieval_date: date = Field(default_factory=date.today, description="Date retrieved and archived")

    # Physical / Technical Characteristics
    mime_type: str = Field(default="application/pdf", description="MIME type of the source artifact")
    file_size_bytes: Optional[int] = Field(default=None, ge=0, description="Size of the raw binary in bytes")
    page_count: Optional[int] = Field(default=None, ge=1, description="Number of pages in the document")
    sha256: Optional[str] = Field(
        default=None,
        description="SHA-256 cryptographic hash of raw binary (64 hex characters)",
    )
    is_scanned: Optional[bool] = Field(default=None, description="Whether document is a scanned image/raster PDF")
    has_tables: Optional[bool] = Field(default=None, description="Whether document contains financial tables")
    has_images: Optional[bool] = Field(default=None, description="Whether document contains non-text illustrations")

    # Versioning & Lifecycle
    version: str = Field(default="1.0", description="Document revision or publication version")
    supersedes: Optional[str] = Field(default=None, description="document_id of previously superseded regulation")
    license_or_usage_note: Optional[str] = Field(
        default=None,
        description="Public domain or fair use research terms note",
    )
    notes: Optional[str] = Field(default=None, description="Additional annotation or research context")

    @field_validator("document_id")
    @classmethod
    def validate_document_id(cls, v: str) -> str:
        """Validate deterministic document_id format."""
        pattern = r"^[A-Z]{2}-[A-Z0-9]+-[A-Z0-9_]+-\d{4}-[A-Z0-9]+$"
        if not re.match(pattern, v):
            raise ValueError(
                f"document_id '{v}' does not match expected convention: [COUNTRY]-[INSTITUTION]-[DOCTYPE]-[YEAR]-[SEQ] (e.g. PK-SBP-CIR-2023-0001)"
            )
        return v

    @field_validator("sha256")
    @classmethod
    def validate_sha256(cls, v: Optional[str]) -> Optional[str]:
        """Validate SHA-256 checksum format if provided."""
        if v is not None:
            if not re.match(r"^[a-fA-F0-9]{64}$", v):
                raise ValueError("sha256 must be a 64-character hexadecimal string")
            return v.lower()
        return v
