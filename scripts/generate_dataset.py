import json, random, re, math, itertools, collections
random.seed(2026)

SYS_VARIANTS = [
 "You are a logical business strategist and behavioral-economics advisor. You understand Bangla and English (and mixed Banglish) and reply in the user's language. Always reason step by step (বিশ্লেষণ), then give a clear recommendation (সুপারিশ), then risks and next steps (ঝুঁকি ও পরবর্তী পদক্ষেপ). Use real frameworks and numbers, never invent social proof.",
 "You are an expert business strategist who combines first-principles thinking, unit economics, and consumer psychology. Reply in the same language the user writes in (Bangla, English or Banglish). Show your reasoning step by step before recommending. Be honest about assumptions and never suggest deceptive tactics.",
 "তুমি একজন লজিক্যাল বিজনেস স্ট্র্যাটেজিস্ট, যে বিজনেস সাইকোলজি ও ইউনিট ইকোনমিকস বোঝে। ব্যবহারকারী যে ভাষায় (বাংলা/English/Banglish) লেখে সেই ভাষায় উত্তর দাও। আগে ধাপে ধাপে বিশ্লেষণ, তারপর সুপারিশ, তারপর ঝুঁকি। প্রতারণামূলক কৌশল কখনো সুপারিশ করো না।",
]

BNMAP = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")

def grp(n):
    s = str(int(round(abs(n))))
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        head = re.sub(r'(\d)(?=(\d\d)+$)', r'\1,', head)
        s = head + "," + tail
    return ("-" if n < 0 else "") + s

class F:
    def __init__(s, lang):
        s.lang = lang; s.bn = lang == "bn"; s.en = lang == "en"
        s.f = 1 if s.en else 100
    def d(s, t): return str(t).translate(BNMAP) if s.bn else str(t)
    def n(s, x, dec=1):
        t = f"{x:.{dec}f}"
        if "." in t: t = t.rstrip("0").rstrip(".")
        return s.d(t)
    def m(s, x):
        sign = "-" if x < 0 else ""; x = abs(int(round(x)))
        t = ("$" + f"{x:,}") if s.en else ("৳" + grp(x))
        return s.d(sign + t)
    def mb(s, x):  # always taka
        sign = "-" if x < 0 else ""; x = abs(int(round(x)))
        return s.d(sign + "৳" + grp(x))
    def p(s, x, dec=0): return s.n(x, dec) + "%"
    def t(s, en, bn): return en if s.en else bn
    def st(s, i): return s.d(f"{i}.")

H1, H2, H3 = "## বিশ্লেষণ (Step-by-step)", "## সুপারিশ", "## ঝুঁকি ও পরবর্তী পদক্ষেপ"

def pick_lang():
    return random.choices(["en", "bn", "mixed"], weights=[35, 35, 30])[0]

CTX = [("photography package", "ফটোগ্রাফি প্যাকেজ", "photography package"), ("annual software plan", "বার্ষিক সফটওয়্যার প্ল্যান", "annual software plan"),
       ("product", "প্রোডাক্ট", "product"), ("online course", "অনলাইন কোর্স", "online course"), ("video project", "ভিডিও প্রজেক্ট", "video project")]

# ---------------------------------------------------------------- 1 LTV/CAC
def g_ltv(lang):
    x = F(lang); f = x.f
    arpu = random.choice([9, 15, 20, 29, 39, 49, 59, 79, 99, 149]) * f
    gm = random.choice([60, 65, 70, 75, 80, 85]); ch = random.choice([2, 3, 4, 5, 6, 8, 10])
    cac = random.choice([60, 90, 120, 150, 200, 300, 400, 600, 900]) * f
    life = 100 / ch; gp = arpu * gm / 100; ltv = gp * life; r = ltv / cac; pb = cac / gp
    ch2 = ch * 0.7; ltv2 = gp * 100 / ch2
    if r < 1: ve, vb, re_, rb = "you lose money on every customer", "প্রতিটা কাস্টমারে আপনি ক্ষতিতে আছেন", "Stop scaling spend. Fix churn, pricing or CAC first.", "খরচ বাড়ানো বন্ধ রাখুন। আগে churn, প্রাইসিং বা CAC ঠিক করুন।"
    elif r < 3: ve, vb, re_, rb = "viable but fragile", "টিকে থাকার মতো, কিন্তু দুর্বল", "Do not scale ad spend yet. Raise retention and activation first.", "এখনই অ্যাড খরচ বাড়াবেন না। আগে retention ও activation বাড়ান।"
    elif r <= 5: ve, vb, re_, rb = "healthy", "সুস্থ", "Scale gradually while watching payback and cohort churn.", "ধীরে ধীরে স্কেল করুন, payback ও cohort churn নজরে রেখে।"
    else: ve, vb, re_, rb = "very strong, possibly under-investing in growth", "খুব শক্তিশালী, সম্ভবত গ্রোথে কম বিনিয়োগ হচ্ছে", "Test higher acquisition spend; your economics can afford it.", "অ্যাকুইজিশন খরচ বাড়িয়ে টেস্ট করুন; আপনার ইকোনমিকস তা সইতে পারবে।"
    if pb > 18: pe, pbn = "Payback is long; growth will need outside cash.", "Payback অনেক দীর্ঘ; গ্রোথের জন্য বাইরের ক্যাশ লাগবে।"
    elif pb > 12: pe, pbn = "Payback is borderline; watch cash closely.", "Payback সীমারেখায়; ক্যাশ কড়া নজরে রাখুন।"
    else: pe, pbn = "Payback is comfortable.", "Payback স্বস্তিদায়ক।"
    if lang == "en":
        u = random.choice([f"My subscription business has ARPU {x.m(arpu)}/month, {gm}% gross margin, {ch}% monthly churn and CAC of {x.m(cac)}. Is this healthy?",
                           f"Check my unit economics: ARPU {x.m(arpu)}, gross margin {gm}%, churn {ch}% per month, CAC {x.m(cac)}. Should I scale?"])
    elif lang == "bn":
        u = random.choice([f"আমার সাবস্ক্রিপশন বিজনেসে ARPU মাসে {x.m(arpu)}, gross margin {x.d(gm)}%, মাসিক churn {x.d(ch)}%, আর CAC {x.m(cac)}। ইউনিট ইকোনমিকস ঠিক আছে?",
                           f"ARPU {x.m(arpu)}, gross margin {x.d(gm)}%, মাসিক churn {x.d(ch)}%, CAC {x.m(cac)} — এখন কি স্কেল করা উচিত?"])
    else:
        u = random.choice([f"amar SaaS er ARPU {x.m(arpu)}/month, gross margin {gm}%, churn {ch}%, CAC {x.m(cac)}. scale korbo naki age fix korbo?",
                           f"unit economics ta ektu dekho: ARPU {x.m(arpu)}, CAC {x.m(cac)}, churn {ch}% monthly, margin {gm}%. ok ache?"])
    if lang == "en":
        a = f"""{H1}
1. **Lifetime:** 1 ÷ {x.p(ch)} monthly churn = {x.n(life)} months.
2. **Gross profit per month:** {x.m(arpu)} × {x.p(gm)} = {x.m(gp)}.
3. **LTV:** {x.m(gp)} × {x.n(life)} = **{x.m(ltv)}**.
4. **LTV:CAC:** {x.m(ltv)} ÷ {x.m(cac)} = **{x.n(r)}:1**. A common benchmark is 3:1 or better, so this is {ve}.
5. **CAC payback:** {x.m(cac)} ÷ {x.m(gp)} = **{x.n(pb)} months**. {pe}
6. **Biggest lever:** cutting churn by 30% (to {x.p(ch2, 1)}) lifts LTV to {x.m(ltv2)}, a {x.p((ltv2 / ltv - 1) * 100)} gain.

{H2}
{re_} Run a cohort retention table before deciding, because averages hide early-life churn.

{H3}
The formula assumes steady churn and stable ARPU. If most churn happens in month 1-2, it is an onboarding problem. Next step: build a retention curve per signup month and interview 10 churned users."""
    else:
        a = f"""{H1}
১. **Lifetime:** ১ ÷ {x.p(ch)} মাসিক churn = {x.n(life)} মাস।
২. **মাসিক gross profit:** {x.m(arpu)} × {x.p(gm)} = {x.m(gp)}।
৩. **LTV:** {x.m(gp)} × {x.n(life)} = **{x.m(ltv)}**।
৪. **LTV:CAC:** {x.m(ltv)} ÷ {x.m(cac)} = **{x.n(r)}:১**। সাধারণ বেঞ্চমার্ক ৩:১ বা বেশি, অর্থাৎ আপনার অবস্থা: {vb}।
৫. **CAC payback:** {x.m(cac)} ÷ {x.m(gp)} = **{x.n(pb)} মাস**। {pbn}
৬. **সবচেয়ে বড় লিভার:** churn ৩০% কমালে ({x.p(ch2, 1)}) LTV হবে {x.m(ltv2)}, মানে {x.p((ltv2 / ltv - 1) * 100)} বৃদ্ধি।

{H2}
{rb} সিদ্ধান্তের আগে cohort retention টেবিল বানান, কারণ গড় সংখ্যা শুরুর দিকের churn লুকিয়ে রাখে।

{H3}
এই হিসাব ধরে নেয় churn ও ARPU স্থির থাকবে। বেশিরভাগ churn প্রথম ১-২ মাসে হলে সমস্যা onboarding এ। পরবর্তী ধাপ: প্রতি signup মাসের retention curve বানান এবং ১০ জন churned ইউজারের সাথে কথা বলুন।"""
    return u, a, "ltv_cac"

# ---------------------------------------------------------------- 2 Runway
def rnd(v, step): return int(round(v / step) * step)
def g_runway(lang):
    x = F(lang)
    cash = random.choice([10, 15, 20, 30, 40, 60, 100]) * 100000 if not x.en else random.choice([50, 80, 120, 200, 300]) * 1000
    exp = rnd(cash * random.choice([0.06, 0.08, 0.1, 0.15, 0.2]), 10000 if not x.en else 1000)
    rev = rnd(exp * random.choice([0.2, 0.4, 0.6, 0.8, 1.0, 1.2]), 10000 if not x.en else 1000)
    net = exp - rev
    if net <= 0:
        verdict_en = "You are already cash-flow positive, so runway is not your constraint."
        verdict_bn = "আপনি ইতিমধ্যে cash-flow positive, তাই runway এখন আপনার সীমাবদ্ধতা নয়।"
        ru = None
    else:
        ru = cash / net; cut = exp * 0.2; net2 = net - cut
        ru2 = cash / net2 if net2 > 0 else None
    if lang == "en":
        u = random.choice([f"Cash in bank {x.m(cash)}, monthly expenses {x.m(exp)}, monthly revenue {x.m(rev)}. What is my runway and what should I do?",
                           f"We have {x.m(cash)} cash, spend {x.m(exp)} a month and earn {x.m(rev)}. How worried should I be?"])
    elif lang == "bn":
        u = random.choice([f"ব্যাংকে ক্যাশ {x.m(cash)}, মাসিক খরচ {x.m(exp)}, মাসিক রেভিনিউ {x.m(rev)}। আমার runway কত আর কী করা উচিত?",
                           f"আমাদের হাতে {x.m(cash)}, মাসে খরচ {x.m(exp)}, আয় {x.m(rev)}। কতটা চিন্তার কারণ আছে?"])
    else:
        u = random.choice([f"cash {x.m(cash)}, monthly expense {x.m(exp)}, revenue {x.m(rev)}. runway koto? ki korbo?",
                           f"amader kache {x.m(cash)} ache, mash e kharoch {x.m(exp)}, income {x.m(rev)}. tension er kisu ache?"])
    if net <= 0:
        if lang == "en":
            a = f"""{H1}
1. **Net burn:** {x.m(exp)} − {x.m(rev)} = {x.m(net)} (negative means surplus of {x.m(-net)} per month).
2. {verdict_en}
3. With {x.m(cash)} in reserve you hold {x.n(cash / exp)} months of full expenses even if revenue vanished.

{H2}
Keep at least 6 months of expenses as a reserve, then reinvest the surplus into the channel with the best payback. Avoid raising money you do not need on bad terms.

{H3}
Revenue concentration is the hidden risk: if one client is most of the revenue, the real runway is shorter. Next step: list revenue by client and stress-test losing the biggest one."""
        else:
            a = f"""{H1}
১. **Net burn:** {x.m(exp)} − {x.m(rev)} = {x.m(net)} (ঋণাত্মক মানে প্রতি মাসে {x.m(-net)} উদ্বৃত্ত)।
২. {verdict_bn}
৩. {x.m(cash)} রিজার্ভ থাকায় রেভিনিউ শূন্য হলেও আপনি {x.n(cash / exp)} মাসের পুরো খরচ চালাতে পারবেন।

{H2}
কমপক্ষে ৬ মাসের খরচ রিজার্ভ রাখুন, বাকি উদ্বৃত্ত সবচেয়ে ভালো payback এর চ্যানেলে বিনিয়োগ করুন। দরকার নেই এমন ফান্ড খারাপ শর্তে তুলবেন না।

{H3}
লুকানো ঝুঁকি হলো রেভিনিউ কনসেনট্রেশন: একজন ক্লায়েন্ট বেশিরভাগ আয় দিলে আসল runway ছোট। পরবর্তী ধাপ: ক্লায়েন্টভিত্তিক রেভিনিউ লিস্ট করুন এবং সবচেয়ে বড় ক্লায়েন্ট হারালে কী হয় তা দেখুন।"""
        return u, a, "runway"
    if ru < 6: sev_en, sev_bn = "critical: you must act now", "জরুরি: এখনই পদক্ষেপ নিতে হবে"
    elif ru < 12: sev_en, sev_bn = "cautionary: act within weeks", "সতর্কতার পর্যায়: কয়েক সপ্তাহের মধ্যে কাজ শুরু করুন"
    else: sev_en, sev_bn = "reasonably safe, but keep monitoring", "মোটামুটি নিরাপদ, তবে নজর রাখুন"
    c2e = (f"With a 20% expense cut ({x.m(cut)}), net burn becomes {x.m(net2)} and runway {x.n(ru2)} months." if ru2 else f"A 20% expense cut ({x.m(cut)}) would make you break-even.")
    c2b = (f"খরচ ২০% কমালে ({x.m(cut)}) net burn হবে {x.m(net2)}, runway {x.n(ru2)} মাস।" if ru2 else f"খরচ ২০% কমালে ({x.m(cut)}) আপনি break-even এ পৌঁছাবেন।")
    if lang == "en":
        a = f"""{H1}
1. **Net burn:** {x.m(exp)} − {x.m(rev)} = **{x.m(net)} per month**.
2. **Runway:** {x.m(cash)} ÷ {x.m(net)} = **{x.n(ru)} months**, which is {sev_en}.
3. **Fundraising reality:** raising money often takes 3-6 months from first meeting to cash. A short runway weakens your BATNA and your negotiating position.
4. **Cut scenario:** {c2e}

{H2}
Target 10-12 months of runway: (a) cut expenses that do not touch revenue or the core product, (b) bring in cash faster through pre-sales or services, (c) run fundraising in parallel but do not depend on it.

{H3}
Cutting too deep stalls growth, so protect anything directly tied to revenue. Update runway monthly and decide in advance what you will cut if it falls below 3 months."""
    else:
        a = f"""{H1}
১. **Net burn:** {x.m(exp)} − {x.m(rev)} = **মাসে {x.m(net)}**।
২. **Runway:** {x.m(cash)} ÷ {x.m(net)} = **{x.n(ru)} মাস**, যা {sev_bn}।
৩. **ফান্ডরেইজিং বাস্তবতা:** প্রথম মিটিং থেকে টাকা হাতে আসতে সাধারণত ৩-৬ মাস লাগে। ছোট runway আপনার BATNA ও দর-কষাকষির ক্ষমতা দুর্বল করে।
৪. **খরচ কমানোর দৃশ্যপট:** {c2b}

{H2}
১০-১২ মাসের runway লক্ষ্য করুন: (ক) রেভিনিউ বা কোর প্রোডাক্টের সাথে সম্পর্কহীন খরচ কাটুন, (খ) pre-sale বা সার্ভিস দিয়ে দ্রুত ক্যাশ আনুন, (গ) ফান্ডরেইজিং সমান্তরালে চালান কিন্তু এর ওপর নির্ভর করবেন না।

{H3}
বেশি কাটলে গ্রোথ থেমে যাবে, তাই রেভিনিউ-সংশ্লিষ্ট খরচ রক্ষা করুন। প্রতি মাসে runway আপডেট করুন এবং ৩ মাসের নিচে নামলে কী কাটবেন তা আগে থেকে ঠিক করে রাখুন।"""
    return u, a, "runway"

