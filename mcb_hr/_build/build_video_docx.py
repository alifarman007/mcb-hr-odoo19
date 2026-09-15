"""Build MCB_HR_Video_Tutorial_Script.docx — the production guide for the
9-part HR video tutorial series (storyboard + narration + screenshots).

Run: /Data/odoo19_enterprise/venv/bin/python _build/build_video_docx.py
"""
from pathlib import Path

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BUILD = Path("/Data/odoo19_enterprise/custom-addons/mcb_hr/_build")
SHOT = BUILD / "screenshots" / "video"
OLD = BUILD / "screenshots"          # the earlier reference-manual captures
MAPS = SHOT / "_maps"
OUT = Path("/Data/odoo19_enterprise/mukticox/MCB_HR_Video_Tutorial_Script.docx")

NAVY = RGBColor(0x1F, 0x36, 0x4D)
GREY = RGBColor(0x55, 0x55, 0x55)
GREEN = RGBColor(0x1E, 0x7A, 0x53)
RED = RGBColor(0xA6, 0x2B, 0x2B)
AMBER = RGBColor(0x8A, 0x60, 0x00)


# =============================================================================
# SERIES DEFINITION
# =============================================================================
SERIES = [
    dict(
        num=0, key="v0_overview", title="Welcome — What This System Does",
        dur="3 min", who="Everyone (all staff)", prereq="None — start here",
        map=MAPS / "map_00_master.png",
        goal=[
            "Understand what the HR system replaces (paper forms, registers, Excel).",
            "See the whole journey on one map, so later videos have a place to sit.",
            "Recognise the three things every Odoo screen has: status bar, tabs, chatter.",
        ],
        scenes=[
            dict(t="Open on the map", img=MAPS / "map_00_master.png",
                 show="Full-screen the journey map.",
                 say="Welcome to the Mukti Cox's Bazar HR system. Before we touch a single "
                     "button, look at this picture. Everything we do in HR — hiring someone, "
                     "onboarding them, approving their leave, paying them, and one day saying "
                     "goodbye — is one single journey. Each box you see here is one video in "
                     "this series. And here is the important part: each box hands its paperwork "
                     "to the next box automatically. Nothing is typed twice.",
                 ost="MCB HR — one journey, seven stages"),
            dict(t="Who does what", img=None,
                 show="Show the roles slide (make this in your editor from the table in this script).",
                 say="Five kinds of people use this system. Regular staff apply for leave and "
                     "claim their travel money. Project Managers ask for new staff and approve "
                     "their team's requests. HR runs recruitment, keeps employee records and "
                     "approves leave. Finance runs payroll. And the Chief Executive gives the "
                     "final approval on the big decisions. You only need to learn the parts that "
                     "belong to your role.",
                 ost="Find your role — then watch those videos"),
            dict(t="Logging in", img=SHOT / "v0_overview/01_home_app_launcher.png",
                 show="Log in, land on the main dashboard of apps.",
                 say="You log in with your own email and password. What you see here depends on "
                     "who you are — if you are not in HR, you will simply see fewer apps. That is "
                     "normal and it is deliberate.",
                 ost="You only see what your role allows"),
            dict(t="The MCB apps", img=SHOT / "v0_overview/02_apps_mcb_modules.png",
                 show="Apps list filtered to MCB.",
                 say="These are the parts built specially for Mukti Cox's Bazar — they follow our "
                     "own HR policy, our grades, our leave rules, our forms.",
                 ost="Built to MCB policy — not generic software"),
            dict(t="Anatomy of any screen", img=SHOT / "v0_overview/03_anatomy_of_a_record.png",
                 show="Open any record. Point to (1) the status bar across the top, "
                      "(2) the tabs in the middle, (3) the chatter panel on the right.",
                 say="Every screen in this system looks the same once you know where to look. "
                     "Along the top is the status bar — it shows which step the paper is at. In "
                     "the middle are tabs holding the details. And on the right is the chatter — "
                     "this is your history. Every approval, every change, with the person's name "
                     "and the time. Nothing can be changed quietly.",
                 teach="The chatter is your audit trail — auditors can see who approved what, and when.",
                 ost="1 Status bar  ·  2 Tabs  ·  3 Chatter (history)"),
            dict(t="What is next", img=None,
                 show="Return to the map, point to 'SET UP ONCE'.",
                 say="In the next video, we set the system up — the grades, the leave types, the "
                     "holidays, the travel rates. That is a one-time job for the administrator. "
                     "If you are a normal user, you can skip to video three and start with hiring.",
                 ost="Next → Video 1: One-time setup"),
        ],
        came="—  this is the beginning.",
        goes="Video 1 — the administrator configures MCB's policy into the system.",
    ),

    dict(
        num=1, key="v1_config", title="One-Time Setup (Administrator)",
        dur="7 min", who="System Administrator / HR Manager", prereq="Video 0",
        map=MAPS / "map_v1_config.png",
        goal=[
            "Enter MCB's policy into the system so it enforces itself afterwards.",
            "Understand that GRADE is the master switch that drives leave, travel and salary.",
            "Set leave types, public holidays, per-diem rates and user roles.",
        ],
        scenes=[
            dict(t="Why setup matters", img=MAPS / "map_v1_config.png",
                 show="The map with the 'SET UP ONCE' band highlighted.",
                 say="Everything in this video is done once, by the administrator. After this, "
                     "the system knows MCB's rules and will apply them automatically — so nobody "
                     "has to remember them.",
                 ost="Do this once. The system remembers forever."),
            dict(t="Grades G1–G10", img=SHOT / "v1_config/01_grades_list_g1_g10.png",
                 show="MCB HR → Configuration → MCB Grades. Show the list of ten grades.",
                 say="Start with grades. MCB has ten grades, from G1 at the top to G10. The grade "
                     "is the single most important setting in the whole system, because it "
                     "controls four other things at once.",
                 ost="Grade = the master switch"),
            dict(t="What a grade controls", img=SHOT / "v1_config/02_grade_form_officer.png",
                 show="Open the Officer grade. Point at each field as you name it.",
                 say="Open one grade and you can see it. The grade decides the salary band. It "
                     "decides how many days of leave that person earns. It decides their travel "
                     "and food allowance rate. And it decides whether they are allowed overtime — "
                     "only support staff and drivers are. Set this correctly once, and every "
                     "leave form and every travel claim afterwards fills itself in.",
                 teach="Change a grade here and every future calculation follows the new rule.",
                 ost="Grade drives: salary · leave · per-diem · overtime"),
            dict(t="Leave types", img=SHOT / "v1_config/03_leave_types_list.png",
                 show="Time Off → Configuration → Time Off Types.",
                 say="Next, leave. MCB has eight kinds of leave — annual, sick, casual, maternity, "
                     "paternity, compensatory, leave without pay, and work from home. Each one "
                     "carries its own rules.",
                 ost="8 leave types, each with its own rule"),
            dict(t="Rule: no annual leave on probation",
                 img=SHOT / "v1_config/04_leave_type_annual_probation_block.png",
                 show="Open Annual Leave. Point to the probation-block setting.",
                 say="Here is a good example. Annual leave has 'block during probation' switched "
                     "on. That means a new employee who is still on probation simply cannot apply "
                     "for it — the system stops them politely. HR does not have to police it.",
                 teach="Policy is enforced by the software, not by memory.",
                 ost="Probation staff are blocked automatically"),
            dict(t="Rule: compensatory leave needs the CE",
                 img=SHOT / "v1_config/05_leave_type_compensatory_ce_gate.png",
                 show="Open Compensatory Leave. Point to the CE approval requirement.",
                 say="Compensatory leave is stricter still. Normal leave needs two approvals — the "
                     "manager and HR. Compensatory leave needs a third: the Chief Executive. The "
                     "system will not let it finish without that signature.",
                 ost="Compensatory = Manager + HR + CE"),
            dict(t="Bangladesh holiday calendar", img=SHOT / "v1_config/06_public_holidays_bd.png",
                 show="Time Off → Configuration → Public Holidays.",
                 say="Now the holiday calendar — Independence Day, Pohela Boishakh, both Eids, "
                     "Victory Day and the rest. Load these and the system will never count a "
                     "public holiday as a leave day again.",
                 ost="Load holidays once a year"),
            dict(t="Travel and food rates", img=SHOT / "v1_config/07_per_diem_rate_table.png",
                 show="MCB HR → Configuration → Per Diem Rates.",
                 say="Then the travel and food rates. These are the TA and DA amounts from MCB's "
                     "policy — breakfast, lunch, dinner, full day, and the field-visit lunch. They "
                     "are set per grade band.",
                 ost="TA / DA rates by grade band"),
            dict(t="Rate detail", img=SHOT / "v1_config/08_per_diem_form_detail.png",
                 show="Open one rate row and walk through the amounts.",
                 say="Enter them once here, and when staff claim travel money later, the correct "
                     "amount appears by itself. No arguments, no calculator.",
                 ost="Claims will auto-fill from this table"),
            dict(t="Users and roles", img=SHOT / "v1_config/09_users_and_roles.png",
                 show="Settings → Users. Show a user's role checkboxes.",
                 say="Finally, roles. Each person is marked as CE, Project Manager, Recruitment "
                     "Committee member, HR or Finance. This decides which buttons they see. Give "
                     "the Chief Executive role only to the Chief Executive — the approval gates we "
                     "just set up depend on it.",
                 teach="Roles are the security of the whole system. Assign them carefully.",
                 ost="Roles decide who can approve what"),
        ],
        came="Video 0 — the map.",
        goes="Video 2 — with policy in place, a Project Manager can now ask for a new staff member.",
    ),

    dict(
        num=2, key="v2_requisition", title="Asking for New Staff (Requisition)",
        dur="6 min", who="Project Manager · HR · Chief Executive", prereq="Video 1",
        map=MAPS / "map_v2_requisition.png",
        goal=[
            "Raise a Staff Requisition (the replacement for MCB Form 21a/21b).",
            "Move it through the PM → HR → CE approval chain.",
            "Publish it and print the Job Circular.",
        ],
        scenes=[
            dict(t="Where we are", img=MAPS / "map_v2_requisition.png",
                 show="Map with stage 1 lit.",
                 say="Hiring at MCB starts with a piece of paper called the Staff Requisition. In "
                     "this video we replace that paper.",
                 ost="Stage 1 of 7 — Requisition"),
            dict(t="The requisition list", img=SHOT / "v2_requisition/01_requisition_list.png",
                 show="MCB HR → Recruitment → Staff Requisitions.",
                 say="Here is every request for new staff, and the stage each one has reached. "
                     "Let us follow a real one — the MEAL Officer post for Cox's Bazar.",
                 ost="MCB HR → Recruitment → Staff Requisitions"),
            dict(t="Filling the form", img=SHOT / "v2_requisition/02_requisition_form_published.png",
                 show="Open REQ/2026/0001. Walk down the form: position, grade, vacancies, "
                      "employment type, working area, project and donor, required-from date.",
                 say="The Project Manager fills this in. What is the position. Which grade. How "
                     "many vacancies. Is it permanent or project-based. Where will they work. And "
                     "very importantly — which project and which donor pays for this post. That "
                     "last part matters, because it is how the salary later reaches the right "
                     "donor report.",
                 teach="Project and donor entered here follow the employee for their whole career.",
                 ost="Project + donor = correct donor reporting later"),
            dict(t="The budget check", img=None,
                 show="Point to the 'Budget Confirmed' checkbox and remarks field.",
                 say="Before this goes anywhere, someone confirms there is budget for the post. "
                     "Without that tick, it should not proceed.",
                 ost="No budget, no recruitment"),
            dict(t="Exam marks setup",
                 img=SHOT / "v2_requisition/04_requisition_full_form_marks_scheme.png",
                 show="Open the Marks Configuration tab.",
                 say="Here you set how the candidates will be marked — written fifty, computer "
                     "twenty, oral thirty. That is MCB's standard. These numbers travel with this "
                     "recruitment, so every candidate is judged the same way.",
                 ost="Written 50 · Computer 20 · Oral 30"),
            dict(t="The approval chain", img=None,
                 show="RECORD LIVE: click Submit, then approve as HR, then approve as CE. "
                      "Show the status bar moving at each step.",
                 say="Now watch the status bar at the top. The Project Manager submits it. HR "
                     "reviews it. Then the Chief Executive approves it. Three different people, "
                     "three separate steps — and every one of them is recorded on the right-hand "
                     "side with a name and a time.",
                 teach="Nobody can approve their own request. Watch the chatter fill up.",
                 ost="PM → HR → CE"),
            dict(t="Publish and print", img=SHOT / "v2_requisition/06_job_circular_pdf.png",
                 show="Click Publish, then Print Job Circular.",
                 say="Once the CE approves, you publish it — and the system writes the job "
                     "circular for you, on MCB letterhead, using what you already typed. Nothing "
                     "is retyped. Send this out, and applications can begin.",
                 ost="One click → ready-to-send circular"),
        ],
        came="Video 1 — grades and roles were set up.",
        goes="Video 3 — applications arrive against this published post.",
    ),

    dict(
        num=3, key="v3_recruitment", title="Applicants, Exams & the Merit List",
        dur="8 min", who="Recruitment Committee · HR", prereq="Video 2",
        map=MAPS / "map_v3_recruitment.png",
        goal=[
            "Record candidates and shortlist them.",
            "Issue Admit Cards and print the attendance top sheet.",
            "Enter marks and let the system build an honest merit list.",
        ],
        scenes=[
            dict(t="Where we are", img=MAPS / "map_v3_recruitment.png",
                 show="Map with stage 2 lit.",
                 say="The post is advertised. Now the applications come in, and we have to choose "
                     "fairly — and be able to prove it was fair.",
                 ost="Stage 2 of 7 — Recruitment"),
            dict(t="The pipeline", img=SHOT / "v3_recruitment/01_recruitment_pipeline_kanban.png",
                 show="Recruitment app kanban.",
                 say="Every applicant is a card, and the columns are the stages of our process. "
                     "You move a candidate forward by dragging the card. It is the same board the "
                     "whole committee can see.",
                 ost="Drag cards to move candidates forward"),
            dict(t="A candidate's file", img=SHOT / "v3_recruitment/03_applicant_form_rashedul.png",
                 show="Open Rashedul Karim.",
                 say="This is Rashedul Karim — remember his name, because he is going to be with us "
                     "for the rest of this series. His file holds everything MCB asks for: father's "
                     "and mother's name, present and permanent address, NID, education and past "
                     "experience.",
                 ost="Meet Rashedul Karim — our example throughout"),
            dict(t="Admit cards", img=SHOT / "v3_recruitment/05_admit_card_pdf.png",
                 show="On the applicant, click Issue Admit Card, then print it.",
                 say="When the committee shortlists someone, you issue an admit card. The system "
                     "gives each candidate a unique admit card number, prints their exam date, "
                     "time and venue, and signs it off from the CE or Director HR and Admin.",
                 ost="Unique admit card number per candidate"),
            dict(t="The attendance sheet",
                 img=SHOT / "v3_recruitment/06_admit_card_topsheet_pdf.png",
                 show="From the requisition, click Print Admit Card Top Sheet.",
                 say="And this is the sheet the invigilator carries into the exam hall — every "
                     "candidate, with their father's and mother's name, mobile number, and a column "
                     "for their signature. Print it, and your exam day is organised.",
                 ost="Invigilator's attendance sheet — one click"),
            dict(t="Entering marks", img=SHOT / "v3_recruitment/04_applicant_mcb_tab_marks.png",
                 show="Open the MCB Recruitment tab on a candidate. Type written, computer, "
                      "oral skills and oral knowledge marks.",
                 say="After the exams, you enter the marks on each candidate's MCB tab. Written out "
                     "of fifty. Computer out of twenty. Then the oral marks are split in two — "
                     "skills out of fifteen and knowledge out of fifteen — because two examiners "
                     "score separately. The total adds itself up.",
                 teach="Marks are entered per candidate — no master spreadsheet to lose.",
                 ost="W 50 + C 20 + Oral (15+15) = 100"),
            dict(t="The merit list", img=SHOT / "v3_recruitment/02_applicants_list_with_marks.png",
                 show="Back on the list view, click Compute Merit Rank. Show the ranked list.",
                 say="Now the important moment. Click compute merit rank, and the system sorts "
                     "every candidate by total score and numbers them one, two, three. Rashedul "
                     "Karim comes first with ninety-two. This list is the evidence that the "
                     "selection was made on marks — not on anything else.",
                 teach="The merit list is your audit defence. It is computed, not typed.",
                 ost="Ranked automatically by total marks"),
            dict(t="Selection and cost", img=SHOT / "v3_recruitment/08_recruitment_expenditure.png",
                 show="Mark the top candidate as Selected. Then open Recruitment Expenditure.",
                 say="Mark the top candidate as selected. And because recruitment costs money — "
                     "food, committee members' travel, stationery — you record that here too, "
                     "against the recruitment budget.",
                 ost="Record recruitment costs against budget"),
        ],
        came="Video 2 — the published requisition.",
        goes="Video 4 — the selected candidate becomes a real employee.",
    ),

    dict(
        num=4, key="v4_onboarding", title="Hiring & Onboarding a New Employee",
        dur="6 min", who="HR", prereq="Video 3",
        map=MAPS / "map_v4_onboarding.png",
        goal=[
            "Turn the selected candidate into an employee record.",
            "Complete the MCB Profile — NID, parents, service dates, PF nominee.",
            "Launch the orientation plan and track probation.",
        ],
        scenes=[
            dict(t="Where we are", img=MAPS / "map_v4_onboarding.png",
                 show="Map with stage 3 lit.",
                 say="Rashedul has been selected. Now HR turns him from a candidate into a member "
                     "of staff.",
                 ost="Stage 3 of 7 — Onboarding"),
            dict(t="Hire", img=SHOT / "v4_onboarding/01_employees_list_with_codes.png",
                 show="RECORD LIVE: on the applicant, press Create Employee / move to Hired. "
                      "Then show him appearing in the Employees list.",
                 say="One button — create employee — and his whole file moves across. Everything "
                     "you typed during recruitment is already there. And notice he now has an "
                     "employee code, generated automatically with his project prefix.",
                 teach="No re-typing between recruitment and HR. That is the point of the chain.",
                 ost="Applicant → Employee, in one click"),
            dict(t="The MCB Profile tab", img=SHOT / "v4_onboarding/03_employee_mcb_profile_tab.png",
                 show="Open Rashedul → MCB Profile tab.",
                 say="This tab is the part built for MCB. National ID, father's and mother's name, "
                     "blood group, emergency contact. Then the service dates — when he joined, when "
                     "probation starts and ends, and when he was confirmed. And his Provident Fund "
                     "nominee, which matters a great deal on the day someone leaves.",
                 ost="NID · parents · service dates · PF nominee"),
            dict(t="Contract and grade",
                 img=SHOT / "v4_onboarding/05_employee_full_form.png",
                 show="Open the contract / version details showing employment type, grade, "
                      "project code, donor and analytic code.",
                 say="Here is where the grade from video one gets attached to a real person. His "
                     "employment type, his grade, his project and his donor. From this moment, the "
                     "system knows how much leave he earns, what travel rate he gets, and which "
                     "donor pays his salary.",
                 teach="This single screen powers leave, expense and payroll for this person.",
                 ost="Grade attached → leave, TA/DA and salary all follow"),
            dict(t="Orientation plan", img=SHOT / "v4_onboarding/06_activity_plans_list.png",
                 show="Show the MCB Employee Onboarding activity plan and its ten tasks.",
                 say="New staff need orientation, and MCB requires ten sessions — organisation "
                     "history and vision, code of conduct, safeguarding and PSEAH, anti-fraud, "
                     "finance, IT, procurement, logistics, monitoring and evaluation, and their own "
                     "job description. Launch the plan and all ten appear as tasks with owners and "
                     "due dates, plus the ID card, email account, bank details and contract "
                     "signing.",
                 ost="10 orientations + ID + email + bank + contract"),
            dict(t="Probation reminder", img=None,
                 show="Point at the probation end date on the MCB Profile tab.",
                 say="One last thing. Fifteen days before probation ends, the system automatically "
                     "reminds his line manager to make a decision — confirm him, extend, or not. "
                     "No one has to keep that date in their head.",
                 teach="Automatic reminder 15 days before probation ends.",
                 ost="Probation reminder is automatic"),
        ],
        came="Video 3 — the selected candidate.",
        goes="Video 5 — now employed, Rashedul can apply for leave.",
    ),

    dict(
        num=5, key="v5_leave", title="Applying for Leave & Approving It",
        dur="6 min", who="All staff · Line Managers · HR", prereq="Video 4",
        map=MAPS / "map_v5_leave.png",
        goal=[
            "Check your balance and apply for leave.",
            "Approve leave as a manager, then as HR (two levels).",
            "See how the system blocks leave that breaks policy.",
        ],
        scenes=[
            dict(t="Where we are", img=MAPS / "map_v5_leave.png",
                 show="Map with stage 4 lit.",
                 say="This is the video most staff will watch, because everyone takes leave.",
                 ost="Stage 4 of 7 — Leave"),
            dict(t="Your balance first",
                 img=SHOT / "v5_leave/01_timeoff_dashboard_balances.png",
                 show="Open the Time Off app dashboard.",
                 say="Open Time Off and the first thing you see is what you actually have — annual, "
                     "sick, casual. Always look here before you plan anything.",
                 ost="Check your balance before you apply"),
            dict(t="Applying", img=SHOT / "v5_leave/02_my_leave_requests_list.png",
                 show="RECORD LIVE: click New. Choose Annual Leave, pick the dates, type the "
                      "reason, Save.",
                 say="Rashedul needs three days for a family wedding. He clicks New, chooses annual "
                     "leave, picks his dates, and the system counts the working days for him — it "
                     "already knows about Fridays, Saturdays and public holidays. He writes the "
                     "reason and saves.",
                 teach="Weekends and public holidays are never counted as leave.",
                 ost="Working days counted automatically"),
            dict(t="Waiting for approval",
                 img=SHOT / "v5_leave/03_leave_pending_approval_buttons.png",
                 show="Show the saved request sitting in 'To Approve'.",
                 say="Now it is out of his hands. The status says to approve, and it has gone to "
                     "his manager.",
                 ost="Status: To Approve"),
            dict(t="Manager approves",
                 img=SHOT / "v5_leave/05_manager_approval_queue.png",
                 show="Log in as the manager. Time Off → to-approve list. Click Approve.",
                 say="The manager sees everything waiting for them in one list. They open it, check "
                     "the team is covered, and approve. That is level one.",
                 ost="Level 1 — Line Manager"),
            dict(t="HR approves — and it is final",
                 img=SHOT / "v5_leave/04_leave_approved.png",
                 show="As HR, approve the same request. Show status = Approved and the "
                      "balance dropping.",
                 say="Then HR gives the second approval, and only now is it really leave. Look at "
                     "the balance — it has come down by three days by itself. And the chatter on "
                     "the right shows both approvals with names and times.",
                 teach="Two approvals for normal leave. Compensatory leave needs a third from the CE.",
                 ost="Level 2 — HR  →  Approved"),
            dict(t="When the rules say no", img=None,
                 show="RECORD LIVE (good teaching moment): as an employee still on probation, "
                      "try to apply for Annual Leave. Show the error message appearing.",
                 say="And here is what happens when someone tries to break the rule. A staff member "
                     "still on probation applies for annual leave — and the system stops it, and "
                     "explains why. Nobody has to be the bad person. The policy does it.",
                 teach="Show at least one blocked action in the video — it teaches the rule instantly.",
                 ost="Policy blocks it — automatically"),
        ],
        came="Video 4 — Rashedul is now an active employee with a grade.",
        goes="Video 6 — travelling for work and claiming the money back.",
    ),

    dict(
        num=6, key="v6_expense", title="Travel Money — TA / DA Claims",
        dur="6 min", who="All staff · HoD · Finance", prereq="Video 4",
        map=MAPS / "map_v6_expense.png",
        goal=[
            "Raise a TA/DA claim and let the grade fill in the rate.",
            "Understand the field-visit, distance and overnight rules.",
            "Know when the Chief Executive must approve.",
        ],
        scenes=[
            dict(t="Where we are", img=MAPS / "map_v6_expense.png",
                 show="Map with stage 5 lit.",
                 say="Staff travel to the camps constantly. This is how they get their money back "
                     "without arguing about the amount.",
                 ost="Stage 5 of 7 — Expense / TA-DA"),
            dict(t="A real claim", img=SHOT / "v6_expense/03_expense_form_ta_da.png",
                 show="Open Rashedul's Camp 12 monitoring claim.",
                 say="Rashedul went to Camp 12 to do monitoring. Sixty-two kilometres, and he stayed "
                     "overnight. He records the trip here.",
                 ost="One claim = one trip"),
            dict(t="The grade fills the rate",
                 img=SHOT / "v6_expense/04_expense_full_form_tada_fields.png",
                 show="Point at the grade field, then click Apply Per Diem and show the amount "
                      "appear.",
                 say="Notice he does not type an amount. His grade is already on the form — it came "
                     "from his contract in video four. He clicks apply per diem, and the correct "
                     "rate from the table we set up in video one appears by itself. Over fifty "
                     "kilometres and an overnight stay both change what he is entitled to, and the "
                     "system knows.",
                 teach="Rates come from the table — so two people on the same grade always get "
                       "the same amount.",
                 ost="Grade → automatic, correct amount"),
            dict(t="Rules that protect the organisation", img=None,
                 show="RECORD LIVE: tick Air Travel and try to choose Business class — show the "
                      "system refusing. Then show the CE-approval flag appearing for air travel.",
                 say="Two rules are built in. First, air travel is economy class only — try to "
                     "choose business and the system simply will not accept it. Second, if the trip "
                     "involves flying, or the person is grade one or two, the Chief Executive must "
                     "approve it personally. The claim cannot be paid without that.",
                 teach="Economy-only and CE-approval are hard rules, not reminders.",
                 ost="Economy only · CE approves air travel"),
            dict(t="Approval and payment", img=SHOT / "v6_expense/02_expenses_list.png",
                 show="RECORD LIVE: submit → HoD approves → Finance posts and reimburses.",
                 say="He submits it, his head of department approves, and Finance pays it. And "
                     "because the project and donor are on the claim, that cost lands in the right "
                     "donor's report automatically.",
                 ost="Staff → HoD → Finance → paid"),
        ],
        came="Video 4 — his grade and project came from his contract.",
        goes="Video 7 — the monthly payroll run.",
    ),

    dict(
        num=7, key="v7_payroll", title="Running Monthly Payroll",
        dur="8 min", who="Finance / Payroll Officer", prereq="Videos 1 & 4",
        map=MAPS / "map_v7_payroll.png",
        goal=[
            "Run a monthly payslip batch.",
            "Understand what the system calculates: PF, festival bonus, gratuity, tax.",
            "Produce the bank transfer file.",
        ],
        scenes=[
            dict(t="Where we are", img=MAPS / "map_v7_payroll.png",
                 show="Map with stage 6 lit.",
                 say="Payroll is where everything we have set up so far quietly pays off.",
                 ost="Stage 6 of 7 — Payroll"),
            dict(t="Three salary structures",
                 img=SHOT / "v7_payroll/01_salary_structures_list.png",
                 show="Payroll → Configuration → Salary Structures.",
                 say="MCB pays three kinds of staff differently — permanent staff on grades, "
                     "project staff on a consolidated salary, and support staff. So there are three "
                     "structures, and each employee is on the right one automatically because of "
                     "their employment type.",
                 ost="Permanent · Project · Support"),
            dict(t="What the rules do",
                 img=SHOT / "v7_payroll/02_structure_mcb_permanent_rules.png",
                 show="Open the MCB Permanent structure and scroll its rules.",
                 say="Inside a structure are the rules, and this is MCB's policy written as "
                     "arithmetic. Provident fund at ten percent from the employee and ten percent "
                     "from MCB, once they have completed a year. Two festival bonuses. The "
                     "Baishakhi bonus for permanent staff. Gratuity. Bangladesh income tax slabs. "
                     "And overtime — but only for support staff and drivers, exactly as the policy "
                     "says.",
                 teach="You never edit these during a payroll run. They are policy, set once.",
                 ost="PF · Festival · Baishakhi · Gratuity · Tax · OT"),
            dict(t="Creating the batch", img=SHOT / "v7_payroll/03_payslip_batches.png",
                 show="Payroll → Payslip Batches → New. Name it for the month.",
                 say="Each month you create one batch — call it by the month — and generate "
                     "payslips for everyone in it.",
                 ost="One batch per month"),
            dict(t="Inside a payslip", img=SHOT / "v7_payroll/05_payslip_form.png",
                 show="Open one payslip.",
                 say="Open any payslip and you can see the whole calculation, line by line. Basic, "
                     "allowances, the deductions, and the net. Nothing is a mystery number — you "
                     "can point at any line and say which rule produced it.",
                 ost="Every line traceable to a rule"),
            dict(t="The computation lines",
                 img=SHOT / "v7_payroll/06_payslip_salary_computation_lines.png",
                 show="Open the Salary Computation tab.",
                 say="This is the detail Finance checks before paying. Attendance and approved "
                     "leave from earlier videos have already been taken into account.",
                 ost="Leave and attendance already included"),
            dict(t="Paying everyone", img=None,
                 show="RECORD LIVE: confirm the batch, then run the Bank Transfer wizard and show "
                      "the CSV downloading.",
                 say="When Finance is satisfied, confirm the batch and generate the bank transfer "
                     "file. That single file goes to the bank and pays everyone — with their "
                     "employee code, account number, project and donor already on each line.",
                 ost="One file → the whole payroll paid"),
        ],
        came="Videos 1 and 4 — grades, contracts, leave and attendance.",
        goes="Video 8 — the last stage: when someone leaves.",
    ),

    dict(
        num=8, key="v8_separation", title="Resignation & Final Settlement",
        dur="6 min", who="HR · Line Manager · CE", prereq="Videos 4, 5 & 7",
        map=MAPS / "map_v8_separation.png",
        goal=[
            "Record a resignation and let the system check the notice period.",
            "Complete the exit interview and property handover.",
            "Produce the final settlement and the experience certificate.",
        ],
        scenes=[
            dict(t="Where we are", img=MAPS / "map_v8_separation.png",
                 show="Map with stage 7 lit.",
                 say="People leave, and that has to be done properly and fairly. This is the last "
                     "stage of the journey.",
                 ost="Stage 7 of 7 — Separation"),
            dict(t="The resignation",
                 img=SHOT / "v8_separation/02_resignation_form_short_notice.png",
                 show="Open Farzana Akter's resignation. Point at required vs actual notice.",
                 say="Farzana is resigning. She is permanent staff, so MCB policy requires sixty "
                     "days' notice — but she is only giving twenty. Look what the system does: it "
                     "works out that she is forty days short, and calculates the salary in lieu "
                     "automatically. Nobody had to look up the rule or argue about it.",
                 teach="Notice periods: 60 days permanent · 30 project · 15 on probation.",
                 ost="Short notice → salary in lieu, calculated"),
            dict(t="Approvals", img=SHOT / "v8_separation/01_resignation_list.png",
                 show="RECORD LIVE: submit → manager review → HR → CE approve.",
                 say="It goes to her line manager, then HR, then the Chief Executive — the same "
                     "pattern you have seen all through this series.",
                 ost="Manager → HR → CE"),
            dict(t="Exit interview", img=SHOT / "v8_separation/05_exit_interview_list.png",
                 show="Show the exit interview record created from the resignation.",
                 say="An exit interview is recorded — why she is really leaving. Over a year, these "
                     "answers tell the organisation something worth knowing.",
                 ost="Exit interview — recorded, not lost"),
            dict(t="Final settlement",
                 img=SHOT / "v8_separation/03_resignation_full_form_settlement.png",
                 show="Open the Final Settlement tab and walk through each figure.",
                 say="Now the money. Outstanding salary. Leave encashment — using the balance from "
                     "the leave videos. Provident fund, and here the rule matters: under one year "
                     "she gets only her own contribution, over one year she gets MCB's share as "
                     "well, and in a dismissal the employer share is forfeited. Then gratuity. The "
                     "system adds it all up, and subtracts the short-notice amount.",
                 teach="The settlement pulls from leave, PF and gratuity automatically.",
                 ost="Salary + leave + PF + gratuity − short notice"),
            dict(t="Closing the file", img=None,
                 show="Tick property returned, print the experience certificate, then Close.",
                 say="Finally: property handed back, experience certificate printed, and when you "
                     "close the record her system access is switched off the same day. The file "
                     "stays for audit — but the access does not.",
                 teach="Access is revoked automatically on closing. That is a real security control.",
                 ost="Certificate printed · access revoked"),
            dict(t="Full circle", img=MAPS / "map_00_master.png",
                 show="Return to the full map.",
                 say="And that is the whole journey — from asking for a new post, to the day "
                     "someone leaves. Every stage handed its paperwork to the next one, and every "
                     "approval is recorded with a name and a time. Thank you for watching.",
                 ost="One journey · seven stages · fully auditable"),
        ],
        came="Videos 4, 5 and 7 — service dates, leave balance and salary.",
        goes="— the journey is complete.",
    ),
]


