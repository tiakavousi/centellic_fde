from enum import Enum


class Product_type(str, Enum):
    mortgage = "mortgage"
    credit_card = "credit_card"
    current_account = "current_account"
    personal_loan = "personal_loan"
    savings = "savings"

class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class ComplaintStatus(str, Enum):
    open = "open"
    in_review = "in_review"
    resolved = "resolved"
    escalated = "escalated"

class Channel(str, Enum):
    app = "app"
    phone = "phone"
    branch = "branch"
    email = "email"
    webform = "webform"

class CustomerSegment(str, Enum):
    mass_market="mass_market"
    premier="premier"
    business="business"

class DocumentType(str, Enum):
     policy="policy"
     methodology="methodology"
     ombudsman="ombudsman"
     product_terms="product_terms"
     regulatory="regulatory"
     case_note="case_note"