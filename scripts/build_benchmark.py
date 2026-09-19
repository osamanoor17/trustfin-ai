#!/usr/bin/env python3
"""Script to generate data/benchmarks/finurdu_pilot_v0_1.jsonl deterministically."""

import json
import sys
from pathlib import Path

# Ensure app package is importable regardless of execution directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.schemas.benchmark import (
    BenchmarkAnswerability,
    BenchmarkDifficulty,
    BenchmarkLanguage,
    BenchmarkQueryType,
    BenchmarkRecord,
    BenchmarkScript,
    EvidenceSpan,
)

CONCEPTS_DATA = [
    {
        "concept_id": "DIGITAL_BANK_MINIMUM_CAPITAL_001",
        "query_type": "LIMIT_OR_THRESHOLD",
        "difficulty": "EASY",
        "answerability": "ANSWERABLE",
        "doc_id": "PK-SBP-DIGITAL_BANKING_POLICY-2022-0001",
        "page": 20,
        "span": "4.1 Digital banks shall be subject to Minimum Capital Requirement (MCR) as follows or as may be\nprescribed by SBP from time to time:\nBank\nMCR at grant of restricted\nlicense for pilot stage/ DFB\nlicense\n(PKR Billions)\nMCR at\ncommercial\nlaunch\n(PKR Billions)\nMCR during each financial year\nafter the year of commercial\nlaunch/ DFB license\n(PKR Billions)\n\nYear 1\nYear 2\nYear 3\nDRB\n1.5\n2\n2.5\n3\n4\nDFB\n6.5\nN/A\n8\n10\n-",
        "EN": "What is the Minimum Capital Requirement (MCR) specified by SBP for digital banks?",
        "UR": "اسٹیٹ بینک کی جانب سے ڈیجیٹل بینکوں کے لیے کم از کم سرمائے کی ضرورت (MCR) کیا مقرر کی گئی ہے؟",
        "RU": "State Bank ki taraf se digital banks ke liye Minimum Capital Requirement (MCR) kitna mukarrar kiya gaya hai?",
    },
    {
        "concept_id": "DIGITAL_BANK_CAR_REQUIREMENT_001",
        "query_type": "REGULATORY_REQUIREMENT",
        "difficulty": "EASY",
        "answerability": "ANSWERABLE",
        "doc_id": "PK-SBP-DIGITAL_BANKING_POLICY-2022-0001",
        "page": 26,
        "span": "Minimum CAR for a DRB shall be 15% and shall comprise the following:\na) CET1 CAR = 9.5%\nb) Total CAR = 12.50%\nc) Capital Conservation Buffer (CCB) = 2.5%",
        "EN": "What is the minimum Capital Adequacy Ratio (CAR) required for a Digital Retail Bank (DRB)?",
        "UR": "ڈیجیٹل ریٹیل بینک (DRB) کے لیے کم از کم کیپٹل ایڈیکویسی ریشو (CAR) کتنا درکار ہے؟",
        "RU": "Digital Retail Bank (DRB) ke liye kam az kam Capital Adequacy Ratio (CAR) kitna hona lazmi hai?",
    },
    {
        "concept_id": "DIGITAL_BANK_PILOT_DEPOSIT_CAP_001",
        "query_type": "LIMIT_OR_THRESHOLD",
        "difficulty": "MEDIUM",
        "answerability": "ANSWERABLE",
        "doc_id": "PK-SBP-DIGITAL_BANKING_POLICY-2022-0001",
        "page": 21,
        "span": "6.5 During the pilot stage, DRB shall be subject to an aggregate deposit cap of 25% of the MCR,\nas per the table in Regulation 4, while per depositor balance shall be capped at PKR 500,000\n(Five Hundred Thousand Rupees).",
        "EN": "What is the per-depositor balance limit during the pilot stage of a Digital Retail Bank?",
        "UR": "ڈیجیٹل ریٹیل بینک کے پائلٹ مرحلے کے دوران فی جمع کنندہ رقم کی حد کیا ہے؟",
        "RU": "Digital Retail Bank ke pilot stage ke doran per depositor balance ki maximum limit kya hai?",
    },
    {
        "concept_id": "CUSTOMER_ONBOARDING_STANDARDIZED_FORM_001",
        "query_type": "REGULATORY_REQUIREMENT",
        "difficulty": "EASY",
        "answerability": "ANSWERABLE",
        "doc_id": "PK-SBP-AML_KYC_GUIDANCE-2025-0001",
        "page": 5,
        "span": "2. Furthermore, for face-to-face onboarding, banks and MFBs shall invariably use a standardized account\nopening form for opening of Resident Pakistani Accounts. The Standardized Account Opening Form\n(SAOF) is placed at Annex-A.",
        "EN": "What account opening form must banks use for face-to-face onboarding of resident Pakistani accounts?",
        "UR": "مقیم پاکستانی اکاؤنٹس کی ان پرسن آن بورڈنگ کے لیے بینکوں کو کون سا فارم استعمال کرنا لازمی ہے؟",
        "RU": "Resident Pakistani accounts ki face-to-face onboarding ke liye banks ko konsa standardized account opening form istemal karna hota hai?",
    },
    {
        "concept_id": "CUSTOMER_ONBOARDING_FICTITIOUS_ACCOUNTS_001",
        "query_type": "REGULATORY_REQUIREMENT",
        "difficulty": "EASY",
        "answerability": "ANSWERABLE",
        "doc_id": "PK-SBP-AML_KYC_GUIDANCE-2025-0001",
        "page": 5,
        "span": "SBP REs shall not open accounts/wallets in fictitious names or numbered\naccounts.",
        "EN": "Are regulated entities allowed to open bank accounts or wallets in fictitious names or numbered accounts?",
        "UR": "کیا ریگولیٹڈ اداروں کو فرضی ناموں یا نمبر والے بینک اکاؤنٹس اور والٹس کھولنے کی اجازت ہے؟",
        "RU": "Kya regulated entities ko farzi naamo ya numbered accounts mein bank accounts ya wallets kholne ki ijazat hai?",
    },
    {
        "concept_id": "ASAAN_ACCOUNT_CREDIT_BALANCE_LIMIT_001",
        "query_type": "LIMIT_OR_THRESHOLD",
        "difficulty": "MEDIUM",
        "answerability": "ANSWERABLE",
        "doc_id": "PK-SBP-AML_KYC_GUIDANCE-2025-0001",
        "page": 18,
        "span": "2\nAsaan Account\n(Digital/\nIn-\nperson)\n\nPKR only\n\uf0b7 Resident Pakistanis\n\uf0b7 Self-declaration\nregarding\nresidency\nstatus,\nsource\nof\nincome/\nfunds\nand\nbeneficial ownership,\n\uf0b7 Restriction\nfor cross\nborder\n(outward)\ntransactions. However,\nin case of card-based\naccounts\nhaving\ninternational\nacceptance, the bank\nmay allow international\ntransactions subject to\napplicable limits.\n\uf0b7 Only one account of an\nindividual\nshall\nbe\nallowed\n\nMax\nCredit\nBalance:\nPKR 3,000,000",
        "EN": "What is the maximum credit balance allowed for an Asaan Account under SBP regulations?",
        "UR": "اسٹیٹ بینک کے قواعد کے تحت آسان اکاؤنٹ میں زیادہ سے زیادہ کریڈٹ بیلنس کی حد کیا ہے؟",
        "RU": "SBP regulations ke tehat Asaan Account mein kitni maximum credit balance ki limit di gayi hai?",
    },
    {
        "concept_id": "DIGITAL_ONBOARDING_NON_RESIDENTS_001",
        "query_type": "ELIGIBILITY",
        "difficulty": "EASY",
        "answerability": "ANSWERABLE",
        "doc_id": "PK-SBP-AML_KYC_GUIDANCE-2026-0001",
        "page": 1,
        "span": "Digital onboarding shall be allowed\nfor all residents and non-residents,\nnatural and juridical persons.",
        "EN": "Is digital onboarding permitted for non-resident individuals and entities under the updated 2026 SBP framework?",
        "UR": "کیا اسٹیٹ بینک کے 2026 کے اپ ڈیٹ شدہ فریم ورک کے تحت غیر مقیم افراد اور اداروں کے لیے ڈیجیٹل آن بورڈنگ کی اجازت ہے؟",
        "RU": "Kya SBP ke updated 2026 framework ke mutabiq non-resident individuals aur entities ke liye digital onboarding allow hai?",
    },
    {
        "concept_id": "THIRD_PARTY_KYC_RELIANCE_ROSHAN_DIGITAL_001",
        "query_type": "PROCEDURAL",
        "difficulty": "MEDIUM",
        "answerability": "ANSWERABLE",
        "doc_id": "PK-SBP-AML_KYC_GUIDANCE-2026-0001",
        "page": 2,
        "span": "For opening of accounts including Roshan Digital Accounts, REs may rely\non KYC/CDD of third party regulated financial institutions, including their\nforeign correspondent banks, parent banking company, overseas\nbranches / banking subsidiaries etc., as permissible under Regulation-3 of\nSBP’s AML/CFT/CPF Regulations.",
        "EN": "Can regulated entities rely on third-party regulated financial institutions for KYC/CDD when opening Roshan Digital Accounts?",
        "UR": "کیا روشن ڈیجیٹل اکاؤنٹ کھولتے وقت ریگولیٹڈ ادارے تھرڈ پارٹی مالیاتی اداروں کی KYC/CDD تصدیق پر انحصار کر سکتے ہیں؟",
        "RU": "Kya Roshan Digital Account kholte waqt regulated entities kisi third-party financial institution ki KYC/CDD par inhisar kar sakti hain?",
    },
    {
        "concept_id": "CONSUMER_COMPLAINT_MAJOR_TAT_001",
        "query_type": "LIMIT_OR_THRESHOLD",
        "difficulty": "MEDIUM",
        "answerability": "ANSWERABLE",
        "doc_id": "PK-SBP-CONSUMER_GUIDANCE-2025-0001",
        "page": 48,
        "span": "Any complaint that\nrequire more than 7 working days for resolution shall be treated as ‘major complaint’.",
        "EN": "How many working days are required for resolving a consumer complaint to be classified as a major complaint?",
        "UR": "صارف کی شکایت کو 'بڑی شکایت' (major complaint) شمار کرنے کے لیے حل کی کتنی ورکنگ ڈیز کی مدت درکار ہوتی ہے؟",
        "RU": "Consumer complaint ko major complaint consider karne ke liye kitne working days se zyada ka resolution timeframe chahiye hota hai?",
    },
    {
        "concept_id": "KEY_FACT_STATEMENT_REQUIREMENT_001",
        "query_type": "REGULATORY_REQUIREMENT",
        "difficulty": "EASY",
        "answerability": "ANSWERABLE",
        "doc_id": "PK-SBP-CONSUMER_GUIDANCE-2025-0001",
        "page": 20,
        "span": "FIs shall provide KFS for deposit products as per format at Annexure-2A and for financing products\nas per Annexures 2B, 2B.1 and 2B.2 to their prospective customers for comparison and decision\nmaking.",
        "EN": "Why must financial institutions provide a Key Fact Statement (KFS) to prospective customers for deposit and financing products?",
        "UR": "مالیاتی اداروں کو ڈیپازٹ اور فنانسنگ پروڈکٹس کے لیے ممکنہ گاہکوں کو کی فیکٹ سٹیٹمنٹ (KFS) فراہم کرنا کیوں ضروری ہے؟",
        "RU": "Financial institutions ko deposit aur financing products ke liye prospective customers ko Key Fact Statement (KFS) dena kyun zaroori hai?",
    },
    {
        "concept_id": "CRYPTO_CURRENCY_TRADING_FRAMEWORK_001",
        "query_type": "REGULATORY_REQUIREMENT",
        "difficulty": "EASY",
        "answerability": "UNANSWERABLE",
        "doc_id": None,
        "page": None,
        "span": None,
        "EN": "What are the State Bank of Pakistan licensing requirements and compliance guidelines for operating a cryptocurrency exchange?",
        "UR": "پاکستان میں کرپٹو کرنسی ایکسچینج چلانے کے لیے اسٹیٹ بینک آف پاکستان کے لائسنسنگ کے تقاضے اور قوانین کیا ہیں؟",
        "RU": "Pakistan mein cryptocurrency exchange chalane ke liye State Bank of Pakistan ke licensing rules aur compliance guidelines kya hain?",
    },
    {
        "concept_id": "MICROFINANCE_MAXIMUM_INTEREST_CAP_001",
        "query_type": "LIMIT_OR_THRESHOLD",
        "difficulty": "EASY",
        "answerability": "UNANSWERABLE",
        "doc_id": None,
        "page": None,
        "span": None,
        "EN": "What is the maximum statutory interest rate cap percentage that Microfinance Banks are permitted to charge on emergency agricultural loans?",
        "UR": "مائیکرو فنانس بینکوں کے لیے ہنگامی زرعی قرضوں پر سود کی زیادہ سے زیادہ قانونی حد (percentage cap) کیا ہے؟",
        "RU": "Microfinance Banks ke liye emergency zarai qarzay par sood ki maximum statutory percentage cap kitni mukarrar hai?",
    },
]