# ---------------------------------------------------------------- 3 Decision EV
def g_ev(lang):
    x = F(lang)
    I = random.choice([5, 10, 15, 20]) * 100000 if not x.en else random.choice([10, 20, 50]) * 1000
    G = I * random.choice([2, 3, 4]); p = random.choice([0.2, 0.3, 0.4, 0.5, 0.6])
    S = I * random.choice([0.3, 0.5, 0.7]); q = random.choice([0.8, 0.9, 0.95]); C = I * random.choice([2, 3, 5, 8])
    evA = p * G - (1 - p) * I; evB = q * S; pstar = I / (G + I) * 100; ratio = I / C * 100
    if evA <= evB: dec = "B"
    elif ratio <= 30: dec = "A"
    else: dec = "pilot"
    if lang == "en":
        u = f"Option A: launch a new venture costing {x.m(I)}; {x.p(p * 100)} chance of success with a net gain of {x.m(G)}, otherwise I lose the {x.m(I)}. Option B: a safe upsell with a {x.p(q * 100)} chance of {x.m(S)} profit. I have {x.m(C)} in cash. Which one?"
    elif lang == "bn":
        u = f"অপশন A: {x.m(I)} খরচে নতুন উদ্যোগ; সফল হওয়ার সম্ভাবনা {x.p(p * 100)}, সফল হলে নেট লাভ {x.m(G)}, নইলে {x.m(I)} ক্ষতি। অপশন B: নিরাপদ আপসেল, {x.p(q * 100)} সম্ভাবনায় {x.m(S)} লাভ। আমার ক্যাশ আছে {x.m(C)}। কোনটা নেব?"
    else:
        u = f"A option: {x.m(I)} invest, {p * 100:.0f}% success chance, success hole profit {x.m(G)}, fail hole {x.m(I)} loss. B option: safe upsell, {q * 100:.0f}% chance e {x.m(S)} profit. cash ache {x.m(C)}. kon ta nibo?"
    recs_en = {"B": f"Take B. Option A has a lower expected value ({x.m(evA)} vs {x.m(evB)}), so it does not compensate for its risk.",
               "A": f"Take A, but validate the {x.p(p * 100)} assumption with a small pilot first. The loss ({x.p(ratio)} of cash) is survivable and the expected value is higher.",
               "pilot": f"A has the higher expected value, but a loss of {x.m(I)} would be {x.p(ratio)} of your cash, which is dangerous. Run a small pilot or do B first to build the reserve, then take A."}
    recs_bn = {"B": f"B নিন। A এর expected value কম ({x.m(evA)} বনাম {x.m(evB)}), তাই ঝুঁকির বিনিময়ে যথেষ্ট প্রতিদান নেই।",
               "A": f"A নিন, তবে আগে ছোট পাইলটে {x.p(p * 100)} সম্ভাবনার অনুমান যাচাই করুন। সম্ভাব্য ক্ষতি আপনার ক্যাশের {x.p(ratio)}, যা সামলানো যায়, আর expected value বেশি।",
               "pilot": f"A এর expected value বেশি, কিন্তু {x.m(I)} হারালে তা ক্যাশের {x.p(ratio)} যা বিপজ্জনক। ছোট পাইলট করুন, অথবা আগে B করে রিজার্ভ বাড়িয়ে তারপর A নিন।"}
    if lang == "en":
        a = f"""{H1}
1. **Option A:** EV = ({x.p(p * 100)} × {x.m(G)}) + ({x.p((1 - p) * 100)} × −{x.m(I)}) = **{x.m(evA)}**.
2. **Option B:** EV = {x.p(q * 100)} × {x.m(S)} = **{x.m(evB)}**.
3. **Break-even probability for A:** EV = 0 at p = {x.m(I)} ÷ ({x.m(G)} + {x.m(I)}) = **{x.p(pstar, 1)}**. Your estimate is {x.p(p * 100)}.
4. **Survivability:** the downside of A is {x.p(ratio)} of cash. Expected value alone is not the decision; ruin risk matters.

{H2}
{recs_en[dec]}

{H3}
The probabilities are your estimates, not facts. Ask how you arrived at {x.p(p * 100)} and write the success criteria for the pilot before you start (for example, a measurable result in 30 days)."""
    else:
        a = f"""{H1}
১. **অপশন A:** EV = ({x.p(p * 100)} × {x.m(G)}) + ({x.p((1 - p) * 100)} × −{x.m(I)}) = **{x.m(evA)}**।
২. **অপশন B:** EV = {x.p(q * 100)} × {x.m(S)} = **{x.m(evB)}**।
৩. **A এর break-even সম্ভাবনা:** EV = ০ হয় p = {x.m(I)} ÷ ({x.m(G)} + {x.m(I)}) = **{x.p(pstar, 1)}** এ। আপনার অনুমান {x.p(p * 100)}।
৪. **টিকে থাকার ক্ষমতা:** A এর ক্ষতি ক্যাশের {x.p(ratio)}। শুধু expected value দিয়ে সিদ্ধান্ত নেওয়া যায় না; ব্যবসা ডুবে যাওয়ার ঝুঁকিও দেখতে হবে।

{H2}
{recs_bn[dec]}

{H3}
সম্ভাবনাগুলো আপনার অনুমান, তথ্য নয়। {x.p(p * 100)} কীভাবে পেলেন তা প্রশ্ন করুন এবং শুরুর আগে পাইলটের সাফল্যের মাপকাঠি লিখে রাখুন (যেমন ৩০ দিনে পরিমাপযোগ্য ফলাফল)।"""
    return u, a, "decision_ev"

# ---------------------------------------------------------------- 4 Discount math
def g_discount(lang):
    x = F(lang)
    price = random.choice([800, 1500, 3000, 12000, 50000, 150000]) if not x.en else random.choice([20, 49, 99, 500, 2000])
    cf = random.choice([0.3, 0.4, 0.5, 0.6, 0.7]); c = price * cf; d = random.choice([10, 15, 20, 25, 30, 40])
    ctx = random.choice(CTX)
    old = price - c; newp = price * (1 - d / 100); new = newp - c
    never = new <= 0
    mult = old / new if not never else None
    if lang == "en":
        u = random.choice([f"A customer wants {d}% off my {ctx[0]} priced at {x.m(price)} (my cost is {x.m(c)}). How much extra volume do I need to make up for it?",
                           f"Should I give a {d}% discount on a {x.m(price)} {ctx[0]} that costs me {x.m(c)}? Run the numbers."])
    elif lang == "bn":
        u = f"আমার {ctx[1]} এর দাম {x.m(price)}, খরচ {x.m(c)}। ক্লায়েন্ট {x.d(d)}% ডিসকাউন্ট চাইছে। লোকসান পুষিয়ে নিতে কতটা বাড়তি বিক্রি লাগবে?"
    else:
        u = f"{ctx[1]} er price {x.m(price)}, cost {x.m(c)}. client {d}% discount chaay. dile koto beshi sales lagbe?"
    if never:
        calc_en = f"After {d}% off the price is {x.m(newp)}, below your cost of {x.m(c)}. No volume increase can fix a negative margin."
        calc_bn = f"{x.d(d)}% ছাড়ের পর দাম {x.m(newp)}, যা আপনার খরচ {x.m(c)} এর নিচে। ঋণাত্মক মার্জিন কোনো বাড়তি ভলিউমে পুষবে না।"
    else:
        calc_en = f"New margin per unit: {x.m(newp)} − {x.m(c)} = {x.m(new)}. To earn the same total profit you need {x.n(mult)}× the volume, i.e. **{x.p((mult - 1) * 100)} more sales**."
        calc_bn = f"নতুন মার্জিন: {x.m(newp)} − {x.m(c)} = {x.m(new)}। একই মোট লাভের জন্য {x.n(mult)} গুণ বিক্রি লাগবে, অর্থাৎ **{x.p((mult - 1) * 100)} বেশি বিক্রি**।"
    if lang == "en":
        a = f"""{H1}
1. **Current margin per unit:** {x.m(price)} − {x.m(c)} = {x.m(old)} ({x.p(old / price * 100)} of price).
2. **After {d}% discount:** {calc_en}
3. **Think in value, not price:** a discount permanently trains the customer to expect it, while a scope or terms change protects your price anchor.

{H2}
Do not give a blanket discount. Offer conditional trades: a smaller discount for 50% advance payment, a leaner scope at a lower price, a bundle with a real add-on, or a time-limited offer that is genuinely time-limited.

{H3}
The customer may walk away, which can be the right outcome if volume will not rise. Decide your walk-away price (the lowest price that still earns an acceptable margin) before the conversation starts."""
    else:
        a = f"""{H1}
১. **বর্তমান মার্জিন:** {x.m(price)} − {x.m(c)} = {x.m(old)} (দামের {x.p(old / price * 100)})।
২. **{x.d(d)}% ছাড়ের পর:** {calc_bn}
৩. **দাম নয়, ভ্যালু নিয়ে ভাবুন:** ডিসকাউন্ট গ্রাহককে সবসময় ছাড় আশা করতে শেখায়, আর scope বা শর্ত বদলালে আপনার প্রাইস anchor অক্ষত থাকে।

{H2}
সরাসরি ছাড় দেবেন না। শর্তসাপেক্ষ বিনিময় দিন: ৫০% advance এর বিনিময়ে ছোট ছাড়, কম scope এ কম দাম, আসল অ্যাড-অনসহ বান্ডল, অথবা সত্যিই সীমিত সময়ের অফার।

{H3}
গ্রাহক চলে যেতে পারেন, আর ভলিউম না বাড়লে সেটাই সঠিক ফল। আলোচনার আগে আপনার walk-away price (যে সর্বনিম্ন দামে গ্রহণযোগ্য মার্জিন থাকে) ঠিক করে নিন।"""
    return u, a, "discount_math"

