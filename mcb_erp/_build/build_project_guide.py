# -*- coding: utf-8 -*-
"""Build MCB_Project_Training_Guide_Bangla.docx"""
import sys
sys.path.insert(0, "/Data/odoo19_enterprise/custom-addons/mcb_erp/_build")
from build_module_docx import build         # noqa: E402
from project_bn import SESSIONS             # noqa: E402
from module_facts import (PROJECT_POLICY, PROJECT_QUICKREF,
                          PROJECT_FAQ)      # noqa: E402

build(dict(
    sessions=SESSIONS,
    header="মুক্তি কক্সবাজার · Odoo ১৯ — প্রকল্প মডিউল · প্রশিক্ষকের গাইড",
    title_bn="প্রকল্প ব্যবস্থাপনা মডিউল",
    title_en="Project Management — Trainer's Guide",
    subtitle="প্রকল্প খোলা থেকে সমাপ্তি — দশটি সেশনে",
    story_line="উদাহরণ: GBViE প্রকল্প · CARE-এর অর্থায়নে · উখিয়ার ক্যাম্প ৪, ১২ ও ১৯",
    policy=PROJECT_POLICY,
    quickref=PROJECT_QUICKREF,
    faq=PROJECT_FAQ,
    agenda_note="প্রস্তাব: দিন ১ — সেশন ১–৩ (প্রকল্প, কাজের ভাগ, মাইলফলক) · দিন ২ — "
                "সেশন ৪–৭ (বরাদ্দ, টাইমশিট, হাজিরা, ভ্রমণ; এর মধ্যে সেশন ৫ ও ৭ সব "
                "কর্মীর জন্য) · দিন ৩ — সেশন ৮–১০ (সুবিধাভোগী, রিপোর্ট, সমাপ্তি)। "
                "ভিডিওগুলো আছে mukticox/video_project ফোল্ডারে।",
    out="/Data/odoo19_enterprise/mukticox/MCB_Project_Training_Guide_Bangla.docx",
))
