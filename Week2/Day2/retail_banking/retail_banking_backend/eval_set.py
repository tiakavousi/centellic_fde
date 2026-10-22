"""
Labelled eval set for retrieval and answer quality.

Each answerable question records:
  doc_id    the document that holds the answer
  evidence  a short verbatim span from that document. A retrieved chunk counts
            as a hit only if it contains this exact span, so a chunk that cuts
            the span in half is a miss. That is deliberate: it shows chunking damage.
  keywords  what a correct answer must mention. Every item must appear in the answer.
            "a|b" means either a or b is acceptable. Matching is case-insensitive and
            whole-word, so "no" does not match inside "not". A trailing * allows any
            ending, so "acknowledg*" matches "acknowledged" and "acknowledgement".
            A refusal never counts as correct, whatever words it happens to contain.
  kind      what the question tests

Unanswerable questions have doc_id None and no evidence. The correct behaviour is refusal.

┌─────────────────────────────────────────┬───────────┬──────────────────────────────────────┐
│                 Source                  │ Questions │            Kinds covered             │
├─────────────────────────────────────────┼───────────┼──────────────────────────────────────┤
│ documents.py (doc-001 to doc-017)       │ q01 q19   │ numeric, lookup, negation            │
├─────────────────────────────────────────┼───────────┼──────────────────────────────────────┤
│ corpus.py doc-101 (Consumer Duty)       │ q20 q22   │ heading-dependent, exact-id          │
├─────────────────────────────────────────┼───────────┼──────────────────────────────────────┤
│ corpus.py doc-102 (Complaints Policy)   │ q23 q25   │ negation, heading-dependent, numeric │
├─────────────────────────────────────────┼───────────┼──────────────────────────────────────┤
│ corpus.py doc-103 (FOS Adjudications)   │ q26 q27   │ heading-dependent, negation          │
├─────────────────────────────────────────┼───────────┼──────────────────────────────────────┤
│ corpus.py doc-104 (APP Fraud Policy)    │ q28 q29   │ negation, numeric                    │
├─────────────────────────────────────────┼───────────┼──────────────────────────────────────┤
│ corpus.py doc-105 (Redress Methodology) │ q30 q31   │ heading-dependent, negation          │
├─────────────────────────────────────────┼───────────┼──────────────────────────────────────┤
│ Unanswerable                            │ q32 q34   │ unanswerable                         │
└─────────────────────────────────────────┴───────────┴──────────────────────────────────────┘
"""

