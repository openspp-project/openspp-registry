STATE_DRAFT = "draft"
STATE_TO_APPROVE = "to_approve"
STATE_APPROVED = "approved"
STATE_DISTRIBUTED = "distributed"
# STATE_ACTIVE = "active"
STATE_ENDED = "ended"
STATE_CANCELLED = "cancelled"

MANAGER_ELIGIBILITY = 1
MANAGER_CYCLE = 2
MANAGER_PROGRAM = 3
MANAGER_ENTITLEMENT = 4
MANAGER_DEDUPLICATION = 5
MANAGER_NOTIFICATION = 6
MANAGER_PAYMENT = 7

MANAGER_MODELS = {
    "deduplication_managers": {
        "g2p.deduplication.manager": "g2p.deduplication.manager.default",
    },
    "notification_managers": {
        "g2p.program.notification.manager": "g2p.program.notification.manager.sms",
    },
    "program_managers": {
        "g2p.program.manager": "g2p.program.manager.default",
    },
    "payment_managers": {
        "g2p.program.payment.manager": "g2p.program.payment.manager.default",
    },
}