# ---------------------------------------------------------------- 5 Breakeven
def g_breakeven(lang):
    x = F(lang)
    Fx = random.choice([50000, 100000, 200000, 500000]) if not x.en else random.choice([1000, 3000, 5000, 10000])
    price = random.choice([500, 1200, 2500, 5000]) if not x.en else random.choice([10, 25, 60, 150])
    v = price * random.choice([0.3, 0.4, 0.5, 0.6]); cm = price - v
    units = math.ceil(Fx / cm); T = Fx * 0.5; unitsT = math.ceil((Fx + T) / cm)
    if lang == "en":
        u = f"Fixed costs are {x.m(Fx)} a month. I sell at {x.m(price)} with {x.m(v)} variable cost per unit. What is my break-even?"
    elif lang == "bn":
        u = f"আমার মাসিক fixed cost {x.m(Fx)}। প্রতি ইউনিট বিক্রয়মূল্য {x.m(price)}, variable cost {x.m(v)}। break-even কত?"
    else:
        u = f"fixed cost {x.m(Fx)}/month, price {x.m(price)}, variable cost {x.m(v)} per unit. break-even koto unit?"
    if lang == "en":
        a = f"""{H1}
1. **Contribution margin per unit:** {x.m(price)} − {x.m(v)} = {x.m(cm)} ({x.p(cm / price * 100)}).
2. **Break-even units:** {x.m(Fx)} ÷ {x.m(cm)} = **{units} units/month** (about {x.n(units / 30)} per day).
3. **Break-even revenue:** {units} × {x.m(price)} = {x.m(units * price)}.
4. **To earn a profit of {x.m(T)} a month:** ({x.m(Fx)} + {x.m(T)}) ÷ {x.m(cm)} = **{unitsT} units**.

{H2}
Judge feasibility with your acquisition numbers: can you realistically sell {units} units a month with your current traffic and conversion? If not, raise price, lower variable cost, or cut fixed cost before spending more on marketing.

{H3}
Break-even assumes constant prices and costs. Check your real conversion rate and CAC, since marketing spend is usually a fixed cost too. Next step: model best, base and worst case for the next 6 months."""
    else:
        a = f"""{H1}
১. **প্রতি ইউনিট contribution margin:** {x.m(price)} − {x.m(v)} = {x.m(cm)} ({x.p(cm / price * 100)})।
২. **Break-even ইউনিট:** {x.m(Fx)} ÷ {x.m(cm)} = **মাসে {x.d(units)} ইউনিট** (দিনে প্রায় {x.n(units / 30)})।
৩. **Break-even রেভিনিউ:** {x.d(units)} × {x.m(price)} = {x.m(units * price)}।
৪. **মাসে {x.m(T)} লাভ করতে হলে:** ({x.m(Fx)} + {x.m(T)}) ÷ {x.m(cm)} = **{x.d(unitsT)} ইউনিট**।

{H2}
আপনার ট্রাফিক ও conversion দিয়ে মাসে {x.d(units)} ইউনিট বিক্রি করা বাস্তবসম্মত কি না যাচাই করুন। না হলে মার্কেটিং খরচ বাড়ানোর আগে দাম বাড়ান, variable cost কমান বা fixed cost ছাঁটুন।

{H3}
Break-even ধরে নেয় দাম ও খরচ স্থির। আসল conversion rate ও CAC দেখুন, কারণ মার্কেটিং খরচও সাধারণত fixed cost। পরবর্তী ধাপ: আগামী ৬ মাসের best, base ও worst case মডেল বানান।"""
    return u, a, "breakeven"

# ---------------------------------------------------------------- 6 COD returns
def g_cod(lang):
    x = F(lang); N = 100
    aov = random.choice([800, 1200, 1500, 2000, 3000]); mm = random.choice([0.3, 0.35, 0.4, 0.45])
    r = random.choice([0.2, 0.25, 0.3, 0.35, 0.4, 0.45]); out = random.choice([60, 80, 100, 120]); ret = random.choice([60, 80, 100]); pkg = random.choice([10, 15, 20, 25])
    def prof(n, rr): return n * (1 - rr) * aov * mm - n * (out + pkg) - n * rr * ret
    p1 = prof(N, r); r2 = r * 0.6; N2 = N * 0.9; p2 = prof(N2, r2)
    if lang == "en":
        u = f"My Facebook shop gets 100 COD orders per batch. Average order {x.mb(aov)}, product margin {x.p(mm * 100)}, return rate {x.p(r * 100)}, outbound courier cost {x.mb(out)}, return courier cost {x.mb(ret)}, packaging {x.mb(pkg)} per order. Is it worth asking for advance delivery charge?"
    elif lang == "bn":
        u = f"আমার F-commerce পেজে প্রতি ব্যাচে ১০০টা COD অর্ডার। গড় অর্ডার {x.mb(aov)}, প্রোডাক্ট মার্জিন {x.p(mm * 100)}, রিটার্ন রেট {x.p(r * 100)}, কুরিয়ার (যাওয়া) {x.mb(out)}, রিটার্ন কুরিয়ার {x.mb(ret)}, প্যাকেজিং {x.mb(pkg)}। ডেলিভারি চার্জ advance নেওয়া কি লাভজনক হবে?"
    else:
        u = f"100 ta COD order e avg order {x.mb(aov)}, margin {mm * 100:.0f}%, return rate {r * 100:.0f}%, courier {x.mb(out)} + return {x.mb(ret)}, packaging {x.mb(pkg)}. advance delivery charge nile laabh hobe?"
    better = p2 > p1
    if lang == "en":
        a = f"""{H1}
1. **Today (100 orders):** delivered {x.n(N * (1 - r), 0)} × {x.mb(aov)} × {x.p(mm * 100)} margin = {x.mb(N * (1 - r) * aov * mm)}. Minus courier and packaging {x.mb(N * (out + pkg))} and return-leg cost {x.mb(N * r * ret)}. **Net profit: {x.mb(p1)}.**
2. **Scenario with advance delivery charge:** assume 10% of buyers drop off ({x.n(N2, 0)} orders) and returns fall by 40% to {x.p(r2 * 100, 1)} (commitment effect). Net profit: **{x.mb(p2)}**.
3. **Comparison:** {x.mb(p2)} vs {x.mb(p1)}, a difference of {x.mb(p2 - p1)} per 100 visitors who would have ordered.
4. **Psychology:** a small upfront payment creates commitment, so the order is no longer free for the buyer to cancel.

{H2}
{'Test the advance model: the assumptions favor it.' if better else 'The assumptions do not favor advance payment here; first try order-confirmation calls and clearer product photos, and test again.'} The 10% drop-off and 40% return reduction are assumptions, so run an A/B test on real traffic.

{H3}
Measure net profit per 100 interested buyers, not just order count. Track return reasons for 2 weeks (wrong size, fake order, delayed delivery) because the fix depends on the cause."""
    else:
        a = f"""{H1}
১. **বর্তমান (১০০ অর্ডার):** ডেলিভারি হয় {x.n(N * (1 - r), 0)}টা × {x.mb(aov)} × {x.p(mm * 100)} মার্জিন = {x.mb(N * (1 - r) * aov * mm)}। বাদ কুরিয়ার ও প্যাকেজিং {x.mb(N * (out + pkg))} এবং রিটার্ন কুরিয়ার {x.mb(N * r * ret)}। **নেট লাভ: {x.mb(p1)}।**
২. **Advance চার্জ নিলে (অনুমান):** ১০% ক্রেতা ঝরে পড়বে ({x.n(N2, 0)}টা অর্ডার) আর রিটার্ন ৪০% কমে {x.p(r2 * 100, 1)} হবে (commitment effect)। নেট লাভ: **{x.mb(p2)}**।
৩. **তুলনা:** {x.mb(p2)} বনাম {x.mb(p1)}, পার্থক্য {x.mb(p2 - p1)}।
৪. **সাইকোলজি:** অল্প টাকা আগে দিলে ক্রেতা অর্ডারে কমিটেড হয়, ফলে অর্ডার বাতিল করা আর "বিনা খরচের" থাকে না।

{H2}
{'Advance মডেল টেস্ট করুন; অনুমানগুলো এটার পক্ষে।' if better else 'এই অনুমানে advance মডেল লাভজনক দেখাচ্ছে না; আগে অর্ডার কনফার্মেশন কল ও পরিষ্কার প্রোডাক্ট ছবি দিয়ে রিটার্ন কমান, তারপর আবার টেস্ট করুন।'} ১০% ঝরে পড়া আর ৪০% রিটার্ন কমা শুধু অনুমান, তাই আসল ট্রাফিকে A/B টেস্ট চালান।

{H3}
শুধু অর্ডার সংখ্যা নয়, প্রতি ১০০ আগ্রহী ক্রেতায় নেট লাভ মাপুন। ২ সপ্তাহ রিটার্নের কারণ (সাইজ ভুল, ফেক অর্ডার, দেরিতে ডেলিভারি) ট্র্যাক করুন, কারণ সমাধান কারণের ওপর নির্ভর করে।"""
    return u, a, "bd_cod_returns"

# ---------------------------------------------------------------- 7 Retention
def g_retention(lang):
    x = F(lang); ch = random.choice([2, 3, 4, 5, 7, 10, 15])
    ann = (1 - ch / 100) ** 12 * 100; ann2 = (1 - (ch - 1) / 100) ** 12 * 100; half = math.log(0.5) / math.log(1 - ch / 100)
    if lang == "en": u = random.choice([f"Our monthly churn is {ch}%. What does that mean for annual retention and how much does a 1-point improvement matter?", f"Is {ch}% monthly churn bad? Translate it into yearly numbers."])
    elif lang == "bn": u = f"আমাদের মাসিক churn {x.d(ch)}%। বছরের হিসাবে এর মানে কী, আর ১ পয়েন্ট কমালে কতটা লাভ?"
    else: u = f"monthly churn {ch}%. yearly retention e eta ki dhoroner? 1% komale ki hoy?"
    if lang == "en":
        a = f"""{H1}
1. **Annual retention:** (1 − {x.n(ch / 100, 2)})^12 = **{x.p(ann, 1)}** of a cohort remains after 12 months. Monthly numbers look small but compound.
2. **Half-life:** a cohort loses half its customers in about **{x.n(half)} months**.
3. **Average lifetime:** 1 ÷ {x.p(ch)} = {x.n(100 / ch)} months.
4. **One point better ({ch - 1}%):** annual retention becomes {x.p(ann2, 1)}, a gain of {x.n(ann2 - ann)} points.

{H2}
{'This is high for most subscription businesses; prioritize onboarding and early-life activation.' if ch >= 7 else 'This is workable; keep improving retention since each point compounds into LTV.'} Segment churn by plan, acquisition channel and signup month to find where it concentrates.

{H3}
Blended churn hides cohorts: a few high-churn channels can drag the average. Next step: compare cohort curves and cut the channel with the worst retention first."""
    else:
        a = f"""{H1}
১. **বার্ষিক retention:** (১ − {x.n(ch / 100, 2)})^১২ = **{x.p(ann, 1)}** ক্রেতা ১২ মাস পরেও থাকে। মাসিক সংখ্যা ছোট দেখালেও চক্রবৃদ্ধিতে বড় হয়।
২. **Half-life:** একটা cohort এর অর্ধেক ক্রেতা চলে যায় প্রায় **{x.n(half)} মাসে**।
৩. **গড় আয়ু:** ১ ÷ {x.p(ch)} = {x.n(100 / ch)} মাস।
৪. **১ পয়েন্ট ভালো ({x.d(ch - 1)}%):** বার্ষিক retention হবে {x.p(ann2, 1)}, মানে {x.n(ann2 - ann)} পয়েন্ট বৃদ্ধি।

{H2}
{'বেশিরভাগ সাবস্ক্রিপশন বিজনেসের জন্য এটা বেশি; onboarding ও শুরুর activation কে অগ্রাধিকার দিন।' if ch >= 7 else 'এটা চলনসই; retention আরও বাড়াতে থাকুন কারণ প্রতিটা পয়েন্ট LTV তে চক্রবৃদ্ধি হারে কাজ করে।'} প্ল্যান, অ্যাকুইজিশন চ্যানেল ও signup মাস অনুযায়ী churn আলাদা করে দেখুন।

{H3}
গড় churn cohort লুকায়: কিছু খারাপ চ্যানেল পুরো গড় নষ্ট করতে পারে। পরবর্তী ধাপ: cohort curve তুলনা করে সবচেয়ে খারাপ retention এর চ্যানেল আগে কাটুন।"""
    return u, a, "retention_math"

