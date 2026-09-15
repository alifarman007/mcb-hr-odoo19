# -*- coding: utf-8 -*-
"""Build MCB_Open_Tender_IFT_Training_Bangla.docx — the open-tender path only.

IFT is not a separate module: it is the >5,00,000 branch of the same eleven-step
process. So this guide pulls the sessions that make up the tender path and adds an
opening section on what is DIFFERENT about a tender.
"""
import copy
import sys
sys.path.insert(0, "/Data/odoo19_enterprise/custom-addons/mcb_erp/_build")
from build_module_docx import build          # noqa: E402
from purchase_bn import SESSIONS             # noqa: E402

# the open-tender path, in order
WANTED = ["pur03_method", "pur05_opening", "pur06_technical", "pur07_comparative",
          "pur08_evaluation", "pur09_noal", "pur10_order"]

by_key = {s["key"]: s for s in SESSIONS}
sessions = []
for i, k in enumerate(WANTED, start=1):
    s = copy.deepcopy(by_key[k])
    s["no"] = i
    sessions.append(s)

IFT_POLICY = [
    ("ক. উন্মুক্ত দরপত্র (IFT) কখন — এবং তখন কী বদলায়",
     ["বিষয়", "RFQ / RFP", "উন্মুক্ত দরপত্র (IFT)"],
     [["টাকার অঙ্ক", "১০,০০০ – ৫,০০,০০০", "৫,০০,০০০ ও তার উপরে"],
      ["পদ্ধতি কে ঠিক করে", "সিস্টেম, অঙ্ক দেখে", "সিস্টেম, অঙ্ক দেখে"],
      ["ন্যূনতম দর", "৩টি", "৩টি"],
      ["কারিগরি মূল্যায়ন", "TA-1", "TA-2 (Tender)"],
      ["বিক্রেতা মূল্যায়ন", "Eval-1", "Eval-2 (Tender)"],
      ["কার্যাদেশ পত্র (NOAL)", "লাগে না", "বাধ্যতামূলক"],
      ["ক্রয়াদেশ নিশ্চিত করা", "তিনটি সই হলেই হয়",
       "তিনটি সই + ইস্যুকৃত NOAL — দুটোই লাগবে"]],
     [1.6, 2.1, 2.7]),

    ("খ. উন্মুক্ত দরপত্রের পথ — সাতটি ধাপ",
     ["ধাপ", "কী হয়", "কোন সেশনে"],
     [["১", "অঙ্ক দেখে সিস্টেম IFT ঠিক করে, NOAL Required টিক পড়ে", "সেশন ১"],
      ["২", "নির্ধারিত দিনে কমিটি দরপত্র খোলে ও লিপিবদ্ধ করে", "সেশন ২"],
      ["৩", "TA-2 — মান যাচাই, পাস/ফেল", "সেশন ৩"],
      ["৪", "তুলনামূলক বিবরণী — শুধু পাস করা দরদাতাদের দাম", "সেশন ৪"],
      ["৫", "Eval-2 — ১০০ নম্বরে মূল্যায়ন, বিজয়ী নির্বাচন", "সেশন ৫"],
      ["৬", "NOAL ইস্যু, তারপর বিক্রেতার স্বীকৃতি", "সেশন ৬"],
      ["৭", "তিনটি সই, তারপর ক্রয়াদেশ নিশ্চিত", "সেশন ৭"]],
     [0.6, 3.6, 1.2]),

    ("গ. IFT-তে সিস্টেম যেখানে সত্যিই আটকে দেয়",
     ["কোড", "কখন আটকায়", "কী বার্তা আসে"],
     [["NOAL-002", "চুক্তিমূল্য না বসিয়ে চিঠি ইস্যু", "Set the contract price"],
      ["NOAL-006", "খসড়া NOAL রেখে ক্রয়াদেশ নিশ্চিত",
       "৫,০০,০০০-এর উপরে ইস্যুকৃত কার্যাদেশ পত্র ছাড়া নিশ্চিত করা যাবে না"],
      ["PO-008", "তিনটি সই ছাড়া নিশ্চিত", "Checked → Reviewed → Approved লাগবে"],
      ["CS-005", "কারিগরিতে ফেল করা দরদাতা তুলনায়",
       "এই দরদাতা কারিগরি মূল্যায়নে পাস করেননি"],
      ["CS-002", "যথেষ্ট যোগ্য দর ছাড়া চূড়ান্তকরণ", "ন্যূনতম যোগ্য দর লাগবে"]],
     [1.0, 2.5, 2.9]),
]