EVAL_SET = [
    # --- doc-001: Complaint Handling Policy — Timeliness and Escalation ---
    {"id": "q01", "question": "How many business days does the bank have to acknowledge a complaint?",
     "doc_id": "doc-001", "evidence": "acknowledged within three business days",
     "keywords": ["three|3"], "kind": "numeric"},

    {"id": "q02", "question": "What is the maximum number of weeks a bank has to issue a final response to a complaint?",
     "doc_id": "doc-001", "evidence": "substantive response issued within eight weeks",
     "keywords": ["eight|8"], "kind": "numeric"},

    {"id": "q03", "question": "Which types of complaints must be routed to a specialist handler on the day of receipt?",
     "doc_id": "doc-001", "evidence": "arrears, fraud disputes or vulnerable customers must be routed to a specialist handler on the day of receipt",
     "keywords": ["arrears", "fraud"], "kind": "lookup"},

    # --- doc-002: Vulnerable Customers Standard ---
    {"id": "q04", "question": "What are the recognised drivers of customer vulnerability?",
     "doc_id": "doc-002", "evidence": "bereavement, serious illness, mental health conditions, financial hardship, coercion and reduced capacity",
     "keywords": ["bereavement", "hardship"], "kind": "lookup"},

    {"id": "q05", "question": "What must happen to collection activity when vulnerability is present or suspected?",
     "doc_id": "doc-002", "evidence": "standard collection activity must be paused and the case escalated to the specialist team",
     "keywords": ["paus*", "escalat*"], "kind": "lookup"},

    # --- doc-003: Redress Methodology — Mortgage Arrears and Late Fees ---
    {"id": "q06", "question": "How quickly must an incorrect credit reference agency entry be corrected?",
     "doc_id": "doc-003", "evidence": "record must be amended within fifteen business days",
     "keywords": ["fifteen|15"], "kind": "numeric"},

    {"id": "q07", "question": "Who must sign off redress amounts above the upper band of the severity matrix?",
     "doc_id": "doc-003", "evidence": "Amounts above the upper band of that matrix require sign-off from the Head of Conduct",
     "keywords": ["Head of Conduct"], "kind": "lookup"},

    # --- doc-004: Redress Methodology — Credit Card ---
    {"id": "q08", "question": "From what date is interest refunded on a disputed credit card transaction?",
     "doc_id": "doc-004", "evidence": "Interest charged on disputed transactions is refunded from the date the dispute was raised",
     "keywords": ["disput* was raised|dispute was raised"], "kind": "lookup"},

    # --- doc-005: FOS Decision — Direct Debit Failure ---
    {"id": "q09", "question": "What did the FOS direct the bank to do in the direct debit failure case?",
     "doc_id": "doc-005", "evidence": "refund the fee, remove the late marker from the customer's credit file",
     "keywords": ["refund", "credit file"], "kind": "lookup"},

    {"id": "q10", "question": "Was the customer at fault in the direct debit failure complaint?",
     "doc_id": "doc-005", "evidence": "the customer had done everything a reasonable person could be expected to do",
     "keywords": ["no|not|fault"], "kind": "negation"},

    # --- doc-006: FOS Decision — PPI ---
    {"id": "q11", "question": "What rate of interest did the FOS direct the bank to pay on refunded PPI premiums?",
     "doc_id": "doc-006", "evidence": "refund all premiums paid, with interest at eight per cent simple",
     "keywords": ["eight|8"], "kind": "numeric"},

    # --- doc-007: Standard Current Account ---
    {"id": "q12", "question": "Can the bank decline a payment it suspects is an authorised push payment scam?",
     "doc_id": "doc-007", "evidence": "The bank reserves the right to decline a payment where it reasonably suspects the customer is the victim of an authorised push payment scam",
     "keywords": ["yes|declin*|right"], "kind": "negation"},

    # --- doc-008: Consumer Duty ---
    {"id": "q13", "question": "What should a firm do when a pattern of complaints indicates harm at scale?",
     "doc_id": "doc-008", "evidence": "firms are expected to act on the root cause rather than continue to redress individual cases",
     "keywords": ["root cause"], "kind": "lookup"},

    # --- doc-010: Fixed-Rate Mortgage ---
    {"id": "q14", "question": "When do early repayment charges apply on a fixed-rate mortgage?",
     "doc_id": "doc-010", "evidence": "Early repayment charges apply to any capital repaid above the annual overpayment allowance during the fixed period",
     "keywords": ["overpayment allowance|fixed period"], "kind": "lookup"},

    # --- doc-013: FOS Decision — Arrears After Payment Holiday ---
    {"id": "q15", "question": "What did the FOS say about the time the customer spent chasing the credit file correction?",
     "doc_id": "doc-013", "evidence": "the underlying error should have been resolved on first contact",
     "keywords": ["first contact"], "kind": "lookup"},

    # --- doc-014: FOS Decision — Bereavement ---
    {"id": "q16", "question": "How long was the surviving customer unable to access joint funds after bereavement?",
     "doc_id": "doc-014", "evidence": "unable to access funds for over five weeks",
     "keywords": ["five|5"], "kind": "numeric"},

    # --- doc-016: APP Fraud Reimbursement Procedure ---
    {"id": "q17", "question": "Does vulnerability remove the gross negligence exception in APP fraud cases?",
     "doc_id": "doc-016", "evidence": "Vulnerability at the time of the payment removes the gross negligence exception",
     "keywords": ["yes|remov*"], "kind": "negation"},

    {"id": "q18", "question": "Within how many business days must a reimbursement decision be issued for APP fraud?",
     "doc_id": "doc-016", "evidence": "reimbursement decision must be issued within fifteen business days",
     "keywords": ["fifteen|15"], "kind": "numeric"},

    # --- doc-017: FOS Decision — APP Fraud Declined ---
    {"id": "q19", "question": "Why did the FOS uphold the APP fraud complaint?",
     "doc_id": "doc-017", "evidence": "the warnings relied on were not specific and effective in the circumstances of this payment",
     "keywords": ["specific and effective|not specific"], "kind": "lookup"},

    # --- doc-101: FCA Consumer Duty (corpus, sectioned) ---
    {"id": "q20", "question": "How often must a product review be carried out under the Consumer Duty?",
     "doc_id": "doc-101", "evidence": "A product review must be carried out at least annually",
     "keywords": ["annual*|year*|once a year"], "kind": "heading-dependent"},

    {"id": "q21", "question": "What is the Consumer Duty test for consumer communications?",
     "doc_id": "doc-101", "evidence": "whether a reasonable person in the target market would understand what is being offered",
     "keywords": ["reasonable person"], "kind": "heading-dependent"},

    {"id": "q22", "question": "What regulatory reference covers the minimum complaints data expected in board MI?",
     "doc_id": "doc-101", "evidence": "Reference CD-4.2 sets out the minimum data expected in board MI",
     "keywords": ["CD-4.2"], "kind": "exact-id"},

    # --- doc-102: Complaints Handling Policy 2026 (corpus, sectioned) ---
    {"id": "q23", "question": "Can the eight-week complaints clock be reset by transferring the case to another team?",
     "doc_id": "doc-102", "evidence": "cannot be reset by transferring the case between teams",
     "keywords": ["no|cannot|can not"], "kind": "negation"},

    {"id": "q24", "question": "How long must complaint case files be preserved?",
     "doc_id": "doc-102", "evidence": "Case files must be preserved for a minimum of six years",
     "keywords": ["six|6"], "kind": "heading-dependent"},

    {"id": "q25", "question": "How many complaints sharing the same root cause trigger a systemic finding?",
     "doc_id": "doc-102", "evidence": "three or more complaints within a rolling ninety-day window",
     "keywords": ["three|3"], "kind": "numeric"},

    # --- doc-103: FOS Adjudication Summary — Mortgage Arrears (corpus, sectioned) ---
    {"id": "q26", "question": "What award level did the FOS apply where a payment holiday error persisted for more than four weeks?",
     "doc_id": "doc-103", "evidence": "award level was consistently placed in the mid band of the redress methodology",
     "keywords": ["mid band"], "kind": "heading-dependent"},

    {"id": "q27", "question": "Does the FOS require forbearance to be granted once a written request is received?",
     "doc_id": "doc-103", "evidence": "The FOS did not require forbearance to be granted in all cases",
     "keywords": ["no|not required|did not require"], "kind": "negation"},

    # --- doc-104: APP Fraud Policy 2026 (corpus, sectioned) ---
    {"id": "q28", "question": "Does a generic scam warning on the login screen satisfy the specific and effective warning test?",
     "doc_id": "doc-104", "evidence": "A generic warning about scams displayed on the login screen does not satisfy the specific and effective warning test",
     "keywords": ["no|does not|not satisfy"], "kind": "negation"},

    {"id": "q29", "question": "What is the maximum number of business days an extended APP fraud assessment can take?",
     "doc_id": "doc-104", "evidence": "extended assessment must still conclude within thirty business days",
     "keywords": ["thirty|30"], "kind": "numeric"},

    # --- doc-105: Redress Methodology Full Reference (corpus, sectioned) ---
    {"id": "q30", "question": "From what date is consequential interest calculated when a bank error causes extra charges?",
     "doc_id": "doc-105", "evidence": "The calculation runs from the date the error occurred to the date it was corrected",
     "keywords": ["error occurred|error was made"], "kind": "heading-dependent"},

    {"id": "q31", "question": "Can a handler quote a redress figure to a customer before second-handler review?",
     "doc_id": "doc-105", "evidence": "Redress figures of any kind must not be quoted to a customer, even as estimates, before the calculation has been reviewed by a second handler",
     "keywords": ["no|must not|cannot"], "kind": "negation"},

    # --- Unanswerable: not in any document ---
    {"id": "q32", "question": "What is the bank's net promoter score?",
     "doc_id": None, "evidence": None, "keywords": [], "kind": "unanswerable"},

    {"id": "q33", "question": "Who is the current Chief Executive of the bank?",
     "doc_id": None, "evidence": None, "keywords": [], "kind": "unanswerable"},

    {"id": "q34", "question": "What is the bank's total number of retail customers?",
     "doc_id": None, "evidence": None, "keywords": [], "kind": "unanswerable"},
]


def answerable() -> list[dict]:
    return [q for q in EVAL_SET if q["doc_id"] is not None]


def unanswerable() -> list[dict]:
    return [q for q in EVAL_SET if q["doc_id"] is None]