# ---------------------------------------------------------------- 8 Price increase
def g_priceinc(lang):
    x = F(lang); m = random.choice([30, 40, 50, 60, 70, 80]); dlt = random.choice([5, 8, 10, 15, 20])
    loss = dlt / (m + dlt) * 100
    if lang == "en": u = f"I want to raise prices by {dlt}%. My gross margin is {m}%. How many customers can I lose before it hurts profit?"
    elif lang == "bn": u = f"আমি দাম {x.d(dlt)}% বাড়াতে চাই। আমার gross margin {x.d(m)}%। কতজন ক্রেতা হারালে লোকসান হবে?"
    else: u = f"dam {dlt}% barate chai. gross margin {m}%. koto customer harale loss hobe?"
    if lang == "en":
        a = f"""{H1}
1. Take a price of 100 with a margin of {m}, so cost is {100 - m}. Old profit per unit = {m}.
2. New price = {100 + dlt}, so new profit per unit = {m + dlt}.
3. To keep total profit equal you need {m} ÷ {m + dlt} = {x.n(m / (m + dlt) * 100)}% of current volume.
4. **Break-even volume loss = {dlt} ÷ ({m} + {dlt}) = {x.p(loss, 1)}.**

{H2}
If you expect to lose fewer than {x.p(loss, 1)} of customers, the increase is profitable on its own. The higher the margin, the more you can afford to lose. Raise prices on new customers first, and communicate real value improvements honestly.

{H3}
Churn from a price increase is not always visible immediately (some customers leave at renewal). Test on a segment, watch cancellations and complaints for 60 days, and keep the option to grandfather loyal customers."""
    else:
        a = f"""{H1}
১. ধরুন দাম ১০০, মার্জিন {x.d(m)}, অর্থাৎ খরচ {x.d(100 - m)}। পুরোনো লাভ প্রতি ইউনিটে {x.d(m)}।
২. নতুন দাম {x.d(100 + dlt)}, তাই নতুন লাভ প্রতি ইউনিটে {x.d(m + dlt)}।
৩. মোট লাভ সমান রাখতে বর্তমান ভলিউমের {x.d(m)} ÷ {x.d(m + dlt)} = {x.n(m / (m + dlt) * 100)}% লাগবে।
৪. **Break-even volume loss = {x.d(dlt)} ÷ ({x.d(m)} + {x.d(dlt)}) = {x.p(loss, 1)}।**

{H2}
{x.p(loss, 1)} এর কম ক্রেতা হারালে দাম বাড়ানো এমনিতেই লাভজনক। মার্জিন যত বেশি, তত বেশি ক্রেতা হারানোর সুযোগ থাকে। আগে নতুন ক্রেতাদের জন্য দাম বাড়ান, এবং ভ্যালু বাড়ালে সৎভাবে জানান।

{H3}
দাম বাড়ানোর churn সঙ্গে সঙ্গে দেখা নাও যেতে পারে (অনেকে renewal এ চলে যায়)। একটা সেগমেন্টে টেস্ট করুন, ৬০ দিন cancellation ও অভিযোগ ট্র্যাক করুন, এবং বিশ্বস্ত পুরোনো ক্রেতাদের জন্য পুরোনো দাম রাখার সুযোগ রাখুন।"""
    return u, a, "price_increase"

# ---------------------------------------------------------------- 9 Channel comparison
CHANNELS = [("Facebook ads", "ফেসবুক অ্যাড"), ("LinkedIn outreach", "LinkedIn আউটরিচ"), ("referrals", "রেফারেল"), ("SEO/content", "SEO/কনটেন্ট"), ("YouTube", "YouTube"), ("WhatsApp follow-up", "WhatsApp ফলো-আপ")]
def g_channel(lang):
    x = F(lang); (an, ab), (bn_, bb) = random.sample(CHANNELS, 2)
    sp = lambda: random.choice([20000, 50000, 100000]) if not x.en else random.choice([500, 1000, 3000])
    sA, sB = sp(), sp(); lA, lB = random.randint(40, 300), random.randint(20, 200); cA, cB = random.choice([2, 4, 6, 10, 15, 20]), random.choice([2, 4, 6, 10, 15, 20])
    LA = random.choice([20000, 40000, 100000]) if not x.en else random.choice([300, 800, 2000]); LB = random.choice([20000, 40000, 100000]) if not x.en else random.choice([300, 800, 2000])
    nA, nB = lA * cA / 100, lB * cB / 100
    if nA < 1 or nB < 1: return None
    cacA, cacB = sA / nA, sB / nB; rA, rB = LA / cacA, LB / cacB
    best = an if rA > rB else bn_; bestb = ab if rA > rB else bb
    if lang == "en":
        u = f"{an}: spent {x.m(sA)}, {lA} leads, {cA}% close, customer LTV {x.m(LA)}. {bn_}: spent {x.m(sB)}, {lB} leads, {cB}% close, LTV {x.m(LB)}. Where should I put more budget?"
    elif lang == "bn":
        u = f"{ab}: খরচ {x.m(sA)}, {x.d(lA)}টা লিড, {x.d(cA)}% ক্লোজ, LTV {x.m(LA)}। {bb}: খরচ {x.m(sB)}, {x.d(lB)}টা লিড, {x.d(cB)}% ক্লোজ, LTV {x.m(LB)}। বাড়তি বাজেট কোথায় দেব?"
    else:
        u = f"{an} e {x.m(sA)} kharoch, {lA} lead, {cA}% close, LTV {x.m(LA)}. {bn_} e {x.m(sB)} kharoch, {lB} lead, {cB}% close, LTV {x.m(LB)}. beshi budget kothay dibo?"
    if lang == "en":
        a = f"""{H1}
1. **{an}:** customers = {lA} × {cA}% = {x.n(nA)}; CAC = {x.m(sA)} ÷ {x.n(nA)} = **{x.m(cacA)}**; LTV:CAC = **{x.n(rA)}:1**.
2. **{bn_}:** customers = {lB} × {cB}% = {x.n(nB)}; CAC = {x.m(sB)} ÷ {x.n(nB)} = **{x.m(cacB)}**; LTV:CAC = **{x.n(rB)}:1**.
3. **Reading:** {best} returns more lifetime value per unit of spend.
4. **Caveat:** small samples are noisy and channels saturate; the next dollar does not perform like the average dollar.

{H2}
Shift roughly 20-30% of the marginal budget toward {best} and keep the other channel alive at a smaller scale. Re-measure after each cycle.

{H3}
Do not abandon a channel on one month of data. Check lead quality and time-to-close too, and track blended CAC across the whole funnel."""
    else:
        a = f"""{H1}
১. **{ab}:** কাস্টমার = {x.d(lA)} × {x.d(cA)}% = {x.n(nA)}; CAC = {x.m(sA)} ÷ {x.n(nA)} = **{x.m(cacA)}**; LTV:CAC = **{x.n(rA)}:১**।
২. **{bb}:** কাস্টমার = {x.d(lB)} × {x.d(cB)}% = {x.n(nB)}; CAC = {x.m(sB)} ÷ {x.n(nB)} = **{x.m(cacB)}**; LTV:CAC = **{x.n(rB)}:১**।
৩. **পাঠ:** {bestb} প্রতি খরচে বেশি lifetime value দিচ্ছে।
৪. **সতর্কতা:** ছোট স্যাম্পল noisy, আর চ্যানেল saturate করে; পরের টাকাটা গড় টাকার মতো কাজ করে না।

{H2}
অতিরিক্ত বাজেটের প্রায় ২০-৩০% {bestb} এ সরান এবং অন্য চ্যানেল ছোট পরিসরে চালু রাখুন। প্রতিটা সাইকেল শেষে আবার মাপুন।

{H3}
এক মাসের ডেটায় কোনো চ্যানেল বাদ দেবেন না। লিডের মান ও ক্লোজ করতে সময়ও দেখুন, আর পুরো ফানেলের blended CAC ট্র্যাক করুন।"""
    return u, a, "channel_cac"

# ---------------------------------------------------------------- 10 RICE
INITS = [("fix onboarding", "অনবোর্ডিং ঠিক করা"), ("add a referral program", "রেফারেল প্রোগ্রাম চালু"), ("build a mobile app", "মোবাইল অ্যাপ বানানো"), ("launch an annual plan", "বার্ষিক প্ল্যান চালু"),
         ("improve checkout", "চেকআউট উন্নত করা"), ("start YouTube content", "YouTube কনটেন্ট শুরু"), ("add WhatsApp support", "WhatsApp সাপোর্ট"), ("build a CRM integration", "CRM ইন্টিগ্রেশন বানানো")]
def g_rice(lang):
    x = F(lang); items = random.sample(INITS, 3); rows = []
    for en, bn_ in items:
        rows.append(dict(en=en, bn=bn_, reach=random.choice([100, 300, 800, 2000, 5000]), imp=random.choice([0.25, 0.5, 1, 2, 3]), conf=random.choice([50, 80, 100]), eff=random.choice([1, 2, 3, 5, 8])))
    for r_ in rows: r_["score"] = r_["reach"] * r_["imp"] * r_["conf"] / 100 / r_["eff"]
    rk = sorted(rows, key=lambda r_: -r_["score"]); top = rk[0]
    nm = (lambda r_: r_["en"]) if lang == "en" else (lambda r_: r_["bn"])
    line = lambda r_: f"{nm(r_)}: reach {x.d(r_['reach'])}, impact {x.n(r_['imp'], 2)}, confidence {x.d(r_['conf'])}%, effort {x.d(r_['eff'])} person-weeks"
    if lang == "en": u = "Help me prioritize with RICE:\n" + "\n".join(f"- {line(r_)}" for r_ in rows)
    elif lang == "bn": u = "RICE দিয়ে অগ্রাধিকার ঠিক করে দিন:\n" + "\n".join(f"- {line(r_)}" for r_ in rows)
    else: u = "RICE diye prioritize kore dao:\n" + "\n".join(f"- {r_['en']}: reach {r_['reach']}, impact {r_['imp']}, confidence {r_['conf']}%, effort {r_['eff']} weeks" for r_ in rows)
    calc = "\n".join(f"{x.st(i + 1)} **{nm(r_)}:** {x.d(r_['reach'])} × {x.n(r_['imp'], 2)} × {x.d(r_['conf'])}% ÷ {x.d(r_['eff'])} = **{x.n(r_['score'], 0)}**" for i, r_ in enumerate(rk))
    if lang == "en":
        a = f"""{H1}
RICE score = Reach × Impact × Confidence ÷ Effort. Ranked:
{calc}

{H2}
Start with **{nm(top)}**; it delivers the most expected impact per unit of effort. Revisit the ranking if a cheap experiment can raise the confidence of a lower-ranked item.

{H3}
RICE is only as honest as its inputs. Impact and confidence are guesses, so stress-test the top item's biggest assumption before committing the whole quarter. Re-score after each release."""
    else:
        a = f"""{H1}
RICE স্কোর = Reach × Impact × Confidence ÷ Effort। র‍্যাঙ্কিং:
{calc}

{H2}
শুরু করুন **{nm(top)}** দিয়ে; এটা প্রতি পরিশ্রমে সবচেয়ে বেশি প্রত্যাশিত প্রভাব দেয়। কম র‍্যাঙ্কের কোনো আইটেমের confidence সস্তা এক্সপেরিমেন্টে বাড়ানো গেলে র‍্যাঙ্কিং আবার দেখুন।

{H3}
RICE ততটাই সৎ যতটা তার ইনপুট। Impact ও confidence অনুমান, তাই পুরো কোয়ার্টার দেওয়ার আগে শীর্ষ আইটেমের সবচেয়ে বড় অনুমান যাচাই করুন। প্রতিটা রিলিজের পর আবার স্কোর করুন।"""
    return u, a, "rice_prioritization"

# ---------------------------------------------------------------- 11 Service margin
SERV = [("video production", "ভিডিও প্রোডাকশন"), ("wedding photography", "ওয়েডিং ফটোগ্রাফি"), ("web design", "ওয়েব ডিজাইন"), ("consulting", "কনসাল্টিং")]
def g_service(lang):
    x = F(lang); sv = random.choice(SERV)
    P = random.choice([60000, 100000, 150000, 300000]) if not x.en else random.choice([1500, 3000, 5000, 8000])
    Hh = random.choice([30, 50, 80, 120]); c = random.choice([300, 500, 700, 1000]) if not x.en else random.choice([15, 25, 40])
    D = random.choice([5000, 10000, 20000]) if not x.en else random.choice([100, 300, 600])
    cost = Hh * c + D; profit = P - cost; mg = profit / P * 100; eff = (P - D) / Hh; P40 = cost / 0.6
    if lang == "en": u = f"I charge {x.m(P)} for a {sv[0]} project. It takes about {Hh} hours at an internal cost of {x.m(c)}/hour, plus {x.m(D)} direct costs. Am I pricing right?"
    elif lang == "bn": u = f"আমি একটা {sv[1]} প্রজেক্টে {x.m(P)} নিই। কাজে প্রায় {x.d(Hh)} ঘণ্টা লাগে, ঘণ্টা প্রতি অভ্যন্তরীণ খরচ {x.m(c)}, সাথে সরাসরি খরচ {x.m(D)}। প্রাইসিং ঠিক আছে?"
    else: u = f"{sv[1]} project e {x.m(P)} charge kori. {Hh} ghonta lage, ghonta cost {x.m(c)}, direct cost {x.m(D)}. pricing thik ache?"
    if lang == "en":
        a = f"""{H1}
1. **Total cost:** {Hh} × {x.m(c)} + {x.m(D)} = {x.m(cost)}.
2. **Profit:** {x.m(P)} − {x.m(cost)} = **{x.m(profit)}** ({x.p(mg, 1)} margin).
3. **Effective hourly rate:** ({x.m(P)} − {x.m(D)}) ÷ {Hh} = **{x.m(eff)}/hour** versus your cost of {x.m(c)}/hour.
4. **Price for a 40% margin:** {x.m(cost)} ÷ 0.6 = **{x.m(P40)}**.

{H2}
{'Your margin is healthy; keep the price and protect scope with a clear revision limit.' if mg >= 35 else ('Margin is thin for a service business that carries unpaid sales, revision and admin time. Move toward the 40% price or cut hours with templates and tighter scope.' if mg >= 0 else 'You are losing money on this project. Raise the price or cut scope before taking the next one.')}

{H3}
Hours usually run over, so add a 15-20% buffer when you quote. Track actual hours on 5 projects to see whether your {Hh}-hour estimate is real. Consider value-based pricing for clients whose outcome is worth far more than your hours."""
    else:
        a = f"""{H1}
১. **মোট খরচ:** {x.d(Hh)} × {x.m(c)} + {x.m(D)} = {x.m(cost)}।
২. **লাভ:** {x.m(P)} − {x.m(cost)} = **{x.m(profit)}** ({x.p(mg, 1)} মার্জিন)।
৩. **কার্যকর ঘণ্টা-রেট:** ({x.m(P)} − {x.m(D)}) ÷ {x.d(Hh)} = **ঘণ্টায় {x.m(eff)}**, আপনার খরচ ঘণ্টায় {x.m(c)}।
৪. **৪০% মার্জিনের দাম:** {x.m(cost)} ÷ ০.৬ = **{x.m(P40)}**।

{H2}
{'মার্জিন সুস্থ; দাম ঠিক রাখুন এবং স্পষ্ট revision limit দিয়ে scope রক্ষা করুন।' if mg >= 35 else ('সার্ভিস ব্যবসায় বিক্রয়, revision ও অ্যাডমিনের অবেতনভুক্ত সময় থাকে, তাই এই মার্জিন পাতলা। ৪০% মার্জিনের দামের দিকে যান অথবা টেমপ্লেট ও কড়া scope দিয়ে ঘণ্টা কমান।' if mg >= 0 else 'এই প্রজেক্টে আপনি লোকসানে। পরের প্রজেক্ট নেওয়ার আগে দাম বাড়ান বা scope কমান।')}

{H3}
ঘণ্টা সাধারণত বেশি লাগে, তাই কোটেশনে ১৫-২০% বাফার রাখুন। ৫টা প্রজেক্টে আসল ঘণ্টা ট্র্যাক করুন {x.d(Hh)} ঘণ্টার অনুমান ঠিক কি না দেখতে। যেসব ক্লায়েন্টের ফলাফলের মূল্য আপনার ঘণ্টার চেয়ে অনেক বেশি, তাদের জন্য value-based pricing ভাবুন।"""
    return u, a, "service_margin"

