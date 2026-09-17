"""Unit tests for Phase 1B.3 / Phase 1B.3A document acquisition and semantic identity verification logic."""

from pathlib import Path
import tempfile
import pytest

from scripts.acquire_documents import (
    acquire_single_document,
    compute_sha256,
    is_approved_domain,
    is_valid_pdf_magic_bytes,
    sanitize_filename,
    verify_document_identity,
)


def test_approved_domain_validation():
    """Verify that only official SBP domains pass domain validation."""
    assert is_approved_domain("https://www.sbp.org.pk/circulars/c2022.pdf") is True
    assert is_approved_domain("https://sbp.org.pk/bprd/2025/C1.htm") is True
    assert is_approved_domain("https://archive.sbp.org.pk/publications/report.pdf") is True

    # Rejected domains
    assert is_approved_domain("https://scribd.com/doc/sbp-report.pdf") is False
    assert is_approved_domain("https://example.com/sbp.pdf") is False
    assert is_approved_domain("https://malicious-sbp.org.pk.evil.com/doc.pdf") is False
    assert is_approved_domain("invalid-url-string") is False


def test_filename_sanitization():
    """Verify filename sanitization prevents path traversal and invalid characters."""
    assert sanitize_filename("normal_file.pdf") == "normal_file.pdf"
    assert sanitize_filename("../../etc/passwd") == "passwd"
    assert sanitize_filename("C:\\Windows\\System32\\cmd.exe") == "cmd.exe"
    assert sanitize_filename("BPRD Circular #1 (2025).pdf") == "bprd_circular__1__2025_.pdf"


def test_pdf_magic_bytes_validation():
    """Verify detection of standard PDF header signature."""
    assert is_valid_pdf_magic_bytes(b"%PDF-1.4\n1 0 obj...") is True
    assert is_valid_pdf_magic_bytes(b"%PDF-1.7\r\n...") is True
    assert is_valid_pdf_magic_bytes(b"<html><head><title>Error</title></head>") is False
    assert is_valid_pdf_magic_bytes(b"PK\x03\x04") is False  # Zip file
    assert is_valid_pdf_magic_bytes(b"") is False


def test_sha256_computation(tmp_path: Path):
    """Verify SHA-256 calculation accuracy on known binary content."""
    test_file = tmp_path / "specimen.bin"
    test_content = b"TrustFin AI Research Binary Specimen 2026"
    test_file.write_bytes(test_content)

    digest = compute_sha256(test_file)
    assert len(digest) == 64
    assert digest == digest.lower()
    import hashlib
    expected = hashlib.sha256(test_content).hexdigest().lower()
    assert digest == expected


def test_semantic_identity_mismatch_detection(tmp_path: Path):
    """Verify that verify_document_identity flags semantic mismatch (e.g. NPSS vs Sandbox)."""
    # Create a specimen PDF containing NPSS metadata
    specimen_pdf = tmp_path / "npss_specimen.pdf"
    npss_content = (
        b"%PDF-1.7\n1 0 obj\n<< /Title (National Payment Systems Strategy) /Subject (NPSS) >>\nendobj\n"
        b"stream\nBT /F1 12 Tf (National Payment Systems Strategy November 2019) Tj ET\nendstream\n"
    )
    specimen_pdf.write_bytes(npss_content)

    sandbox_candidate = {
        "document_id": "PK-SBP-FINTECH_REGULATION-2025-0001",
        "title": "Guidelines for Regulatory Sandbox",
        "resolved_document_url": "https://www.sbp.org.pk/assets/document/NPSS.pdf",
    }

    is_ok, reason = verify_document_identity(specimen_pdf, sandbox_candidate)
    assert is_ok is False
    assert "Semantic mismatch" in reason
    assert "National Payment Systems Strategy" in reason


def test_semantic_identity_verification_success(tmp_path: Path):
    """Verify that verify_document_identity succeeds for matching metadata."""
    specimen_pdf = tmp_path / "onboarding_amendment.pdf"
    onboarding_content = (
        b"%PDF-1.4\n1 0 obj\n<< /Author (Shahzeb Saleem Shaikh BPRD) >>\nendobj\n"
        b"stream\nBT (BPRD Circular Letter No. 09 of 2026 Onboarding Roshan Digital Account) Tj ET\nendstream\n"
    )
    specimen_pdf.write_bytes(onboarding_content)

    onboarding_candidate = {
        "document_id": "PK-SBP-AML_KYC_GUIDANCE-2026-0001",
        "title": "Amendments to Consolidated Customer Onboarding Framework",
        "resolved_document_url": "https://www.sbp.org.pk/assets/documents/circulars/BPRD-2026-CL9-Annex.pdf",
    }

    is_ok, reason = verify_document_identity(specimen_pdf, onboarding_candidate)
    assert is_ok is True
    assert "Identity verified" in reason


def test_unapproved_domain_rejection(tmp_path: Path):
    """Verify acquire_single_document rejects candidates with unapproved host URLs."""
    unapproved_candidate = {
        "document_id": "PK-SBP-TEST-2026-0001",
        "title": "Unapproved Third Party Document",
        "file_name": "test.pdf",
        "source_url": "https://unapproved-third-party.com/fake.pdf",
        "landing_page_url": "https://unapproved-third-party.com/fake.html",
    }

    result = acquire_single_document(unapproved_candidate, tmp_path)
    assert result["acquisition_status"] == "FAILED_DOMAIN_VALIDATION"
    assert "not in approved SBP allowlist" in result["failure_reason"]


def test_duplicate_identical_handling(tmp_path: Path):
    """Verify safe duplicate detection when identical SHA-256 file exists in raw storage."""
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()

    target_filename = "pk-sbp-digital_banking_policy-2022-0001.pdf"
    existing_file = raw_dir / target_filename
    pdf_content = (
        b"%PDF-1.5\n1 0 obj\n<< /Author (BPRD SBP) >>\nendobj\n"
        b"stream\nBT (Digital Banking Policy 2022) Tj ET\nendstream\n"
    )
    existing_file.write_bytes(pdf_content)

    candidate = {
        "document_id": "PK-SBP-DIGITAL_BANKING_POLICY-2022-0001",
        "title": "Licensing and Regulatory Framework for Digital Banks",
        "file_name": target_filename,
        "source_url": "https://www.sbp.org.pk/circulars/bprd-circular-no-01-of-2022.pdf",
    }

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp_path_file = Path(tmp.name)
        tmp_path_file.write_bytes(pdf_content)

    expected_sha = compute_sha256(existing_file)
    assert compute_sha256(tmp_path_file) == expected_sha
    assert existing_file.exists()
    tmp_path_file.unlink()
