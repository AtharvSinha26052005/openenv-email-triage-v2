"""
Email triage scenarios for each task difficulty.
"""
from typing import Dict, Any, List


SCENARIOS: Dict[str, List[Dict[str, Any]]] = {
    "easy": [
        {
            "id": "easy_001",
            "emails": [
                {
                    "from": "customer@example.com",
                    "subject": "Cannot access my account",
                    "body": "I've been trying to log in for an hour but keep getting an error. Please help.",
                    "timestamp": "2024-01-15T10:30:00Z"
                }
            ],
            "context": "Single support email requiring categorization and prioritization.",
            "available_actions": [
                "category:support priority:high action:escalate_to_technical_support",
                "category:billing priority:medium action:escalate_to_billing",
                "category:general priority:low action:respond",
                "category:support priority:medium action:respond",
            ],
            "expected_category": "support",
            "expected_priority": "high",
            "expected_action": "escalate_to_technical_support",
        },
        {
            "id": "easy_002",
            "emails": [
                {
                    "from": "finance@company.com",
                    "subject": "Invoice #12345 - Payment Confirmation Needed",
                    "body": "We received your payment but the invoice number doesn't match our records. Please verify the transaction details at your earliest convenience.",
                    "timestamp": "2024-01-16T14:20:00Z"
                }
            ],
            "context": "Billing inquiry requiring verification and response.",
            "available_actions": [
                "category:billing priority:medium action:respond_with_verification",
                "category:support priority:high action:escalate_to_technical_support",
                "category:billing priority:low action:archive",
                "category:general priority:medium action:respond",
            ],
            "expected_category": "billing",
            "expected_priority": "medium",
            "expected_action": "respond_with_verification",
        },
        {
            "id": "easy_003",
            "emails": [
                {
                    "from": "marketing@newsletter.com",
                    "subject": "Your Weekly Tech Digest - January 2024",
                    "body": "Here are this week's top technology stories and industry insights...",
                    "timestamp": "2024-01-17T08:00:00Z"
                }
            ],
            "context": "Newsletter email with low priority.",
            "available_actions": [
                "category:general priority:low action:archive",
                "category:marketing priority:high action:respond",
                "category:support priority:medium action:escalate_to_technical_support",
                "category:general priority:medium action:respond",
            ],
            "expected_category": "general",
            "expected_priority": "low",
            "expected_action": "archive",
        },
    ],
    "medium": [
        {
            "id": "medium_001",
            "emails": [
                {
                    "id": "email_1",
                    "from": "partner@business.com",
                    "subject": "Q4 Partnership Proposal",
                    "body": "We'd like to discuss a potential partnership for Q4.",
                    "timestamp": "2024-01-15T09:15:00Z"
                },
                {
                    "id": "email_2",
                    "from": "billing@vendor.com",
                    "subject": "URGENT: Payment Overdue - Service Suspension",
                    "body": "Your account is 30 days overdue. Pay within 48 hours to avoid suspension.",
                    "timestamp": "2024-01-15T11:00:00Z"
                },
                {
                    "id": "email_3",
                    "from": "newsletter@marketing.com",
                    "subject": "Weekly Industry Updates",
                    "body": "Check out this week's top stories in tech...",
                    "timestamp": "2024-01-15T08:00:00Z"
                }
            ],
            "context": "Three emails requiring prioritization. Handle the most urgent first.",
            "available_actions": [
                "priority_order:email_2,email_1,email_3 immediate:email_2",
                "priority_order:email_1,email_2,email_3 immediate:email_1",
                "priority_order:email_3,email_2,email_1 immediate:email_3",
                "priority_order:email_2,email_3,email_1 immediate:email_2",
            ],
            "expected_priority_first": "email_2",
            "expected_immediate": "email_2",
        },
        {
            "id": "medium_002",
            "emails": [
                {
                    "id": "email_1",
                    "from": "security@company.com",
                    "subject": "Security Alert: Unusual Login Activity",
                    "body": "We detected a login attempt from an unrecognized device in a different country. Please verify this was you.",
                    "timestamp": "2024-01-16T13:45:00Z"
                },
                {
                    "id": "email_2",
                    "from": "hr@company.com",
                    "subject": "Reminder: Annual Performance Review Due Friday",
                    "body": "Please complete your self-assessment by end of week.",
                    "timestamp": "2024-01-16T10:00:00Z"
                },
                {
                    "id": "email_3",
                    "from": "ceo@company.com",
                    "subject": "All-Hands Meeting Tomorrow at 2 PM",
                    "body": "Important company updates to share. Attendance is mandatory.",
                    "timestamp": "2024-01-16T16:30:00Z"
                },
                {
                    "id": "email_4",
                    "from": "sales@vendor.com",
                    "subject": "Special Offer: 30% Off Enterprise Plan",
                    "body": "Limited time offer for premium customers...",
                    "timestamp": "2024-01-16T09:00:00Z"
                }
            ],
            "context": "Four emails with varying urgency. Security issue takes precedence.",
            "available_actions": [
                "priority_order:email_1,email_3,email_2,email_4 immediate:email_1",
                "priority_order:email_3,email_1,email_2,email_4 immediate:email_3",
                "priority_order:email_2,email_1,email_3,email_4 immediate:email_2",
                "priority_order:email_4,email_3,email_2,email_1 immediate:email_4",
            ],
            "expected_priority_first": "email_1",
            "expected_immediate": "email_1",
        },
    ],
    "hard": [
        {
            "id": "hard_001",
            "emails": [
                {
                    "from": "vip.customer@enterprise.com",
                    "subject": "Extremely disappointed - considering legal action",
                    "body": "Third outage in two months. Lost significant revenue. Legal team reviewing contract. Need immediate senior management response.",
                    "timestamp": "2024-01-15T14:30:00Z",
                    "metadata": {"customer_tier": "enterprise", "account_value": "$500k/year"}
                }
            ],
            "context": "VIP enterprise customer threatening legal action after repeated service failures. SLA breach confirmed.",
            "available_actions": [
                "category:critical_escalation escalate:customer_success_manager,vp_operations,legal_review strategy:acknowledge,compensate,executive_call",
                "category:support escalate:support_team strategy:respond",
                "category:billing escalate:billing_team strategy:respond",
                "category:critical_escalation escalate:support_manager strategy:acknowledge",
            ],
            "expected_category": "critical_escalation",
            "expected_escalation": ["customer_success_manager", "vp_operations", "legal_review"],
        },
        {
            "id": "hard_002",
            "emails": [
                {
                    "from": "media@techcrunch.com",
                    "subject": "Request for Comment: Data Breach Allegations",
                    "body": "We're running a story about alleged data breach affecting 50,000 users. Multiple sources claim customer data was exposed. Need official statement within 2 hours before publication.",
                    "timestamp": "2024-01-16T15:00:00Z",
                    "metadata": {"urgency": "critical", "public_relations_risk": "severe"}
                }
            ],
            "context": "Media inquiry about potential data breach. High reputational risk. Requires immediate crisis management response.",
            "available_actions": [
                "category:crisis_management escalate:ceo,legal_counsel,pr_director,security_team strategy:investigate,legal_review,prepare_statement,media_response",
                "category:support escalate:support_team strategy:respond",
                "category:general escalate:pr_team strategy:acknowledge",
                "category:crisis_management escalate:pr_director strategy:acknowledge",
            ],
            "expected_category": "crisis_management",
            "expected_escalation": ["ceo", "legal_counsel", "pr_director", "security_team"],
        },
        {
            "id": "hard_003",
            "emails": [
                {
                    "from": "regulator@sec.gov",
                    "subject": "Formal Investigation Notice - Compliance Violation",
                    "body": "This is formal notification of an investigation into potential securities law violations. You are required to preserve all relevant documents and provide requested materials within 10 business days. Failure to comply may result in penalties.",
                    "timestamp": "2024-01-17T11:20:00Z",
                    "metadata": {"sender_type": "government_regulator", "legal_risk": "extreme"}
                }
            ],
            "context": "Government regulatory investigation notice. Requires immediate legal counsel and executive involvement. Non-compliance has severe consequences.",
            "available_actions": [
                "category:legal_regulatory escalate:ceo,general_counsel,compliance_officer,board_of_directors strategy:legal_review,document_preservation,external_counsel,regulatory_response",
                "category:legal escalate:legal_team strategy:respond",
                "category:support escalate:compliance_team strategy:acknowledge",
                "category:legal_regulatory escalate:general_counsel strategy:legal_review",
            ],
            "expected_category": "legal_regulatory",
            "expected_escalation": ["ceo", "general_counsel", "compliance_officer", "board_of_directors"],
        },
    ]
}


def get_scenario(task: str, index: int = 0) -> Dict[str, Any]:
    if task not in SCENARIOS:
        raise ValueError(f"Unknown task: {task}")
    scenarios = SCENARIOS[task]
    return scenarios[index % len(scenarios)]