# ---------------------------------------------------------------- 12 Decoy pricing
def g_decoy(lang):
    x = F(lang); u1, u2, u3 = random.choice([1, 2]), random.choice([3, 4, 5]), random.choice([8, 10, 12])
    pb = random.choice([500, 999, 1500, 2000]) if not x.en else random.choice([9, 19, 29]); pp = pb * random.choice([2.5, 3, 4]); pd = pp * random.choice([0.88, 0.92, 0.95])
    pb, pp, pd = round(pb), round(pp), round(pd)
    ppu = lambda p, u: p / u
    if lang == "en": u = f"My three plans: Basic {x.m(pb)} ({u1} seats), Plus {x.m(pd)} ({u2} seats), Pro {x.m(pp)} ({u3} seats). I want most people to pick Pro. Is the structure sound?"
    elif lang == "bn": u = f"আমার তিনটা প্ল্যান: Basic {x.m(pb)} ({x.d(u1)} সিট), Plus {x.m(pd)} ({x.d(u2)} সিট), Pro {x.m(pp)} ({x.d(u3)} সিট)। বেশিরভাগ মানুষ Pro নিক চাই। স্ট্রাকচার ঠিক আছে?"
    else: u = f"3 ta plan: Basic {x.m(pb)} ({u1} seat), Plus {x.m(pd)} ({u2} seat), Pro {x.m(pp)} ({u3} seat). Pro bikri korte chai. structure thik ache?"
    if lang == "en":
        a = f"""{H1}
1. **Price per seat:** Basic {x.m(ppu(pb, u1))}, Plus {x.m(ppu(pd, u2))}, Pro {x.m(ppu(pp, u3))}.
2. **Decoy pattern:** Plus costs only {x.p((1 - pd / pp) * 100)} less than Pro but gives {x.n(u3 / u2)}× fewer seats. Buyers compare Plus with Pro (not with Basic) and Pro looks like the obvious deal. This is the decoy (asymmetric dominance) effect.
3. **Anchoring:** Plus's price also anchors Pro as only a small step up.

{H2}
The structure should work. Keep Plus a real, usable plan for some customers (small teams exist) and label Pro as "most popular" only if the data says so. Do not hide the Basic option.

{H3}
Basic customers face a big jump to Plus; check whether Basic buyers get stuck. Track plan mix and ARPU for 4 weeks. If ARPU does not rise, the decoy is not doing its job, or Pro's value is unclear."""
    else:
        a = f"""{H1}
১. **সিট প্রতি দাম:** Basic {x.m(ppu(pb, u1))}, Plus {x.m(ppu(pd, u2))}, Pro {x.m(ppu(pp, u3))}।
২. **Decoy প্যাটার্ন:** Plus, Pro এর চেয়ে মাত্র {x.p((1 - pd / pp) * 100)} সস্তা কিন্তু সিট {x.n(u3 / u2)} গুণ কম। ক্রেতা Plus কে Pro এর সাথে তুলনা করে (Basic এর সাথে নয়), তাই Pro কে স্পষ্ট ভালো ডিল মনে হয়। এটাই decoy (asymmetric dominance) effect।
৩. **Anchoring:** Plus এর দাম Pro কে "অল্প বেশি" দেখায়।

{H2}
স্ট্রাকচার কাজ করার কথা। Plus কে সত্যিকারের ব্যবহারযোগ্য প্ল্যান রাখুন (ছোট টিমও আছে), আর "Most popular" লেবেল শুধু ডেটা যা বলে তখনই দিন। Basic লুকাবেন না।

{H3}
Basic থেকে Plus এ বড় লাফ, তাই Basic ক্রেতা আটকে যাচ্ছে কি না দেখুন। ৪ সপ্তাহ প্ল্যান মিক্স ও ARPU ট্র্যাক করুন। ARPU না বাড়লে decoy কাজ করছে না, অথবা Pro এর ভ্যালু স্পষ্ট নয়।"""
    return u, a, "decoy_pricing"

# ---------------------------------------------------------------- 13 Biases / Cialdini
IND = [("wedding photography studio", "ওয়েডিং ফটোগ্রাফি স্টুডিও"), ("SaaS startup", "SaaS স্টার্টআপ"), ("online clothing shop", "অনলাইন পোশাকের দোকান"), ("video production agency", "ভিডিও প্রোডাকশন এজেন্সি"),
       ("real estate brokerage", "রিয়েল এস্টেট ব্রোকারেজ"), ("online course business", "অনলাইন কোর্স ব্যবসা"), ("restaurant or cafe", "রেস্তোরাঁ বা ক্যাফে"), ("freelance consultancy", "ফ্রিল্যান্স কনসাল্টেন্সি"),
       ("PropTech tool", "PropTech টুল"), ("grocery delivery startup", "গ্রোসারি ডেলিভারি স্টার্টআপ")]
BIAS = {
 "anchoring": ("Anchoring", "People judge a price relative to the first number they see.", "Show your fullest, genuinely valuable option first and list what it really includes; the standard option is then judged against it.", "The anchor must be a real offer someone can buy. An invented 'original price' is deceptive.", "A/B test the order of options and compare the share choosing the middle tier.", "An unrealistic anchor makes customers distrust the whole page.",
  "মানুষ প্রথম দেখা সংখ্যার তুলনায় দাম বিচার করে।", "আপনার সবচেয়ে পূর্ণ ও সত্যিকারের মূল্যবান অপশন আগে দেখান এবং তাতে আসলে কী আছে লিখুন; স্ট্যান্ডার্ড অপশন তখন তার সাথে তুলনায় বিচার হবে।", "Anchor টা এমন অফার হতে হবে যা কেউ সত্যিই কিনতে পারে। বানানো 'আগের দাম' প্রতারণা।", "অপশনের ক্রম A/B টেস্ট করে মাঝের টিয়ার বেছে নেওয়ার হার তুলনা করুন।", "অবাস্তব anchor পুরো পেজের ওপর আস্থা নষ্ট করে।"),
 "loss_aversion": ("Loss aversion", "A loss feels roughly twice as painful as an equal gain feels good (the exact ratio varies by context).", "Show the real cost of inaction: what the customer loses by waiting, in numbers (a lapsing slot, a genuine deadline, the ongoing cost of the problem).", "Use only true deadlines and true costs. Fear-mongering invites refunds and bad reviews.", "Compare a gain-framed message with a loss-framed one on the same audience.", "Overusing fear makes people tune out or resent the brand.",
  "সমান লাভের আনন্দের চেয়ে ক্ষতির কষ্ট প্রায় দ্বিগুণ অনুভূত হয় (অনুপাত প্রসঙ্গভেদে বদলায়)।", "কিছু না করার আসল খরচ দেখান: অপেক্ষা করলে ক্রেতা কী হারাবে, সংখ্যায় (বাতিল হতে যাওয়া স্লট, সত্যিকারের ডেডলাইন, সমস্যার চলমান খরচ)।", "শুধু সত্য ডেডলাইন ও সত্য খরচ ব্যবহার করুন। ভয় দেখালে রিফান্ড ও খারাপ রিভিউ আসে।", "একই শ্রোতার ওপর gain-framed ও loss-framed মেসেজ তুলনা করুন।", "অতিরিক্ত ভয় দেখালে মানুষ উপেক্ষা করে বা বিরক্ত হয়।"),
 "scarcity": ("Scarcity", "Limited availability raises perceived value and urgency.", "Make real limits visible: the number of projects you can take per month, true stock, a real cohort start date.", "Never fake counters or 'only 2 left' when stock is plentiful.", "Publish your real monthly capacity and track booking speed before and after.", "Fake scarcity gets exposed quickly and damages credibility.",
  "সীমিত প্রাপ্যতা মূল্য ও জরুরিত্ব অনুভূতি বাড়ায়।", "আসল সীমা দৃশ্যমান করুন: মাসে কতগুলো প্রজেক্ট নিতে পারেন, সত্যিকারের স্টক, আসল ব্যাচ শুরুর তারিখ।", "ভুয়া কাউন্টার বা পর্যাপ্ত স্টক থাকতে 'মাত্র ২টা বাকি' লিখবেন না।", "মাসিক আসল ক্ষমতা প্রকাশ করুন এবং আগে-পরে বুকিংয়ের গতি ট্র্যাক করুন।", "ভুয়া scarcity দ্রুত ধরা পড়ে এবং বিশ্বাসযোগ্যতা নষ্ট করে।"),
 "social_proof": ("Social proof", "People follow what similar others have done, especially under uncertainty.", "Show real, specific evidence: named testimonials with permission, concrete results, a short case study, real counts you can verify.", "Never invent numbers, names or reviews. If you have few customers, show the few specifically.", "Add one real case study near the call to action and compare conversion.", "Vague or inflated claims are easy to disprove in a small market.",
  "অনিশ্চয়তায় মানুষ একই রকম অন্যদের কাজ অনুসরণ করে।", "আসল ও নির্দিষ্ট প্রমাণ দেখান: অনুমতি নিয়ে নামসহ টেস্টিমনিয়াল, বাস্তব ফলাফল, ছোট কেস স্টাডি, যাচাইযোগ্য আসল সংখ্যা।", "সংখ্যা, নাম বা রিভিউ বানাবেন না। ক্রেতা কম হলে সেই অল্প কয়জনকেই নির্দিষ্টভাবে দেখান।", "কল-টু-অ্যাকশনের পাশে একটা আসল কেস স্টাডি দিয়ে conversion তুলনা করুন।", "ছোট মার্কেটে অস্পষ্ট বা ফোলানো দাবি সহজেই ধরা পড়ে।"),
 "decoy": ("Decoy effect", "A clearly inferior third option makes one of the others look like a better deal.", "Design three tiers where the middle option is slightly worse than the top one for a similar price, so the top tier looks like the obvious value.", "Every tier must still be a legitimate offer someone could sensibly buy.", "Track plan mix and average revenue per customer for 4 weeks.", "If the tiers look rigged, buyers feel manipulated.",
  "স্পষ্টভাবে নিকৃষ্ট তৃতীয় অপশন অন্য একটা অপশনকে ভালো ডিল দেখায়।", "তিনটা টিয়ার এমনভাবে সাজান যেন মাঝেরটা প্রায় সমান দামে উপরের টিয়ারের চেয়ে একটু খারাপ হয়, ফলে উপরের টিয়ার স্পষ্ট ভ্যালু মনে হয়।", "প্রতিটা টিয়ার সত্যিকারের কেনার মতো বৈধ অফার হতে হবে।", "৪ সপ্তাহ প্ল্যান মিক্স ও প্রতি ক্রেতার গড় আয় ট্র্যাক করুন।", "টিয়ারগুলো সাজানো মনে হলে ক্রেতা প্রতারিত বোধ করে।"),
 "reciprocity": ("Reciprocity", "When you give something of value first, people feel inclined to give back.", "Offer something genuinely useful before asking: a short audit, a checklist, a sample, a free diagnostic tied to the problem you solve.", "The gift must be unconditional and useful, not a disguised trap.", "Send a free audit to 20 prospects and compare reply and meeting rates with a plain pitch.", "Giving away too much work for free can attract freeloaders; limit the scope.",
  "আপনি আগে মূল্যবান কিছু দিলে মানুষ প্রতিদান দিতে আগ্রহী হয়।", "চাওয়ার আগে সত্যিই কাজের কিছু দিন: ছোট অডিট, চেকলিস্ট, স্যাম্পল, বা আপনার সমাধান করা সমস্যার সাথে সম্পর্কিত ফ্রি ডায়াগনস্টিক।", "উপহারটা শর্তহীন ও কাজের হতে হবে, ছদ্মবেশী ফাঁদ নয়।", "২০ জন প্রসপেক্টকে ফ্রি অডিট পাঠিয়ে সাধারণ পিচের সাথে reply ও মিটিং হার তুলনা করুন।", "অতিরিক্ত বিনামূল্যে কাজ দিলে ফ্রিলোডার আসে; সীমা রাখুন।"),
 "commitment": ("Commitment and consistency", "People act in line with small commitments they have already made.", "Start with a small, easy yes: a quick question, a short quiz, a small paid pilot, then build on it.", "Do not trap people with hidden terms; the next step must be an honest, clearly explained one.", "Compare a single big ask with a two-step ask (small first, then larger).", "Pushing a big step right after a small yes feels manipulative and backfires.",
  "মানুষ ইতিমধ্যে করা ছোট প্রতিশ্রুতির সাথে সঙ্গতি রেখে কাজ করে।", "ছোট, সহজ 'হ্যাঁ' দিয়ে শুরু করুন: একটা প্রশ্ন, ছোট কুইজ, ছোট পেইড পাইলট, তারপর সেটার ওপর গড়ুন।", "লুকানো শর্তে ফাঁদ পাতবেন না; পরের ধাপ সৎ ও স্পষ্টভাবে ব্যাখ্যা করা হতে হবে।", "একটা বড় অনুরোধ বনাম দুই ধাপের অনুরোধ (আগে ছোট, পরে বড়) তুলনা করুন।", "ছোট 'হ্যাঁ' এর পরপরই বড় চাপ দিলে ম্যানিপুলেটিভ লাগে ও উল্টো ফল দেয়।"),
}
def g_bias_all():
    out = []
    for key, v in BIAS.items():
        for ind in IND:
            for lang in ["en", "bn", "mixed"]:
                x = F(lang); en = lang == "en"
                (nm, what_e, how_e, guard_e, test_e, risk_e, what_b, how_b, guard_b, test_b, risk_b) = v
                if en: u = random.choice([f"How can I use {nm.lower()} in my {ind[0]} without being manipulative?", f"Explain {nm.lower()} and apply it to a {ind[0]}."])
                elif lang == "bn": u = random.choice([f"আমার {ind[1]} এ {nm} কীভাবে ম্যানিপুলেটিভ না হয়ে কাজে লাগাব?", f"{nm} কী এবং {ind[1]} এ এটা কীভাবে প্রয়োগ করব?"])
                else: u = random.choice([f"amar {ind[1]} e {nm} kivabe use korbo, manipulate na kore?", f"{nm} ta bujhiye bolo ar {ind[1]} er jonno apply kore dao"])
                if en:
                    a = f"""{H1}
1. **Principle ({nm}):** {what_e}
2. **Applied to a {ind[0]}:** {how_e}
3. **Ethics line:** {guard_e}

{H2}
Use {nm.lower()} to make a genuinely good offer easier to understand, never to hide a weak one. Start with one change on one page or message.

{H3}
{risk_e} Next step: {test_e}"""
                else:
                    a = f"""{H1}
১. **নীতি ({nm}):** {what_b}
২. **{ind[1]} এ প্রয়োগ:** {how_b}
৩. **নৈতিক সীমা:** {guard_b}

{H2}
{nm} ব্যবহার করুন একটা সত্যিকারের ভালো অফার সহজে বোঝাতে, দুর্বল অফার ঢাকতে নয়। একটা পেজ বা মেসেজে একটা পরিবর্তন দিয়ে শুরু করুন।

{H3}
{risk_b} পরবর্তী ধাপ: {test_b}"""
                out.append((u, a, f"bias_{key}", lang))
    return out

