"""
The document corpus. SYNTHETIC PLACEHOLDER CONTENT ONLY.
"""

from typing import Any
from data.enums import DocumentType


DOCUMENTS: list[dict[str, Any]] = [
    {
        "id": "doc-001",
        "title": "Complaint Handling Policy — Timeliness and Escalation",
        "complaint_id": None, # for the purpose of having uniform shape in all docs
        "type": DocumentType.policy,
        "body": (
            "All complaints must be acknowledged within three business days of "
            "receipt and a substantive response issued within eight weeks. "
            "Where a final response cannot be issued within that window, the "
            "customer must be informed in writing of their right to refer the "
            "matter to the Financial Ombudsman Service. Complaints involving "
            "arrears, fraud disputes or vulnerable customers must be routed to "
            "a specialist handler on the day of receipt. Handlers may not close "
            "a complaint without documented evidence that the customer's "
            "concerns have been addressed on their substance, not merely "
            "acknowledged."
        ),
    },
    {
        "id": "doc-002",
        "title": "Vulnerable Customers Standard — Identification and Care",
        "complaint_id": None,
        "type": DocumentType.policy,
        "body": (
            "A customer is treated as vulnerable where circumstances make them "
            "materially less able to represent their own interests. Recognised "
            "drivers include bereavement, serious illness, mental health "
            "conditions, financial hardship, coercion and reduced capacity. "
            "The vulnerability flag on the customer record is indicative and "
            "not exhaustive; handlers must remain alert to language in the "
            "complaint itself that suggests vulnerability, even where no flag "
            "is set. Where vulnerability is present or suspected, standard "
            "collection activity must be paused and the case escalated to the "
            "specialist team before any redress decision is communicated."
        ),
    },
    {
        "id": "doc-003",
        "title": "Redress Methodology — Mortgage Arrears and Late Fees",
        "complaint_id": None,
        "type": DocumentType.methodology,
        "body": (
            "Where a late payment fee has been charged as a result of a bank "
            "processing error, the fee is refunded in full together with any "
            "consequential interest. Where arrears have been reported to a "
            "credit reference agency in error, the record must be amended "
            "within fifteen business days and the customer notified. Where "
            "distress and inconvenience is evidenced, a payment in the range "
            "of one hundred to five hundred pounds may be offered, with the "
            "specific figure determined by the severity matrix in appendix A. "
            "Amounts outside that range require sign-off from the Head of "
            "Conduct. Redress figures must never be quoted to a customer "
            "before the calculation has been reviewed by a second handler."
        ),
    },
    {
        "id": "doc-004",
        "title": "Redress Methodology — Credit Card Interest and Charges",
        "complaint_id": None,
        "type": DocumentType.methodology,
        "body": (
            "Interest charged on disputed transactions is refunded from the "
            "date the dispute was raised, not from the date of resolution. "
            "Where a promotional rate has been mis-applied, the account is "
            "reworked on the basis of the rate the customer was entitled to "
            "expect. Over-limit and late payment fees are refunded where the "
            "underlying cause is attributable to the bank. Goodwill payments "
            "outside these categories are permitted up to one hundred and "
            "fifty pounds per complaint at handler discretion; above that "
            "figure, team leader approval is required."
        ),
    },
    {
        "id": "doc-005",
        "title": "FOS Decision Note — Direct Debit Failure and Late Fee",
        "complaint_id": 1,
        "type": DocumentType.ombudsman,
        "body": (
            "The customer set up a Direct Debit for their credit card two "
            "weeks before the payment due date. The instruction was accepted "
            "by the bank but not applied to the account in time, and a late "
            "payment fee was charged. The Ombudsman upheld the complaint and "
            "directed the bank to refund the fee, remove the late marker from "
            "the customer's credit file and pay one hundred and fifty pounds "
            "for distress and inconvenience. The decision notes that the fault "
            "was operational and that the customer had done everything a "
            "reasonable person could be expected to do."
        ),
    },
    {
        "id": "doc-006",
        "title": "FOS Decision Note — Insurance Sold Alongside Personal Loan",
        "complaint_id": 4,
        "type": DocumentType.ombudsman,
        "body": (
            "The customer took out a personal loan and was sold a payment "
            "protection product at the point of sale. The Ombudsman found "
            "that the customer's employment circumstances at the time meant "
            "the product would not have paid out under its own terms, and "
            "that this had not been made clear. The complaint was upheld. "
            "The bank was directed to refund all premiums paid, with interest "
            "at eight per cent simple, and to remove the product from the "
            "loan going forward. The decision notes that the customer was not "
            "flagged as vulnerable but that the sales process fell below the "
            "standard expected."
        ),
    },
    {
        "id": "doc-007",
        "title": "Product Terms — Standard Current Account (v2026.1)",
        "complaint_id": None,
        "type": DocumentType.product_terms,
        "body": (
            "The standard current account carries no monthly fee where the "
            "account is funded with at least five hundred pounds in each "
            "calendar month. Unarranged overdraft usage attracts a daily fee "
            "capped at a monthly maximum set out in the fee schedule. Faster "
            "Payments sent from the account are subject to the limits "
            "published in the mobile application; these limits may be reduced "
            "temporarily where fraud indicators are present. The bank reserves "
            "the right to decline a payment where it reasonably suspects the "
            "customer is the victim of an authorised push payment scam, "
            "subject to the customer's right to override that decision after "
            "a recorded warning."
        ),
    },
    {
        "id": "doc-008",
        "title": "Regulator Guidance — Consumer Duty and Foreseeable Harm",
        "complaint_id": None,
        "type": DocumentType.regulatory,
        "body": (
            "Firms must act to deliver good outcomes for retail customers and "
            "must avoid causing foreseeable harm. In the complaints context, "
            "this means identifying not only whether an individual case has "
            "been handled correctly but also whether the pattern of "
            "complaints indicates a product, process or communication that "
            "is causing harm at scale. Where such a pattern is identified, "
            "firms are expected to act on the root cause rather than continue "
            "to redress individual cases. Boards should receive complaints "
            "management information sufficient to discharge this duty. "
            "Reference CD-4.2 sets out the minimum data expected."
        ),
    },
    {
        "id": "doc-009",
        "title": "Product Terms — Rewards Credit Card (v2026.2)",
        "complaint_id": None,
        "type": DocumentType.product_terms,
        "body": (
            "The rewards credit card carries a representative APR set out on "
            "the account summary. Cashback is earned at the published rate on "
            "eligible spend, excluding cash advances, gambling transactions "
            "and balance transfers. Promotional interest-free periods apply "
            "to purchases made within the first three months, subject to "
            "minimum monthly payments being met in full and on time. Failure "
            "to meet a minimum payment ends the promotional period and "
            "restores the standard purchase rate from the following statement. "
            "Over-limit fees are charged where the account exceeds its credit "
            "limit at the statement date; a single fee applies per statement."
        ),
    },
    {
        "id": "doc-010",
        "title": "Product Terms — Fixed-Rate Mortgage (v2025.4)",
        "complaint_id": None,
        "type": DocumentType.product_terms,
        "body": (
            "The fixed-rate mortgage locks the interest rate for the initial "
            "period stated in the offer. Early repayment charges apply to any "
            "capital repaid above the annual overpayment allowance during the "
            "fixed period, calculated as a percentage of the amount repaid. "
            "Where a payment is missed, the account enters arrears and "
            "collections activity begins in line with the arrears handling "
            "procedure. Customers experiencing financial difficulty may "
            "request forbearance, including a payment holiday, subject to "
            "affordability review. Any agreed forbearance must be recorded "
            "in writing before it takes effect."
        ),
    },
    {
        "id": "doc-011",
        "title": "Product Terms — Personal Loan (Unsecured, v2026.1)",
        "complaint_id": None,
        "type": DocumentType.product_terms,
        "body": (
            "The unsecured personal loan is offered at a fixed rate for the "
            "term stated in the credit agreement. Optional payment protection "
            "products, where offered, must be sold on a non-advised basis and "
            "the customer's eligibility to claim under the policy terms must "
            "be established at the point of sale. Early settlement is "
            "permitted at any time; the settlement figure is calculated in "
            "line with the Consumer Credit Act rebate rules. Missed payments "
            "are reported to credit reference agencies after the second "
            "consecutive missed instalment."
        ),
    },
    {
        "id": "doc-012",
        "title": "Product Terms — Instant Access Savings (v2026.1)",
        "complaint_id": None,
        "type": DocumentType.product_terms,
        "body": (
            "The instant access savings account pays interest at the "
            "published variable rate. Introductory rates, where offered, "
            "apply for the period stated at account opening and revert to "
            "the standard rate thereafter without further notice. Interest "
            "is calculated daily and credited monthly. There are no "
            "restrictions on the number or size of withdrawals, subject to "
            "the daily Faster Payment limits. The bank may change the "
            "interest rate on notice as set out in the general terms."
        ),
    },
    {
        "id": "doc-013",
        "title": "FOS Decision Note — Arrears Reported in Error After Payment Holiday",
        "complaint_id": 2,
        "type": DocumentType.ombudsman,
        "body": (
            "The customer had an agreed payment holiday on their mortgage "
            "recorded in writing, but arrears were subsequently reported to "
            "credit reference agencies in respect of the payments covered by "
            "that agreement. The Ombudsman upheld the complaint and directed "
            "the bank to correct the credit file within fifteen business days, "
            "issue a written apology and pay three hundred pounds for "
            "distress and inconvenience. The decision was critical of the "
            "time the customer had spent chasing the correction, noting that "
            "the underlying error should have been resolved on first contact."
        ),
    },
    {
        "id": "doc-014",
        "title": "FOS Decision Note — Access to Joint Funds Following Bereavement",
        "complaint_id": 3,
        "type": DocumentType.ombudsman,
        "body": (
            "Following the death of a joint account holder, the surviving "
            "customer was unable to access funds for over five weeks despite "
            "having provided probate documentation on two occasions. The "
            "Ombudsman upheld the complaint. The bank was directed to release "
            "funds immediately, refund any fees and interest incurred as a "
            "consequence of the delay and pay five hundred pounds in "
            "recognition of the significant distress caused during a period "
            "of bereavement. The decision emphasised the bank's obligation "
            "under the Vulnerable Customers Standard to prioritise such cases."
        ),
    },
    {
        "id": "doc-015",
        "title": "Internal Case Note — Over-Limit Fees During Documented Hardship",
        "complaint_id": 5,
        "type": DocumentType.case_note,
        "body": (
            "Case reviewed under the Consumer Duty foreseeable harm test. "
            "The customer had contacted the hardship team and their status "
            "was recorded on the account, yet over-limit fees continued to be "
            "applied on the credit card for two subsequent statement cycles. "
            "Root cause was identified as a failure to propagate the hardship "
            "flag from the collections system to the fees engine. All fees "
            "charged during the hardship period were refunded, the credit "
            "file was amended and the underlying process defect was raised as "
            "a systemic finding. No individual redress payment was made "
            "beyond the fee refunds; the process defect was treated as the "
            "material remediation."
        ),
    },
    {
        "id": "doc-016",
        "title": "Authorised Push Payment Fraud — Reimbursement Procedure",
        "complaint_id": None,
        "type": DocumentType.policy,
        "body": (
            "Where a customer reports that they have been deceived into "
            "authorising a payment to a third party, the case must be "
            "assessed against the Contingent Reimbursement Model (CRM) code. "
            "The default position is that the customer is reimbursed in full "
            "unless the bank can evidence that one or more exceptions apply: "
            "the customer ignored a specific and effective warning, acted "
            "with gross negligence, or failed to take reasonable steps to "
            "verify the payee. Vulnerability at the time of the payment "
            "removes the gross negligence exception. A reimbursement decision "
            "must be issued within fifteen business days of the claim being "
            "raised; where more time is needed, the customer must be informed "
            "in writing and the reason recorded. Declines must be reviewed by "
            "a second handler before communication to the customer."
        ),
    },
    {
        "id": "doc-017",
        "title": "FOS Decision Note — APP Fraud Reimbursement Declined by Bank",
        "complaint_id": 8,
        "type": DocumentType.ombudsman,
        "body": (
            "The customer was contacted by a party claiming to be from the "
            "bank's fraud team and authorised a payment on that basis. The "
            "bank declined the reimbursement claim on the ground that the "
            "customer had been given generic warnings about impersonation "
            "scams within the mobile application. The Ombudsman found that "
            "the warnings relied on were not specific and effective in the "
            "circumstances of this payment, and that the exception under the "
            "CRM code did not apply. The complaint was upheld. The bank was "
            "directed to reimburse the disputed amount in full, pay interest "
            "at eight per cent simple from the date of the payment and pay "
            "two hundred pounds for distress and inconvenience. The decision "
            "noted that the second-handler review required before decline had "
            "not been evidenced in the bank's file."
        ),
    },
]