def build_benchmark():
    records = []
    for idx, c in enumerate(CONCEPTS_DATA, start=1):
        seq_str = f"{idx:04d}"
        cid = c["concept_id"]

        # EN
        en_rec = BenchmarkRecord(
            benchmark_id=f"TFB-{seq_str}-EN",
            concept_id=cid,
            query_text=c["EN"],
            query_language=BenchmarkLanguage.ENGLISH,
            query_script=BenchmarkScript.LATIN,
            query_type=getattr(BenchmarkQueryType, c["query_type"]),
            difficulty=getattr(BenchmarkDifficulty, c["difficulty"]),
            expected_document_ids=[c["doc_id"]] if c["doc_id"] else [],
            relevant_pages=[c["page"]] if c["page"] else [],
            evidence_spans=[
                EvidenceSpan(document_id=c["doc_id"], page_number=c["page"], verbatim_text=c["span"])
            ]
            if c["span"]
            else [],
            answerability=getattr(BenchmarkAnswerability, c["answerability"]),
            notes=f"English query record for concept {cid}",
        )
        records.append(en_rec)

        # UR
        ur_rec = BenchmarkRecord(
            benchmark_id=f"TFB-{seq_str}-UR",
            concept_id=cid,
            query_text=c["UR"],
            query_language=BenchmarkLanguage.URDU,
            query_script=BenchmarkScript.ARABIC,
            query_type=getattr(BenchmarkQueryType, c["query_type"]),
            difficulty=getattr(BenchmarkDifficulty, c["difficulty"]),
            expected_document_ids=[c["doc_id"]] if c["doc_id"] else [],
            relevant_pages=[c["page"]] if c["page"] else [],
            evidence_spans=[
                EvidenceSpan(document_id=c["doc_id"], page_number=c["page"], verbatim_text=c["span"])
            ]
            if c["span"]
            else [],
            answerability=getattr(BenchmarkAnswerability, c["answerability"]),
            notes=f"Urdu query record for concept {cid}",
        )
        records.append(ur_rec)

        # RU
        ru_rec = BenchmarkRecord(
            benchmark_id=f"TFB-{seq_str}-RU",
            concept_id=cid,
            query_text=c["RU"],
            query_language=BenchmarkLanguage.ROMAN_URDU,
            query_script=BenchmarkScript.LATIN,
            query_type=getattr(BenchmarkQueryType, c["query_type"]),
            difficulty=getattr(BenchmarkDifficulty, c["difficulty"]),
            expected_document_ids=[c["doc_id"]] if c["doc_id"] else [],
            relevant_pages=[c["page"]] if c["page"] else [],
            evidence_spans=[
                EvidenceSpan(document_id=c["doc_id"], page_number=c["page"], verbatim_text=c["span"])
            ]
            if c["span"]
            else [],
            answerability=getattr(BenchmarkAnswerability, c["answerability"]),
            notes=f"Roman Urdu query record for concept {cid}",
        )
        records.append(ru_rec)

    out_path = Path("data/benchmarks/finurdu_pilot_v0_1.jsonl")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as out:
        for rec in records:
            out.write(json.dumps(rec.model_dump(), ensure_ascii=False) + "\n")

    print(f"Successfully generated {len(records)} records in {out_path}")


if __name__ == "__main__":
    build_benchmark()