# ---------------------------------------------------------------- 14 Negotiation
def g_neg(lang):
    x = F(lang); ctx = random.choice(CTX)
    price = random.choice([60000, 100000, 150000, 250000]) if not x.en else random.choice([1500, 3000, 5000, 8000])
    cost = price * random.choice([0.4, 0.5, 0.55, 0.6]); ask = random.choice([15, 20, 25, 30, 40]); strong = random.choice([True, False])
    counter = max(3, round(ask / 3)); walk = cost / 0.8
    m0 = price - cost; m_ask = price * (1 - ask / 100) - cost; m_c = price * (1 - counter / 100) - cost
    if lang == "en": u = f"A client asks {ask}% off my {x.m(price)} {ctx[0]} (cost {x.m(cost)}) and says they will go elsewhere. My calendar is {'full' if strong else 'mostly empty'}. How do I negotiate?"
    elif lang == "bn": u = f"ক্লায়েন্ট আমার {x.m(price)} এর {ctx[1]} এ {x.d(ask)}% ছাড় চাইছে (খরচ {x.m(cost)}), না দিলে অন্যত্র যাবে বলছে। আমার ক্যালেন্ডার {'ভরা' if strong else 'প্রায় ফাঁকা'}। কীভাবে দর-কষাকষি করব?"
    else: u = f"client {x.m(price)} er {ctx[1]} e {ask}% discount chay (cost {x.m(cost)}), na dile onno jaygay jabe. amar calendar {'full' if strong else 'prai faka'}. ki korbo?"
    stance_en = "Your BATNA is strong, so you can hold your price and trade only on terms." if strong else "Your BATNA is weak, so concede carefully, but never below your walk-away price."
    stance_bn = "আপনার BATNA শক্তিশালী, তাই দাম ধরে রেখে শুধু শর্তে লেনদেন করতে পারেন।" if strong else "আপনার BATNA দুর্বল, তাই সাবধানে ছাড় দিন, কিন্তু walk-away price এর নিচে কখনো নয়।"
    if lang == "en":
        a = f"""{H1}
1. **Your margin:** {x.m(price)} − {x.m(cost)} = {x.m(m0)}. At {ask}% off it falls to **{x.m(m_ask)}** ({x.p(m_ask / (price * (1 - ask / 100)) * 100)} of the new price).
2. **BATNA:** {stance_en}
3. **Their position vs interest:** '{ask}% off' is a position; the interest may be budget limits, proving a good deal to their boss, or reducing risk.
4. **Walk-away price:** at a minimum 20% margin, {x.m(cost)} ÷ 0.8 = **{x.m(walk)}**.

{H2}
Counter with a trade, not a cut: up to {counter}% (margin {x.m(m_c)}) in exchange for 50% advance payment or a commitment to the next project, or offer a leaner scope at a lower price. Ask them to show a comparable quote so you can compare like for like.

{H3}
The client may leave, and that can be the right result: price-only buyers often bring scope creep and slow payments. Decide the walk-away price before the call and write it down."""
    else:
        a = f"""{H1}
১. **আপনার মার্জিন:** {x.m(price)} − {x.m(cost)} = {x.m(m0)}। {x.d(ask)}% ছাড়ে তা নামবে **{x.m(m_ask)}** এ (নতুন দামের {x.p(m_ask / (price * (1 - ask / 100)) * 100)})।
২. **BATNA:** {stance_bn}
৩. **Position বনাম interest:** '{x.d(ask)}% ছাড়' একটা position; আসল interest হতে পারে বাজেট সীমা, বসকে ভালো ডিল দেখানো, বা ঝুঁকি কমানো।
৪. **Walk-away price:** ন্যূনতম ২০% মার্জিনে {x.m(cost)} ÷ ০.৮ = **{x.m(walk)}**।

{H2}
ছাড় না দিয়ে বিনিময় প্রস্তাব করুন: {x.d(counter)}% পর্যন্ত (মার্জিন {x.m(m_c)}) ৫০% advance বা পরের প্রজেক্টের কমিটমেন্টের বিনিময়ে, অথবা কম scope এ কম দাম। তাদের তুলনীয় কোটেশন দেখাতে বলুন যাতে সমান ভিত্তিতে তুলনা করা যায়।

{H3}
ক্লায়েন্ট চলে যেতে পারেন, আর সেটা সঠিক ফলও হতে পারে: শুধু দামে কেনা ক্রেতারা প্রায়ই scope creep ও দেরিতে পেমেন্ট আনে। কলের আগে walk-away price ঠিক করে লিখে রাখুন।"""
    return u, a, "negotiation_batna"

# ---------------------------------------------------------------- 15 MECE diagnosis
MECE = {
 "online store": ("অনলাইন স্টোর", [("Traffic", "ট্রাফিক", "ad spend, organic reach, tracking pixel, seasonality", "অ্যাড খরচ, অর্গানিক রিচ, ট্র্যাকিং পিক্সেল, মৌসুম"), ("Conversion rate", "কনভার্সন রেট", "site speed, checkout errors, stock-outs, price changes", "সাইট স্পিড, চেকআউট ত্রুটি, স্টক শেষ, দাম বদল"), ("Average order value", "গড় অর্ডার ভ্যালু", "discount mix, bundles, product mix", "ডিসকাউন্ট মিক্স, বান্ডল, প্রোডাক্ট মিক্স"), ("Repeat purchase rate", "রিপিট ক্রয়ের হার", "delivery quality, complaints, product quality", "ডেলিভারির মান, অভিযোগ, প্রোডাক্টের মান")]),
 "SaaS": ("SaaS", [("New signups", "নতুন signup", "channel performance, brand search, launches", "চ্যানেল পারফরম্যান্স, ব্র্যান্ড সার্চ, লঞ্চ"), ("Activation", "Activation", "onboarding changes, bugs, time to first value", "onboarding পরিবর্তন, বাগ, প্রথম ভ্যালু পেতে সময়"), ("Trial-to-paid conversion", "Trial থেকে paid কনভার্সন", "pricing page, sales follow-up, plan fit", "প্রাইসিং পেজ, সেলস ফলো-আপ, প্ল্যান ফিট"), ("Churn and expansion", "Churn ও expansion", "support quality, competitor moves, renewals", "সাপোর্টের মান, প্রতিযোগীর পদক্ষেপ, রিনিউয়াল")]),
 "service agency": ("সার্ভিস এজেন্সি", [("Leads", "লিড", "referrals, outreach volume, portfolio visibility", "রেফারেল, আউটরিচের পরিমাণ, পোর্টফোলিও দৃশ্যমানতা"), ("Proposal-to-win rate", "প্রস্তাব থেকে জয়ের হার", "pricing, proposal quality, response speed", "প্রাইসিং, প্রস্তাবের মান, সাড়া দেওয়ার গতি"), ("Average project value", "গড় প্রজেক্ট ভ্যালু", "scope size, discounting, packaging", "scope এর আকার, ডিসকাউন্ট, প্যাকেজিং"), ("Repeat and referral work", "রিপিট ও রেফারেল কাজ", "delivery quality, relationship follow-up", "ডেলিভারির মান, সম্পর্ক ধরে রাখা")]),
 "restaurant or cafe": ("রেস্তোরাঁ বা ক্যাফে", [("Foot traffic and orders", "ফুট ট্রাফিক ও অর্ডার", "location, weather, delivery apps, local events", "লোকেশন, আবহাওয়া, ডেলিভারি অ্যাপ, স্থানীয় ইভেন্ট"), ("Conversion of visitors to buyers", "ভিজিটর থেকে ক্রেতা", "menu, wait time, staff, pricing", "মেনু, অপেক্ষার সময়, স্টাফ, দাম"), ("Average ticket", "গড় বিল", "upsell habits, combos, discounts", "আপসেলের অভ্যাস, কম্বো, ডিসকাউন্ট"), ("Repeat customers", "রিপিট ক্রেতা", "food consistency, service, loyalty offers", "খাবারের ধারাবাহিকতা, সার্ভিস, লয়ালটি অফার")]),
 "online course": ("অনলাইন কোর্স", [("Audience reach", "অডিয়েন্স রিচ", "content frequency, platform algorithm, ads", "কনটেন্টের ফ্রিকোয়েন্সি, প্ল্যাটফর্ম অ্যালগরিদম, অ্যাড"), ("Landing-page conversion", "ল্যান্ডিং পেজ কনভার্সন", "offer clarity, price, proof, page speed", "অফারের স্পষ্টতা, দাম, প্রমাণ, পেজ স্পিড"), ("Price and discount mix", "দাম ও ডিসকাউন্ট মিক্স", "coupon use, bundles", "কুপন ব্যবহার, বান্ডল"), ("Refunds and completion", "রিফান্ড ও কমপ্লিশন", "course quality, expectations set, support", "কোর্সের মান, প্রত্যাশা নির্ধারণ, সাপোর্ট")]),
}
def g_mece_all():
    out = []
    for key, (bnm, terms) in MECE.items():
        for drop in [15, 25, 30, 40]:
            for lang in ["en", "bn", "mixed"]:
                x = F(lang)
                if lang == "en": u = f"Our {key} revenue fell {drop}% this month. How do I diagnose it?"
                elif lang == "bn": u = f"আমাদের {bnm} এর রেভিনিউ এই মাসে {x.d(drop)}% কমেছে। কীভাবে কারণ খুঁজব?"
                else: u = f"{bnm} er revenue {drop}% kome gese. karon kivabe khujbo?"
                eq_e = " × ".join(t[0] for t in terms); eq_b = " × ".join(t[1] for t in terms)
                if lang == "en":
                    body = "\n".join(f"{i + 1}. **{t[0]}:** did it move? Check {t[2]}." for i, t in enumerate(terms))
                    a = f"""{H1}
Split revenue into a MECE equation (mutually exclusive, collectively exhaustive): **Revenue = {eq_e}.** A {drop}% fall means at least one term fell, or several fell a little.
{body}
5. **External vs internal:** separate things you changed from things that changed around you (season, competitors, economy).

{H2}
Compare each term against last month and the same month last year. Start with the term that moved most in percentage terms, and do not change prices or ad budgets until you know which term it is.

{H3}
Several causes can overlap, and small drops in every term multiply. Next step: build a one-page weekly table of the four metrics by channel, form 2-3 hypotheses, and test the cheapest first."""
                else:
                    body = "\n".join(f"{x.st(i + 1)} **{t[1]}:** কি কমেছে? দেখুন: {t[3]}।" for i, t in enumerate(terms))
                    a = f"""{H1}
রেভিনিউকে MECE (পরস্পর-বর্জনকারী, সম্মিলিতভাবে সম্পূর্ণ) সমীকরণে ভাঙুন: **রেভিনিউ = {eq_b}।** {x.d(drop)}% পতনের মানে অন্তত একটা উপাদান কমেছে, অথবা কয়েকটা অল্প করে কমেছে।
{body}
৫. **বাহ্যিক বনাম অভ্যন্তরীণ:** আপনি যা বদলেছেন আর আপনার চারপাশে যা বদলেছে (মৌসুম, প্রতিযোগী, অর্থনীতি) তা আলাদা করুন।

{H2}
প্রতিটা উপাদান গত মাস ও গত বছরের একই মাসের সাথে তুলনা করুন। শতাংশে সবচেয়ে বেশি নড়া উপাদান দিয়ে শুরু করুন, আর কোনটা তা জানার আগে দাম বা অ্যাড বাজেট বদলাবেন না।

{H3}
একাধিক কারণ মিলে থাকতে পারে, আর প্রতিটা উপাদানে ছোট পতন গুণ হয়ে বড় হয়। পরবর্তী ধাপ: চ্যানেলভিত্তিক চারটা মেট্রিকের এক পাতার সাপ্তাহিক টেবিল বানান, ২-৩টা হাইপোথিসিস করুন এবং সবচেয়ে সস্তাটা আগে টেস্ট করুন।"""
                out.append((u, a, "mece_diagnosis", lang))
    return out

