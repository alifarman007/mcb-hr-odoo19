# -*- coding: utf-8 -*-
"""Build MCB_Purchase_Training_Guide_Bangla.docx"""
import sys
sys.path.insert(0, "/Data/odoo19_enterprise/custom-addons/mcb_erp/_build")
from build_module_docx import build          # noqa: E402
from purchase_bn import SESSIONS             # noqa: E402
from module_facts import (PURCHASE_POLICY, PURCHASE_QUICKREF,
                          PURCHASE_FAQ)      # noqa: E402

build(dict(
    sessions=SESSIONS,
    header="মুক্তি কক্সবাজার · Odoo ১৯ — ক্রয় মডিউল · প্রশিক্ষকের গাইড",
    title_bn="ক্রয় ও সংগ্রহ মডিউল",
    title_en="Purchase & Procurement — Trainer's Guide",
    subtitle="চাহিদা থেকে ক্রয়াদেশ — এগারো ধাপের পুরো পথ, বারোটি সেশনে",
    story_line="উদাহরণ: GBViE প্রকল্পের জন্য টিউবওয়েল স্থাপন · ৪,০৮,০০০ টাকা · তিনটি দর",
    policy=PURCHASE_POLICY,
    quickref=PURCHASE_QUICKREF,
    faq=PURCHASE_FAQ,
    agenda_note="প্রস্তাব: দিন ১ — সেশন ১–৪ (চাহিদা ও দর চাওয়া) · দিন ২ — সেশন ৫–৮ "
                "(খোলা, যাচাই, তুলনা, নির্বাচন) · দিন ৩ — সেশন ৯–১২ (কার্যাদেশ, "
                "ক্রয়াদেশ, চেকলিস্ট, প্রতিবেদন)। প্রতিটি সেশনের জন্য একটি করে ভিডিও "
                "আছে mukticox/video_purchase ফোল্ডারে।",
    out="/Data/odoo19_enterprise/mukticox/MCB_Purchase_Training_Guide_Bangla.docx",
))
