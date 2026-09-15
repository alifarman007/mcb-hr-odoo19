"""Shared metadata for the 12 Purchase / Procurement tutorials (video + docx)."""

ADMIN = [("Requester / Accounts / CE / PC", "admin", "admin")]

# key, no, short_name, title, summary, outcome, leads
PUR = [
    ("pur01_request", 1, "Purchase_Request", "Raising a Purchase Request",
     "The form that starts every purchase MCB makes — project, budget head, items and estimated cost.",
     "A request on the system, checked against the budget",
     "Flow 2 — the four people who have to agree to it."),
    ("pur02_approval", 2, "Approval_Chain", "The Approval Chain (PR-005)",
     "Confirm, Accounts Check, CE Approve, Send to PC — and the names recorded at each step.",
     "An approved request, with every approver named on the record",
     "Flow 3 — how the value decides the method."),
    ("pur03_method", 3, "Procurement_Method", "Procurement Method & Thresholds (Table-9)",
     "Direct purchase, RFQ, RFP or open tender — decided by the amount, not by preference.",
     "The right method, chosen by the system, not by argument",
     "Flow 4 — getting the quotations in."),
    ("pur04_rfq", 4, "Sending_RFQs", "Sending Quotations Out to Vendors",
     "One click turns the approved request into a draft order for each supplier invited to quote.",
     "Three comparable quotations out to three vendors",
     "Flow 5 — the day the envelopes are opened."),
    ("pur05_opening", 5, "Opening_Sheet", "The Opening Sheet (Step 4)",
     "The committee opens the sealed quotations together and records who quoted what.",
     "A signed record of the opening, with every bidder and figure",
     "Flow 6 — do the offers actually meet the specification?"),
    ("pur06_technical", 6, "Technical_Analysis", "Technical Analysis (Step 5)",
     "Pass or fail against the written specification — before anybody looks at the price.",
     "Only technically compliant offers survive to the price comparison",
     "Flow 7 — comparing what is left, on price."),
    ("pur07_comparative", 7, "Comparative_Statement", "The Comparative Statement (Step 6)",
     "Side-by-side prices, ranked 1st, 2nd and 3rd lowest, with the committee's comment.",
     "A ranked, commented comparison the auditor can follow",
     "Flow 8 — scoring, and choosing the winner."),
    ("pur08_evaluation", 8, "Evaluation_and_Award", "Evaluation & Award (Steps 7–8)",
     "Price 40, quality 30, delivery 15, experience 15 — and the recommendation that follows.",
     "A scored decision, and the winning order created from it",
     "Flow 9 — telling the winner, in writing."),
    ("pur09_noal", 9, "NOAL", "The Notification of Award Letter (Step 9)",
     "Above 5,00,000 the award letter is compulsory — issued, then acknowledged by the vendor.",
     "An issued and acknowledged NOAL on file",
     "Flow 10 — the order itself, and its four signatures."),
    ("pur10_order", 10, "Purchase_Order", "Purchase Order & 4-Level Authorization (Step 10)",
     "Check, Review, Approve — three different people — and the gates that stop an unsigned order.",
     "A fully authorised order that the system agreed to confirm",
     "Flow 11 — the checklist that closes the file."),
    ("pur11_checklist", 11, "Checklist", "The Procurement Checklist (Annexure-29)",
     "Seventeen questions that confirm the process was actually followed, before the file is closed.",
     "A verified checklist attached to the procurement file",
     "Flow 12 — reading the whole picture back out."),
    ("pur12_reports", 12, "Reports", "The Procurement Reports (Step 11)",
     "Process timings, pending requests, project-wise, work-order-wise and vendor-wise spending.",
     "Every figure procurement is asked for, on demand",
     "— the procurement cycle is complete."),
]

META = {k: (no, title, summary, ADMIN) for k, no, _s, title, summary, _o, _l in PUR}
END = {k: (outcome, leads) for k, _n, _s, _t, _sm, outcome, leads in PUR}
SHORT = {k: short for k, _n, short, _t, _s, _o, _l in PUR}
