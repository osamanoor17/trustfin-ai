"""Unit tests for the DocumentMetadata Pydantic schema."""

from datetime import date
import pytest
from pydantic import ValidationError

from app.schemas.document import (
    DocumentMetadata,
    DocumentType,
    InstitutionType,
    LanguageCode,
    ScriptType,
    SourceTier,
)


def test_valid_minimal_document_metadata():
    """Verify that DocumentMetadata succeeds with only required fields and defaults."""
    doc = DocumentMetadata(
        document_id="PK-SBP-CIR-2023-0001",
        title="Circular on Digital Banking Framework",
        file_name="sbp_circular_2023_01.pdf",
        institution="State Bank of Pakistan",
        institution_type=InstitutionType.CENTRAL_BANK_REGULATOR,
        source_tier=SourceTier.TIER_1,
        source_url="https://www.sbp.org.pk/circulars/2023/c1.pdf",
        document_type=DocumentType.CIRCULAR,
    )

    assert doc.document_id == "PK-SBP-CIR-2023-0001"
    assert doc.country == "PK"
    assert doc.jurisdiction == "Pakistan"
    assert doc.language == LanguageCode.EN
    assert doc.script == ScriptType.LATN
    assert doc.retrieval_date == date.today()
    assert doc.version == "1.0"
    assert doc.publication_date is None
    assert doc.effective_date is None
    assert doc.sha256 is None
    assert doc.page_count is None


def test_valid_rich_document_metadata():
    """Verify that DocumentMetadata handles all optional and detailed fields correctly."""
    sample_sha256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    doc = DocumentMetadata(
        document_id="PK-HBL-SOC-2024-0002",
        title="Schedule of Bank Charges July-Dec 2024",
        file_name="hbl_soc_2024_jul_dec.pdf",
        institution="Habib Bank Limited",
        institution_type=InstitutionType.COMMERCIAL_BANK,
        country="PK",
        jurisdiction="Pakistan",
        source_tier=SourceTier.TIER_2,
        source_url="https://www.hbl.com/assets/documents/soc_2024.pdf",
        document_type=DocumentType.FEE_SCHEDULE,
        language=LanguageCode.EN,
        script=ScriptType.LATN,
        publication_date=date(2024, 6, 25),
        effective_date=date(2024, 7, 1),
        retrieval_date=date(2024, 7, 5),
        mime_type="application/pdf",
        file_size_bytes=1048576,
        page_count=32,
        sha256=sample_sha256,
        is_scanned=False,
        has_tables=True,
        has_images=False,
        version="2.0",
        supersedes="PK-HBL-SOC-2024-0001",
        license_or_usage_note="Public consumer disclosure tariff",
        notes="Contains commercial banking tariffs for individual accounts",
    )

    assert doc.document_id == "PK-HBL-SOC-2024-0002"
    assert doc.institution_type == InstitutionType.COMMERCIAL_BANK
    assert doc.source_tier == SourceTier.TIER_2
    assert doc.document_type == DocumentType.FEE_SCHEDULE
    assert doc.page_count == 32
    assert doc.has_tables is True
    assert doc.supersedes == "PK-HBL-SOC-2024-0001"
    assert doc.sha256 == sample_sha256


def test_invalid_source_url():
    """Verify that invalid URL formats are rejected."""
    with pytest.raises(ValidationError) as exc_info:
        DocumentMetadata(
            document_id="PK-SBP-REG-2023-0001",
            title="Invalid URL Document",
            file_name="doc.pdf",
            institution="State Bank of Pakistan",
            institution_type=InstitutionType.CENTRAL_BANK_REGULATOR,
            source_tier=SourceTier.TIER_1,
            source_url="not-a-valid-url",
            document_type=DocumentType.REGULATION,
        )
    assert "source_url" in str(exc_info.value)


def test_invalid_enum_values():
    """Verify that unsupported document types or institution types are rejected."""
    with pytest.raises(ValidationError) as exc_info:
        DocumentMetadata(
            document_id="PK-SBP-REG-2023-0001",
            title="Invalid Enum Test",
            file_name="doc.pdf",
            institution="State Bank of Pakistan",
            institution_type="NON_EXISTENT_INSTITUTION",  # Invalid
            source_tier=SourceTier.TIER_1,
            source_url="https://www.sbp.org.pk/doc.pdf",
            document_type=DocumentType.REGULATION,
        )
    assert "institution_type" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        DocumentMetadata(
            document_id="PK-SBP-REG-2023-0001",
            title="Invalid Enum Test",
            file_name="doc.pdf",
            institution="State Bank of Pakistan",
            institution_type=InstitutionType.CENTRAL_BANK_REGULATOR,
            source_tier="NON_EXISTENT_TIER",  # Invalid
            source_url="https://www.sbp.org.pk/doc.pdf",
            document_type=DocumentType.REGULATION,
        )
    assert "source_tier" in str(exc_info.value)


def test_invalid_document_id_convention():
    """Verify that malformed document_id patterns are rejected."""
    with pytest.raises(ValidationError) as exc_info:
        DocumentMetadata(
            document_id="invalid-id-format",  # Does not conform to [COUNTRY]-[INSTITUTION]-[DOCTYPE]-[YEAR]-[SEQ]
            title="Bad ID Doc",
            file_name="doc.pdf",
            institution="State Bank of Pakistan",
            institution_type=InstitutionType.CENTRAL_BANK_REGULATOR,
            source_tier=SourceTier.TIER_1,
            source_url="https://www.sbp.org.pk/doc.pdf",
            document_type=DocumentType.REGULATION,
        )
    assert "document_id" in str(exc_info.value)


def test_invalid_sha256_format():
    """Verify that non-hexadecimal or wrong-length sha256 strings are rejected."""
    with pytest.raises(ValidationError) as exc_info:
        DocumentMetadata(
            document_id="PK-SBP-REG-2023-0001",
            title="Bad SHA256 Doc",
            file_name="doc.pdf",
            institution="State Bank of Pakistan",
            institution_type=InstitutionType.CENTRAL_BANK_REGULATOR,
            source_tier=SourceTier.TIER_1,
            source_url="https://www.sbp.org.pk/doc.pdf",
            document_type=DocumentType.REGULATION,
            sha256="not-a-64-char-hex",  # Invalid
        )
    assert "sha256" in str(exc_info.value)


def test_json_serialization_roundtrip():
    """Verify that DocumentMetadata serializes to and deserializes from JSON cleanly."""
    doc = DocumentMetadata(
        document_id="PK-SBP-CIR-2023-0005",
        title="Payment Systems Regulation Circular",
        file_name="circ_05.pdf",
        institution="State Bank of Pakistan",
        institution_type=InstitutionType.CENTRAL_BANK_REGULATOR,
        source_tier=SourceTier.TIER_1,
        source_url="https://www.sbp.org.pk/circulars/2023/circ_05.pdf",
        document_type=DocumentType.CIRCULAR,
        publication_date=date(2023, 5, 10),
        page_count=12,
    )

    json_str = doc.model_dump_json()
    assert "PK-SBP-CIR-2023-0005" in json_str
    assert "CIRCULAR" in json_str

    # Deserialization check
    parsed = DocumentMetadata.model_validate_json(json_str)
    assert parsed.document_id == doc.document_id
    assert parsed.publication_date == date(2023, 5, 10)
    assert parsed.page_count == 12
    assert str(parsed.source_url) == "https://www.sbp.org.pk/circulars/2023/circ_05.pdf"