# =============================================================================
# DOCX HELPERS
# =============================================================================

def set_cell_bg(cell, hex_color):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:fill'), hex_color)
    tc_pr.append(shd)


def add_page_number(p):
    r = p.add_run()
    f1 = OxmlElement('w:fldChar'); f1.set(qn('w:fldCharType'), 'begin')
    it = OxmlElement('w:instrText'); it.set(qn('xml:space'), 'preserve'); it.text = 'PAGE'
    f2 = OxmlElement('w:fldChar'); f2.set(qn('w:fldCharType'), 'end')
    r._r.append(f1); r._r.append(it); r._r.append(f2)


def style_doc(doc):
    doc.styles['Normal'].font.name = 'Calibri'
    doc.styles['Normal'].font.size = Pt(11)
    for size, name in [(16, 'Heading 1'), (14, 'Heading 2'), (12, 'Heading 3')]:
        st = doc.styles[name]
        st.font.name = 'Calibri'; st.font.size = Pt(size); st.font.color.rgb = NAVY
    for s in doc.sections:
        s.top_margin = s.bottom_margin = s.left_margin = s.right_margin = Inches(0.9)


def caption(doc, text):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text); r.italic = True; r.font.size = Pt(9); r.font.color.rgb = GREY


MISSING = []


def embed(doc, path, cap, width=5.9):
    if path is None:
        return
    p = Path(path)
    if not p.exists():
        MISSING.append(str(p))
        para = doc.add_paragraph(); para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = para.add_run(f"[screenshot to capture: {p.name}]")
        r.font.color.rgb = RED; r.font.size = Pt(9)
        return
    ip = doc.add_paragraph(); ip.alignment = WD_ALIGN_PARAGRAPH.CENTER
    ip.add_run().add_picture(str(p), width=Inches(width))
    caption(doc, cap)