IFT_QUICKREF = [
    ["দরপত্র খোলার শিট", "Purchase → MCB Procurement → Opening Sheets"],
    ["কারিগরি মূল্যায়ন (TA-2)", "MCB Procurement → Technical Analysis → Type = TA-2"],
    ["তুলনামূলক বিবরণী", "MCB Procurement → Comparative Statements"],
    ["বিজয়ী নির্বাচন (Eval-2)", "MCB Procurement → Evaluations → Type = Eval-2"],
    ["কার্যাদেশ পত্র ইস্যু", "MCB Procurement → NOAL → Issue"],
    ["বিক্রেতার স্বীকৃতি", "NOAL → Acknowledge"],
    ["চিঠি প্রিন্ট", "NOAL → Print → Notification of Award Letter"],
    ["ক্রয়াদেশ অনুমোদন", "Orders → ক্রয়াদেশ → Check / Review / Approve → Confirm"],
]

IFT_FAQ = [
    ("উন্মুক্ত দরপত্র কখন করতে হয়?",
     "৫,০০,০০০ টাকা বা তার বেশি হলে। কেউ বেছে নেয় না — চাহিদার মোট অঙ্ক বসানোর "
     "সাথে সাথে সিস্টেম নিজেই পদ্ধতিটা IFT করে দেয় আর NOAL Required ঘরে টিক দিয়ে দেয়।"),
    ("বড় ক্রয়কে দুই ভাগে ভাগ করে দরপত্র এড়ানো যায় না?",
     "যায় না, আর এটা নীতিমালার সরাসরি লঙ্ঘন। একই প্রয়োজনকে ভেঙে সীমার নিচে "
     "নামানো নিরীক্ষায় ধরা পড়ে।"),
    ("NOAL ছাড়া কি ক্রয়াদেশ দেওয়া যায়?",
     "না। চিঠি খসড়া অবস্থায় থাকলেও সিস্টেম Confirm করতে দেবে না — বার্তা আসবে "
     "NOAL-006। আগে চিঠি ইস্যু করতে হবে।"),
    ("TA-1 আর TA-2-র পার্থক্য কী?",
     "কাজ একই — মান যাচাই করে পাস বা ফেল দেওয়া। শুধু দরপত্রের ক্ষেত্রে TA-2 "
     "বেছে নিতে হয়, যাতে নথিতে বোঝা যায় এটা উন্মুক্ত দরপত্রের মূল্যায়ন ছিল।"),
    ("সবচেয়ে কম দরদাতাই কি কাজ পাবেন?",
     "না। মূল্যায়ন ১০০ নম্বরে — দাম ৪০, মান ৩০, সরবরাহ ১৫, অভিজ্ঞতা ১৫। "
     "তবে কম দর বাদ দেওয়ার কারণ নথিতে স্পষ্ট লিখে রাখতে হবে।"),
    ("দরপত্র বিজ্ঞপ্তি কি সিস্টেম থেকে প্রকাশ হয়?",
     "না। সিস্টেম দরপত্র প্রক্রিয়াটা নথিভুক্ত ও নিয়ন্ত্রণ করে — বিজ্ঞপ্তি "
     "পত্রিকায় বা ওয়েবসাইটে দেওয়া, আর জামানত (bid security) হিসাব রাখা "
     "এখনো সিস্টেমের বাইরে, হাতেই করতে হয়।"),
]

build(dict(
    sessions=sessions,
    header="মুক্তি কক্সবাজার · Odoo ১৯ — উন্মুক্ত দরপত্র (IFT) · প্রশিক্ষকের গাইড",
    title_bn="উন্মুক্ত দরপত্র (IFT)",
    title_en="Open Tender (IFT) — Trainer's Guide",
    subtitle="৫,০০,০০০ টাকার উপরে ক্রয় — দরপত্র খোলা থেকে ক্রয়াদেশ পর্যন্ত",
    story_line="উদাহরণ: ক্যাম্প লার্নিং সেন্টার সংস্কার · ৬,৫০,০০০ টাকা · NOAL বাধ্যতামূলক",
    policy=IFT_POLICY,
    quickref=IFT_QUICKREF,
    faq=IFT_FAQ,
    agenda_note="এটি ক্রয় মডিউলের পূর্ণ গাইড থেকে শুধু উন্মুক্ত দরপত্রের পথটুকু নিয়ে "
                "তৈরি। চাহিদাপত্র তোলা ও অনুমোদনের ধাপ (পূর্ণ গাইডের সেশন ১ ও ২) "
                "সব পদ্ধতিতেই এক, তাই এখানে রাখা হয়নি — প্রয়োজনে সেগুলো আগে "
                "দেখিয়ে নিন। ভিডিওগুলো mukticox/video_purchase ফোল্ডারে।",
    out="/Data/odoo19_enterprise/mukticox/MCB_Open_Tender_IFT_Training_Bangla.docx",
))