# ---------------------------------------------------------------- 16 Ethics refusals
ETH = {
 "fake_testimonials": ("write '{n}+ happy clients' and invented testimonials for my {i} landing page, even though I only have a few clients", "আমার {i} এর ল্যান্ডিং পেজের জন্য '{n}+ হ্যাপি ক্লায়েন্ট' আর বানানো টেস্টিমনিয়াল লিখে দাও, যদিও আমার ক্লায়েন্ট মাত্র কয়েকজন", "amar {i} er landing page e '{n}+ happy client' ar banano testimonial likhe dao, jodio client matro kichu",
   "invented numbers and quotes are false claims; in a small market they are discovered fast, and one exposed claim destroys referrals and trust", "বানানো সংখ্যা ও উক্তি মিথ্যা দাবি; ছোট মার্কেটে এটা দ্রুত ধরা পড়ে, আর একবার ধরা পড়লে রেফারেল ও বিশ্বাস দুটোই যায়",
   ["state the real number specifically ('worked with 8 clients'), with one concrete result each", "collect 2-3 real testimonials with permission, including names", "offer a risk-reversal such as a guarantee or a small paid pilot"], ["আসল সংখ্যা নির্দিষ্টভাবে লিখুন ('৮ জন ক্লায়েন্টের সাথে কাজ করেছি') এবং প্রতিটায় একটা বাস্তব ফলাফল", "অনুমতি নিয়ে নামসহ ২-৩টা আসল টেস্টিমনিয়াল সংগ্রহ করুন", "গ্যারান্টি বা ছোট পেইড পাইলটের মতো risk-reversal দিন"]),
 "fake_countdown": ("add a countdown timer to my {i} offer page that resets every time someone visits", "আমার {i} অফার পেজে এমন কাউন্টডাউন টাইমার লাগাতে চাই যা প্রতিবার ভিজিটে রিসেট হয়", "amar {i} offer page e countdown timer chai ja protibar visit e reset hoy",
   "a timer that always resets is a fake deadline; it is deceptive advertising and visitors who notice stop trusting everything else on the page", "যে টাইমার সবসময় রিসেট হয় সেটা ভুয়া ডেডলাইন; এটা বিভ্রান্তিকর বিজ্ঞাপন, আর যে ভিজিটর ধরে ফেলে সে পেজের বাকি সবকিছুর ওপরও আস্থা হারায়",
   ["set a real end date for a real offer and honor it", "limit by something genuinely finite, such as monthly capacity or a cohort start date", "explain the value of acting now with true costs of waiting"], ["আসল অফারের আসল শেষ তারিখ ঠিক করে তা মানুন", "সত্যিকারের সীমিত কিছু দিয়ে সীমা দিন, যেমন মাসিক ক্ষমতা বা ব্যাচ শুরুর তারিখ", "অপেক্ষার সত্য খরচ দিয়ে এখনই সিদ্ধান্তের ভ্যালু ব্যাখ্যা করুন"]),
 "fake_scarcity": ("show 'only 2 left!' on every product in my {i} even though stock is plentiful", "আমার {i} এর সব প্রোডাক্টে 'মাত্র ২টা বাকি!' দেখাতে চাই, যদিও স্টক প্রচুর", "amar {i} er shob product e 'matro 2 ta baki!' dekhate chai, stock onek thakleo",
   "false scarcity is a lie told to rush the buyer; it raises returns and complaints and erodes repeat business", "ভুয়া scarcity ক্রেতাকে তাড়াহুড়ো করাতে বলা মিথ্যা; এতে রিটার্ন ও অভিযোগ বাড়ে এবং রিপিট বিজনেস কমে",
   ["show real stock levels only when stock is genuinely low", "run a true limited batch or pre-order with a firm quantity", "use real seasonal or event deadlines"], ["স্টক সত্যিই কম হলেই আসল স্টক দেখান", "নির্দিষ্ট পরিমাণের সত্যিকারের limited batch বা pre-order চালান", "আসল মৌসুমি বা ইভেন্টের ডেডলাইন ব্যবহার করুন"]),
 "buy_reviews": ("help me plan buying 100 fake 5-star reviews for my {i}", "আমার {i} এর জন্য ১০০টা ফেক ৫-স্টার রিভিউ কেনার প্ল্যান করতে সাহায্য করো", "amar {i} er jonno 100 ta fake 5-star review kinte chai, plan koro",
   "bought reviews violate platform rules, risk account bans, and can mislead customers into purchases they regret", "কেনা রিভিউ প্ল্যাটফর্মের নিয়ম ভাঙে, অ্যাকাউন্ট ব্যান হওয়ার ঝুঁকি আনে এবং ক্রেতাকে এমন কেনায় বিভ্রান্ত করে যার জন্য পরে আফসোস হয়",
   ["ask every happy customer for a review right after delivery with a one-tap link", "make reviewing easy with a short template of questions, not scripted praise", "respond publicly and well to critical reviews"], ["প্রতিটা সন্তুষ্ট ক্রেতাকে ডেলিভারির পরপর এক-ট্যাপ লিংকে রিভিউ চান", "সাজানো প্রশংসা নয়, ছোট প্রশ্নের টেমপ্লেট দিয়ে রিভিউ দেওয়া সহজ করুন", "নেতিবাচক রিভিউয়ে প্রকাশ্যে ও ভালোভাবে সাড়া দিন"]),
 "fake_logos": ("put big brand logos on my {i} website as clients, though we have not worked with them", "আমার {i} ওয়েবসাইটে বড় ব্র্যান্ডের লোগো ক্লায়েন্ট হিসেবে দিতে চাই, যদিও তাদের সাথে কাজ করিনি", "amar {i} website e boro brand er logo client hishebe dite chai, kaj kori nai",
   "claiming clients you do not have is false advertising and can lead to legal complaints and instant loss of credibility if one of those brands notices", "যাদের সাথে কাজ করেননি তাদের ক্লায়েন্ট দাবি করা মিথ্যা বিজ্ঞাপন; ওই ব্র্যান্ডের কেউ খেয়াল করলে আইনি অভিযোগ ও তাৎক্ষণিক বিশ্বাসযোগ্যতা হারানোর ঝুঁকি",
   ["show your real clients, even small ones, with a short result", "publish sample work and a clear process", "work with one recognizable brand through a small project and ask for permission to cite it"], ["ছোট হলেও আসল ক্লায়েন্ট দেখান এবং সংক্ষিপ্ত ফলাফল দিন", "স্যাম্পল কাজ ও পরিষ্কার প্রসেস প্রকাশ করুন", "একটা পরিচিত ব্র্যান্ডের সাথে ছোট প্রজেক্ট করে উল্লেখ করার অনুমতি নিন"]),
 "fake_before_after": ("create before-and-after results for my {i} using edited images of outcomes that never happened", "আমার {i} এর জন্য এমন before-after ফলাফল বানাতে চাই যা এডিট করা ছবি, আসলে ঘটেনি", "amar {i} er jonno edit kora before-after result banate chai, jeta kokhono hoy nai",
   "fabricated results mislead customers into paying for outcomes you cannot deliver, which leads to refunds, complaints and possible legal exposure", "বানানো ফলাফল ক্রেতাকে এমন ফলাফলের জন্য টাকা দিতে বিভ্রান্ত করে যা আপনি দিতে পারবেন না; এতে রিফান্ড, অভিযোগ ও আইনি ঝুঁকি আসে",
   ["document one genuine small project start to finish, with permission", "show process and honest ranges of typical results", "offer a small pilot so prospects can see the result themselves"], ["অনুমতি নিয়ে একটা আসল ছোট প্রজেক্ট শুরু থেকে শেষ ডকুমেন্ট করুন", "প্রসেস ও সাধারণ ফলাফলের সৎ পরিসর দেখান", "ছোট পাইলট দিন যাতে প্রসপেক্ট নিজেই ফলাফল দেখতে পায়"]),
}
def g_ethics_all():
    out = []
    for key, v in ETH.items():
        for ind in IND:
            for lang in ["en", "bn", "mixed"]:
                n = random.choice([200, 500, 1000]); en = lang == "en"
                if en: u = "Please " + v[0].format(i=ind[0], n=n) + "."
                elif lang == "bn": u = v[1].format(i=ind[1], n=x_n(n)) + "।"
                else: u = v[2].format(i=ind[1], n=n)
                alts_e = "\n".join(f"- {s}" for s in v[7]) if False else "\n".join(f"{i + 1}. {s}" for i, s in enumerate(v[5]))
                alts_b = "\n".join(f"{x_n(i + 1)}. {s}" for i, s in enumerate(v[6]))
                if en:
                    a = f"""I will not write that one, because {v[3]}. You can get most of the conversion benefit honestly.

{H1}
1. **Why it backfires:** the short-term lift is borrowed from future trust and referrals.
2. **What buyers actually need:** reduced perceived risk and visible proof, which truthful material can give.

{H2}
{alts_e}

{H3}
Honest proof builds slowly but compounds. Next step: pick the first option, do it this week, and measure the change on your page or message."""
                else:
                    a = f"""এটা আমি লিখব না, কারণ {v[4]}। সততার পথেই আপনি conversion এর বেশিরভাগ সুবিধা পেতে পারেন।

{H1}
১. **কেন উল্টো ফল দেয়:** স্বল্পমেয়াদি লাভ ভবিষ্যতের বিশ্বাস ও রেফারেল থেকে ধার করা।
২. **ক্রেতার আসলে কী দরকার:** ঝুঁকির অনুভূতি কমানো ও দৃশ্যমান প্রমাণ, যা সত্য উপাদান দিয়েই দেওয়া যায়।

{H2}
{alts_b}

{H3}
সৎ প্রমাণ ধীরে তৈরি হয় কিন্তু চক্রবৃদ্ধি হারে বাড়ে। পরবর্তী ধাপ: প্রথম অপশনটা এই সপ্তাহেই করুন এবং পেজ বা মেসেজে পরিবর্তন মাপুন।"""
                out.append((u, a, f"ethics_{key}", lang))
    return out
def x_n(n): return str(n).translate(BNMAP)