def table(doc, headers, rows, widths=None):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Light Grid Accent 1"; t.alignment = WD_TABLE_ALIGNMENT.LEFT
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]; c.text = ""
        r = c.paragraphs[0].add_run(h); r.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF); r.font.size = Pt(10)
        set_cell_bg(c, '1F4E79')
    for idx, row in enumerate(rows):
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = str(v) if v is not None else ""
            for pp in cells[i].paragraphs:
                for rr in pp.runs:
                    rr.font.size = Pt(9.5)
        if idx % 2 == 1:
            for c in cells:
                set_cell_bg(c, 'F2F2F2')
    if widths:
        for r_ in t.rows:
            for i, w in enumerate(widths):
                r_.cells[i].width = Inches(w)
    return t


def label_para(doc, label, text, colour, italic=False, bold_text=False):
    p = doc.add_paragraph()
    r = p.add_run(f"{label}  ")
    r.bold = True; r.font.size = Pt(10); r.font.color.rgb = colour
    r2 = p.add_run(text)
    r2.font.size = Pt(10.5); r2.italic = italic; r2.bold = bold_text
    return p


# =============================================================================
# BUILD
# =============================================================================

def build():
    doc = Document()
    style_doc(doc)

    sec = doc.sections[0]
    hp = sec.header.paragraphs[0]
    hp.text = "MCB · HR Video Tutorial Series — Production Script"
    hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    for r in hp.runs:
        r.font.size = Pt(9); r.italic = True; r.font.color.rgb = GREY
    fp = sec.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fp.add_run("Page ").font.size = Pt(9)
    add_page_number(fp)

    # ---------------- TITLE ----------------
    for _ in range(3):
        doc.add_paragraph()
    t = doc.add_paragraph(); t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = t.add_run("Mukti Cox's Bazar"); r.bold = True; r.font.size = Pt(30); r.font.color.rgb = NAVY
    s = doc.add_paragraph(); s.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = s.add_run("HR Video Tutorial Series"); r.bold = True; r.font.size = Pt(22)
    s2 = doc.add_paragraph(); s2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = s2.add_run("Production Script, Storyboard & Narration\n9 videos · about 56 minutes total")
    r.italic = True; r.font.size = Pt(13); r.font.color.rgb = GREY
    doc.add_paragraph()
    embed(doc, MAPS / "map_00_master.png", "The journey this series teaches", width=6.2)
    m = doc.add_paragraph(); m.alignment = WD_ALIGN_PARAGRAPH.CENTER
    m.add_run("Version 1.0  ·  MCB ERP Team").font.size = Pt(11)
    doc.add_page_break()

    # ---------------- HOW TO USE ----------------
    doc.add_heading("How to use this document", level=1)
    doc.add_paragraph(
        "This is not a user manual — it is the script you record from. Work through it "
        "one video at a time, from the top. Every scene tells you exactly what to put on "
        "the screen, what to say out loud, and what to type on top of the picture.")
    table(doc, ["Marker", "Means"], [
        ("SHOW", "What to display or click on screen while recording."),
        ("SAY", "Read this out. It is written to be spoken, not read silently."),
        ("ON-SCREEN", "Short text to place on the video as a caption or callout."),
        ("TEACH", "The rule this scene exists to teach. Do not cut this scene."),
        ("RECORD LIVE", "Must be filmed as live motion (a click, a form filling in, an error "
                        "popping up). A still screenshot will not teach it."),
    ], widths=[1.3, 5.2])
    doc.add_paragraph(
        "Screenshots printed in this document are reference stills taken from the live "
        "system with real demo data. Use them to confirm you are on the right screen, then "
        "record your own moving version.")

    doc.add_heading("The one rule that makes this series work", level=2)
    p = doc.add_paragraph()
    r = p.add_run("Follow one person the whole way through. ")
    r.bold = True
    p.add_run(
        "Our example is Rashedul Karim, a MEAL Officer in Cox's Bazar, funded by UNFPA. "
        "He applies for the job in video 3, is hired in video 4, takes leave in video 5, "
        "claims his travel money in video 6, and is paid in video 7. Viewers remember a "
        "story about a person. They do not remember a tour of menus.")
    doc.add_page_break()

    # ---------------- SERIES AT A GLANCE ----------------
    doc.add_heading("1. The series at a glance", level=1)
    doc.add_paragraph(
        "Nine videos, in this order. The order is not arbitrary — each one can only be "
        "done once the one before it exists in the system.")
    table(doc, ["#", "Video", "Length", "Who should watch", "Needs first"],
          [[f"{v['num']}", v['title'], v['dur'], v['who'], v['prereq']] for v in SERIES],
          widths=[0.4, 2.2, 0.7, 2.0, 1.2])
    doc.add_paragraph()
    doc.add_heading("Two tracks — tell viewers which one they are on", level=2)
    table(doc, ["Track", "Videos", "Who"], [
        ("Set up once", "1", "Administrator / HR Manager — watch once, before go-live."),
        ("Use every day", "2 – 8", "Everyone else — watch the ones for your role."),
    ], widths=[1.4, 1.2, 4.0])
    doc.add_paragraph(
        "Tell people this in video 0. Nothing loses an audience faster than a store-keeper "
        "sitting through payroll configuration.")
    doc.add_page_break()

    # ---------------- THE MAP + CONNECTIONS ----------------
    doc.add_heading("2. The map — and how each stage connects", level=1)
    embed(doc, MAPS / "map_00_master.png", "Master map — put this on screen at the start of every video", 6.3)
    doc.add_paragraph(
        "Show this map at the start of every single video, with the current stage lit up. "
        "Ready-made versions with each stage highlighted are supplied alongside this document "
        "in the _maps folder. Repeating the map is what turns nine separate videos into one "
        "course.")

    doc.add_heading("2.1 What flows from where to where", level=2)
    doc.add_paragraph(
        "This table is the answer to 'how is it all connected'. Each row is a handover — "
        "the thing on the left is produced by one stage and is then used, without being "
        "re-typed, by the stage on the right.")
    table(doc, ["What is produced", "Made in", "Then used by", "Why it matters"], [
        ("Approved Staff Requisition", "V2 Requisition", "V3 Recruitment",
         "Creates the vacancy and fixes the marks scheme (50/20/30)."),
        ("Project + donor on the requisition", "V2", "V4 → V6 → V7",
         "Follows the person into their contract, their travel claims and their payslip, so the "
         "right donor is charged."),
        ("Merit list + selected candidate", "V3 Recruitment", "V4 Onboarding",
         "One button turns the winner into an employee — no re-typing their details."),
        ("Grade on the contract", "V1 config → set in V4", "V5, V6, V7",
         "Decides leave entitlement, per-diem rate, overtime eligibility and salary structure."),
        ("Employee record + service dates", "V4 Onboarding", "V5, V7, V8",
         "Probation dates drive leave restrictions; join date drives PF and gratuity."),
        ("Approved leave", "V5 Leave", "V7 Payroll, V8 Separation",
         "Affects the payslip, and the leave encashment in the final settlement."),
        ("Approved TA/DA claim", "V6 Expense", "Finance / donor reports",
         "Carries the project and donor code, so the cost lands in the right report."),
        ("Payslip + bank file", "V7 Payroll", "V8 Separation",
         "Salary figures feed the outstanding-salary part of the settlement."),
        ("Final settlement + certificate", "V8 Separation", "Audit file",
         "Closes the loop; system access is revoked the same day."),
    ], widths=[1.5, 1.1, 1.2, 2.5])
    doc.add_page_break()

    # ---------------- PRESENTATION STRATEGY ----------------
    doc.add_heading("3. How to present it — seven rules", level=1)
    doc.add_paragraph(
        "These are the decisions that separate a tutorial people finish from one they "
        "abandon. Apply all seven.")
    rules = [
        ("1. One person, all the way through",
         "Rashedul Karim appears in every video from 3 onwards. Say his name. When you reach "
         "payroll, remind viewers this is the same man they hired in video 4."),
        ("2. Always show the map first",
         "Ten seconds at the start of each video: the map, with today's stage lit. Viewers "
         "never feel lost, and they see the shape of the whole system nine times over."),
        ("3. Say who you are being",
         "Put a small badge on screen — Employee, Line Manager, HR, Finance, CE — and change "
         "it when you switch roles. In an approval-heavy system this is the single most "
         "confusing thing if you leave it out."),
        ("4. Explain why before how",
         "Never open with 'click here'. Open with the problem: 'Rashedul needs three days off "
         "for a wedding.' Then the clicks mean something."),
        ("5. Break a rule on purpose",
         "Every video should show one thing the system refuses to do — leave during probation, "
         "business-class flights, a payment without approval. People remember rules that bite "
         "far better than rules that are described."),
        ("6. End with the handover",
         "Last fifteen seconds of every video: 'this record is now sitting in HR's list — that "
         "is the next video.' This is what makes the series feel like one process."),
        ("7. Slow the mouse down",
         "Move deliberately, pause one second before every click, and zoom in on the area you "
         "are talking about. What is obvious to you is brand new to the viewer."),
    ]
    for head, body in rules:
        doc.add_heading(head, level=3)
        doc.add_paragraph(body)
    doc.add_page_break()

    # ---------------- RECORDING SETUP ----------------
    doc.add_heading("4. Recording setup", level=1)
    table(doc, ["Setting", "Use this", "Why"], [
        ("Recording size", "1920 × 1080 (Full HD)", "Text stays readable when compressed."),
        ("Browser", "Chrome or Edge, full screen (F11)", "Hides bookmarks and tabs."),
        ("Browser zoom", "100 %, or 110 % for form-heavy screens", "Bigger text beats more content."),
        ("System", "The MCB training database", "Never record on live production data."),
        ("Login", "Use a demo login per role", "Lets you show real approval hand-offs."),
        ("Audio", "Quiet room, headset mic, record narration separately",
         "You can re-record a sentence without redoing the screen."),
        ("Mouse", "Enable click-highlight in your recorder", "Viewers can follow the pointer."),
        ("Length", "Keep every video under 8 minutes", "Split it rather than run long."),
    ], widths=[1.3, 2.2, 2.8])

    doc.add_heading("4.1 Before you hit record — checklist", level=2)
    for line in [
        "Close email, chat and notifications.",
        "Clear the browser search box and any leftover filters from the last take.",
        "Check the record you plan to open is in the right state (see the cheat-sheet in Appendix A).",
        "Hide any real person's phone number, NID or salary that is not demo data.",
        "Do a 20-second test recording and actually listen to it.",
    ]:
        doc.add_paragraph(line, style="List Bullet")

    doc.add_heading("4.2 On-screen text style", level=2)
    table(doc, ["Element", "How it should look"], [
        ("Callout box", "Yellow rounded rectangle around the button being clicked, 3 px border."),
        ("Arrow", "Red, short, pointing at one thing only. Never more than two on screen."),
        ("Step number", "Navy circle with a white number, top-left of the callout."),
        ("Caption text", "Bottom third, large, maximum eight words."),
        ("Role badge", "Top-right corner, stays on screen the whole time that role is acting."),
        ("Blur", "Blur anything that looks like real personal data."),
    ], widths=[1.5, 4.9])
    doc.add_paragraph(
        "Keep captions short. If a caption needs a second line, it belongs in the narration "
        "instead.")
    doc.add_page_break()

    # ---------------- THE SCRIPTS ----------------
    doc.add_heading("5. The scripts", level=1)
    doc.add_paragraph(
        "One section per video. Record them in order — later videos depend on records "
        "created in earlier ones.")

    for v in SERIES:
        doc.add_page_break()
        doc.add_heading(f"Video {v['num']} — {v['title']}", level=1)
        table(doc, ["Length", "Who it is for", "Watch first", "Stage"],
              [[v['dur'], v['who'], v['prereq'],
                "Set-up" if v['num'] <= 1 else f"{v['num'] - 1} of 7"]],
              widths=[0.9, 2.3, 1.5, 1.0])

        doc.add_heading("What the viewer can do afterwards", level=3)
        for g in v['goal']:
            doc.add_paragraph(g, style="List Bullet")

        doc.add_heading("Opening slide", level=3)
        embed(doc, v['map'], f"Open Video {v['num']} on this map", 5.6)

        doc.add_heading("Scenes", level=3)
        for i, sc in enumerate(v['scenes'], start=1):
            h = doc.add_paragraph()
            hr_ = h.add_run(f"Scene {v['num']}.{i} — {sc['t']}")
            hr_.bold = True; hr_.font.size = Pt(12); hr_.font.color.rgb = NAVY
            embed(doc, sc.get('img'), f"Scene {v['num']}.{i} — {sc['t']}")
            show = sc['show']
            is_live = show.strip().upper().startswith("RECORD LIVE")
            label_para(doc, "RECORD LIVE" if is_live else "SHOW",
                       show, RED if is_live else NAVY)
            label_para(doc, "SAY", f"“{sc['say']}”", GREY, italic=True)
            label_para(doc, "ON-SCREEN", sc['ost'], GREEN, bold_text=True)
            if sc.get('teach'):
                label_para(doc, "TEACH", sc['teach'], AMBER)
            doc.add_paragraph()

        doc.add_heading("How this video connects", level=3)
        table(doc, ["Comes from", "Leads to"], [[v['came'], v['goes']]], widths=[3.2, 3.2])

    # ---------------- APPENDICES ----------------
    doc.add_page_break()
    doc.add_heading("Appendix A — Demo records to use", level=1)
    doc.add_paragraph(
        "These records already exist in the training database, already in the right state. "
        "Use them so your recordings match this script.")
    table(doc, ["Record", "Where to find it", "State it is in", "Used in"], [
        ("REQ/2026/0001 — MEAL Officer (Cox's Bazar)", "MCB HR → Staff Requisitions",
         "Published, CE-approved", "V2"),
        ("Rashedul Karim (applicant)", "Recruitment → applicants",
         "Rank 1, 92 marks, Selected", "V3"),
        ("6 other candidates", "Same job position", "Ranked 2–7 with marks", "V3"),
        ("Rashedul Karim — MEAL-001", "Employees", "Active, grade Officer", "V4, V5, V6, V7"),
        ("Annual leave, 3 days", "Time Off", "Waiting for approval — use for the approve scene", "V5"),
        ("Casual leave, 1 day", "Time Off", "Fully approved — use for the 'after' scene", "V5"),
        ("Camp 12 monitoring — TA/DA", "Expenses", "62 km + overnight, per-diem applied", "V6"),
        ("Farzana Akter — SEP/2026/0003", "MCB HR → Resignations",
         "Submitted, 40 days short notice", "V8"),
    ], widths=[1.9, 1.7, 1.9, 0.9])
    doc.add_paragraph()
    p = doc.add_paragraph()
    r = p.add_run("Reset between takes:  ")
    r.bold = True
    p.add_run("if you approve something while recording and need to film it again, ask the "
              "ERP team to re-run the story script — it puts every record back to the state "
              "listed above.")

    doc.add_page_break()
    doc.add_heading("Appendix B — Words to use (and words to avoid)", level=1)
    doc.add_paragraph(
        "The audience is not technical. Say the plain word, not the software word.")
    table(doc, ["Do not say", "Say instead"], [
        ("Record", "Form, or the file"),
        ("Model / object", "(do not mention it at all)"),
        ("Kanban", "The card view / the board"),
        ("Status bar", "The steps along the top"),
        ("Chatter", "The history on the right"),
        ("Smart button", "The button at the top that counts things"),
        ("Computed field", "This fills in by itself"),
        ("Wizard", "A pop-up window"),
        ("Analytic account", "The project and donor code"),
        ("Validate", "Approve"),
        ("Configuration", "Setup"),
    ], widths=[2.4, 4.0])

    doc.add_heading("Appendix C — Before you publish, check", level=1)
    for line in [
        "The map appears in the first 15 seconds, with the right stage lit.",
        "A role badge is on screen whenever someone approves something.",
        "At least one blocked action (a rule biting) is shown.",
        "The last 15 seconds say what the next video covers.",
        "No real personal data, salary or phone number is visible.",
        "Audio is even — no scene noticeably louder than the others.",
        "Someone who has never used Odoo watched it and could repeat the steps.",
    ]:
        doc.add_paragraph(line, style="List Bullet")

    doc.add_heading("Appendix D — Subtitles", level=1)
    doc.add_paragraph(
        "Record the narration in English, then add Bangla subtitles. Most MCB field staff "
        "read Bangla faster than they follow spoken English, and subtitles also let people "
        "watch quietly in a shared office. Because the SAY text in this document is already "
        "written out word for word, it can be translated directly — you do not need to "
        "transcribe the audio afterwards.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(OUT))
    print(f"\nWrote {OUT}  ({OUT.stat().st_size:,} bytes)")

    # ---------------- VALIDATE ----------------
    re_ = Document(str(OUT))
    heads = [p.text for p in re_.paragraphs if p.style.name == "Heading 1"]
    print("Top-level sections:")
    for h in heads:
        print("   •", h)
    n_scenes = sum(len(v['scenes']) for v in SERIES)
    print(f"Videos: {len(SERIES)}  ·  Scenes: {n_scenes}")
    vids = [h for h in heads if h.startswith("Video ")]
    assert len(vids) == len(SERIES), f"expected {len(SERIES)} video sections, found {len(vids)}"
    if MISSING:
        print(f"MISSING SCREENSHOTS ({len(MISSING)}):")
        for m in sorted(set(MISSING)):
            print("   -", m)
    else:
        print("All referenced screenshots present.")
    print("Validation: OK")


if __name__ == "__main__":
    build()