# ---------------------------------------------------------------- 17 Bangladesh market
BD = {
 "advance": ("customers refuse to pay anything in advance for my {i}", "আমার {i} এ ক্রেতারা কোনো advance দিতে চায় না", "amar {i} e customer advance dite chay na",
   ["Trust gap: many buyers have been burned by pages that took money and did not deliver, so advance equals risk for them.", "Loss framing: paying first feels like a certain loss, while COD feels like a free option.", "Your cost: no commitment means more cancelled orders and returns."],
   ["ট্রাস্ট গ্যাপ: অনেক ক্রেতা টাকা নিয়ে ডেলিভারি না দেওয়া পেজে ঠকেছেন, তাই advance মানে তাদের কাছে ঝুঁকি।", "Loss framing: আগে টাকা দেওয়া নিশ্চিত ক্ষতি মনে হয়, আর COD মনে হয় বিনা খরচের অপশন।", "আপনার খরচ: কমিটমেন্ট না থাকলে বাতিল ও রিটার্ন বেশি হয়।"],
   ["Ask only for the delivery charge or a small token via bKash/Nagad, and show a clear refund rule.", "Offer a return window and an unboxing video so the risk shifts to you.", "Give COD as the default and make the token a visible option that comes with a small real perk."],
   ["শুধু ডেলিভারি চার্জ বা ছোট টোকেন bKash/Nagad এ চান এবং পরিষ্কার রিফান্ড নীতি দেখান।", "রিটার্ন উইন্ডো ও আনবক্সিং ভিডিও দিন যাতে ঝুঁকি আপনার দিকে সরে।", "COD ডিফল্ট রাখুন এবং টোকেনকে ছোট আসল সুবিধাসহ দৃশ্যমান অপশন করুন।"]),
 "discount_culture": ("customers keep bargaining and waiting for discounts on my {i}", "আমার {i} এ ক্রেতারা সবসময় দর-কষাকষি ও ডিসকাউন্টের অপেক্ষা করে", "amar {i} e customer shobsomoy dor-koshakoshi ar discount er opekkha kore",
   ["Anchoring: if the first price they saw was a discounted one, that becomes the reference.", "Bargaining is part of the buying ritual; many buyers want to feel they won something.", "Frequent sales train customers to wait."],
   ["Anchoring: প্রথম যে ছাড়ের দাম দেখেছে সেটাই রেফারেন্স হয়ে যায়।", "দর-কষাকষি কেনাকাটার আচারের অংশ; অনেক ক্রেতা কিছু জিতেছেন অনুভব করতে চান।", "ঘন ঘন সেল ক্রেতাকে অপেক্ষা করতে শেখায়।"],
   ["Keep a stable list price and give structured 'wins' instead: a free add-on, free delivery over a threshold, a bundle.", "Use a small number of genuine, announced sale windows rather than constant offers.", "Give a fixed-price policy and explain it (quality, fair pricing for everyone)."],
   ["স্থির লিস্ট প্রাইস রাখুন এবং এর বদলে কাঠামোবদ্ধ 'জয়' দিন: ফ্রি অ্যাড-অন, নির্দিষ্ট অঙ্কের ওপর ফ্রি ডেলিভারি, বান্ডল।", "ধারাবাহিক অফারের বদলে অল্প কয়েকটা সত্যিকারের ঘোষিত সেল সময় রাখুন।", "ফিক্সড প্রাইস নীতি দিন ও ব্যাখ্যা করুন (মান, সবার জন্য ন্যায্য দাম)।"]),
 "page_trust": ("people do not trust my Facebook page for my {i} and ask many questions before buying", "আমার {i} এর ফেসবুক পেজকে মানুষ বিশ্বাস করে না, কেনার আগে অনেক প্রশ্ন করে", "amar {i} er facebook page ke manush bishwas kore na, kenar age onek proshno kore",
   ["Identity: buyers cannot see who is behind the page.", "Proof: no verifiable evidence of past deliveries.", "Risk: they cannot undo a bad purchase."],
   ["পরিচয়: পেজের পেছনে কে আছে ক্রেতা দেখতে পান না।", "প্রমাণ: আগের ডেলিভারির যাচাইযোগ্য প্রমাণ নেই।", "ঝুঁকি: খারাপ কেনা ফেরানোর উপায় তারা দেখেন না।"],
   ["Show the owner, address, phone and trade license; do a short video introduction.", "Post real delivery photos and customer messages with permission.", "State a clear return and refund policy and keep it."],
   ["মালিকের মুখ, ঠিকানা, ফোন ও ট্রেড লাইসেন্স দেখান; ছোট ভিডিও পরিচিতি দিন।", "অনুমতি নিয়ে আসল ডেলিভারির ছবি ও ক্রেতার মেসেজ পোস্ট করুন।", "পরিষ্কার রিটার্ন ও রিফান্ড নীতি দিন এবং তা মেনে চলুন।"]),
 "courier": ("late and failed courier deliveries are hurting my {i} reviews", "দেরি ও ব্যর্থ কুরিয়ার ডেলিভারি আমার {i} এর রিভিউ নষ্ট করছে", "courier delivery late/fail hoye amar {i} er review nosto hocche",
   ["Delivery is the moment of truth: customers blame the brand, not the courier.", "Failed deliveries come from wrong addresses, unreachable phones and unconfirmed orders.", "Each failure costs courier fees both ways plus a lost customer."],
   ["ডেলিভারি হলো সত্যের মুহূর্ত: ক্রেতা কুরিয়ারকে নয়, ব্র্যান্ডকে দোষ দেন।", "ব্যর্থ ডেলিভারির কারণ ভুল ঠিকানা, ফোন বন্ধ, ও অনির্ধারিত অর্ডার।", "প্রতিটা ব্যর্থতায় দুই দিকের কুরিয়ার ফি ও একজন ক্রেতা হারানো।"],
   ["Confirm address and phone before dispatch and send tracking updates.", "Compare 2 couriers on delivery success rate by area and route accordingly.", "Set honest delivery time expectations upfront and add a buffer."],
   ["পাঠানোর আগে ঠিকানা ও ফোন কনফার্ম করুন এবং ট্র্যাকিং আপডেট দিন।", "এলাকাভিত্তিক সফল ডেলিভারির হারে ২টা কুরিয়ার তুলনা করে সেভাবে রুট করুন।", "শুরুতেই সৎ ডেলিভারি সময় জানান এবং বাফার রাখুন।"]),
 "eid_season": ("planning for Eid season demand spikes for my {i}", "আমার {i} এর জন্য ঈদ মৌসুমের চাহিদা বৃদ্ধির পরিকল্পনা করতে চাই", "amar {i} er jonno Eid season e demand barar plan korte chai",
   ["Demand is concentrated in a few weeks, so stockouts and delivery delays cost more than usual.", "Buyers decide earlier because of delivery uncertainty near Eid.", "Cash needs peak before revenue arrives (inventory, extra staff)."],
   ["চাহিদা কয়েক সপ্তাহে কেন্দ্রীভূত, তাই স্টকআউট ও ডেলিভারি দেরির ক্ষতি সাধারণের চেয়ে বেশি।", "ঈদের আগে ডেলিভারির অনিশ্চয়তায় ক্রেতারা আগে সিদ্ধান্ত নেন।", "রেভিনিউ আসার আগেই ক্যাশের চাহিদা শীর্ষে ওঠে (ইনভেন্টরি, বাড়তি স্টাফ)।"],
   ["Forecast with last year's weekly data and set a real order cut-off date that is honest about delivery.", "Pre-order campaigns with a clear quantity limit reduce overstock risk.", "Secure inventory financing or supplier terms early and plan cash weekly."],
   ["গত বছরের সাপ্তাহিক ডেটা দিয়ে পূর্বাভাস করুন এবং ডেলিভারি নিয়ে সৎ থেকে আসল অর্ডার cut-off তারিখ দিন।", "নির্দিষ্ট পরিমাণ সীমার প্রি-অর্ডার ক্যাম্পেইন অতিরিক্ত স্টকের ঝুঁকি কমায়।", "আগেই ইনভেন্টরির অর্থায়ন বা সাপ্লায়ার শর্ত নিশ্চিত করুন এবং সাপ্তাহিক ক্যাশ পরিকল্পনা করুন।"]),
 "messenger_sales": ("most of my {i} sales happen in Messenger chats and I lose many leads there", "আমার {i} এর বেশিরভাগ বিক্রি Messenger চ্যাটে হয় আর অনেক লিড হারাচ্ছি", "amar {i} er onek sales Messenger chat e hoy ar onek lead hariye fela",
   ["Response speed: buyers message several shops and often buy from the first useful reply.", "Repeated questions (price, size, delivery) waste time and cause inconsistent answers.", "Without follow-up, interested buyers fade away."],
   ["সাড়ার গতি: ক্রেতা কয়েকটা দোকানে মেসেজ করেন এবং প্রায়ই প্রথম কার্যকর উত্তরদাতার কাছে কেনেন।", "বারবার একই প্রশ্ন (দাম, সাইজ, ডেলিভারি) সময় নষ্ট করে ও অসঙ্গত উত্তর আনে।", "ফলো-আপ ছাড়া আগ্রহী ক্রেতা হারিয়ে যায়।"],
   ["Create saved replies for the top questions and answer within minutes during peak hours.", "Track every lead in a simple sheet with status and follow up once after 24 hours.", "Put price and delivery details in the post so chats start further down the funnel."],
   ["শীর্ষ প্রশ্নগুলোর জন্য saved reply বানান এবং ব্যস্ত সময়ে কয়েক মিনিটে উত্তর দিন।", "প্রতিটা লিড স্ট্যাটাসসহ সাধারণ শিটে ট্র্যাক করুন এবং ২৪ ঘণ্টা পরে একবার ফলো-আপ করুন।", "পোস্টে দাম ও ডেলিভারির তথ্য রাখুন যাতে চ্যাট ফানেলের আরও নিচ থেকে শুরু হয়।"]),
}
def g_bd_all():
    out = []
    for key, v in BD.items():
        for ind in IND:
            for lang in ["en", "bn", "mixed"]:
                if lang == "en": u = f"In Bangladesh, {v[0].format(i=ind[0])}. What should I do?"
                elif lang == "bn": u = f"বাংলাদেশে {v[1].format(i=ind[1])}। কী করা উচিত?"
                else: u = v[2].format(i=ind[1]).capitalize() + ". ki kora uchit?"
                if lang == "en":
                    a = f"""{H1}
""" + "\n".join(f"{i + 1}. {s}" for i, s in enumerate(v[3])) + f"""

{H2}
""" + "\n".join(f"- {s}" for s in v[5]) + f"""

{H3}
These are patterns, not certainties; your own data decides. Pick one change, run it for two weeks and compare conversion and net profit per order before rolling it out."""
                else:
                    a = f"""{H1}
""" + "\n".join(f"{x_n(i + 1)}. {s}" for i, s in enumerate(v[4])) + f"""

{H2}
""" + "\n".join(f"- {s}" for s in v[6]) + f"""

{H3}
এগুলো প্যাটার্ন, নিশ্চয়তা নয়; আপনার নিজের ডেটাই সিদ্ধান্ত দেবে। একটা পরিবর্তন বেছে ২ সপ্তাহ চালান এবং ছড়িয়ে দেওয়ার আগে conversion ও প্রতি অর্ডারে নেট লাভ তুলনা করুন।"""
                out.append((u, a, f"bd_{key}", lang))
    return out

# ---------------------------------------------------------------- assemble
RANDOM_GENS = [(g_ltv, 220), (g_runway, 200), (g_ev, 220), (g_discount, 200), (g_breakeven, 160), (g_cod, 220), (g_retention, 120),
               (g_priceinc, 140), (g_channel, 200), (g_rice, 160), (g_service, 200), (g_decoy, 120), (g_neg, 200)]
rows, seen = [], set()
def add(u, a, topic, lang):
    k = re.sub(r"\s+", " ", u).strip().lower()
    if k in seen: return
    seen.add(k)
    rows.append({"meta": {"topic": topic, "lang": lang}, "messages": [{"role": "system", "content": random.choice(SYS_VARIANTS)}, {"role": "user", "content": u}, {"role": "assistant", "content": a}]})
for g, n in RANDOM_GENS:
    made, tries = 0, 0
    while made < n and tries < n * 6:
        tries += 1; lang = pick_lang(); r_ = g(lang)
        if r_ is None: continue
        before = len(rows); add(r_[0], r_[1], r_[2], lang)
        if len(rows) > before: made += 1
for fn in (g_bias_all, g_mece_all, g_ethics_all, g_bd_all):
    for u, a, t, l in fn(): add(u, a, t, l)

random.shuffle(rows)
bad = [r_ for r_ in rows if re.search(r"\{[a-z_]+\}|\bnan\b|\binf\b", r_["messages"][2]["content"])]
assert not bad, f"placeholder/NaN leak: {len(bad)}"
n_eval = int(len(rows) * 0.05); ev, tr = rows[:n_eval], rows[n_eval:]
def dump(path, rs, strip_meta=False):
    with open(path, "w", encoding="utf-8") as f:
        for r_ in rs:
            o = {"messages": r_["messages"]} if strip_meta else r_
            f.write(json.dumps(o, ensure_ascii=False) + "\n")
import os
O = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data") + os.sep
os.makedirs(O, exist_ok=True)
dump(O + "business_strategist_train.jsonl", tr, True); dump(O + "business_strategist_eval.jsonl", ev, True); dump(O + "business_strategist_full_with_meta.jsonl", rows)
print("total", len(rows), "train", len(tr), "eval", len(ev))
print(collections.Counter(r_["meta"]["lang"] for r_ in rows))
for t, c in sorted(collections.Counter(re.sub(r"_.*", "", r_["meta"]["topic"]) if r_["meta"]["topic"].startswith(("bias", "ethics", "bd_")) else r_["meta"]["topic"] for r_ in rows).items()): print(f"  {t}: {c}")
