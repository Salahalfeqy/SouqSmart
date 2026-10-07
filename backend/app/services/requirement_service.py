import re
from dataclasses import dataclass, field

AR_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩٬٫", "0123456789,.")


def normalize(text: str) -> str:
    text = (text or "").translate(AR_DIGITS).lower()
    text = re.sub(r"[ً-ٟـ]", "", text)
    text = text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا").replace("ة", "ه").replace("ى", "ي")
    return text


def is_arabic(text: str) -> bool:
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return False
    return sum("؀" <= c <= "ۿ" for c in letters) / len(letters) > 0.4


CATEGORY_KEYWORDS = {
    "smartphone": ["smartphone", "smartphones", "phone", "phones", "mobile", "mobiles", "موبايل", "موبايلات", "تليفون", "تلفون", "هاتف", "جوال", "فون"],
    "laptop": ["laptop", "laptops", "notebook", "لابتوب", "لاب توب", "لاب", "كمبيوتر محمول"],
    "headphones": ["headphone", "headphones", "earbuds", "earphones", "headset", "airpods", "سماعه", "سماعات", "ايربودز"],
}

BRAND_KEYWORDS = {
    "Samsung": ["samsung", "galaxy", "سامسونج"],
    "Xiaomi": ["xiaomi", "redmi", "poco", "شاومي", "ريدمي", "بوكو"],
    "Apple": ["apple", "iphone", "ايفون", "ابل", "airpods"],
    "Realme": ["realme", "ريلمي"],
    "Oppo": ["oppo", "اوبو"],
    "Lenovo": ["lenovo", "thinkpad", "لينوفو"],
    "HP": ["hp", "اتش بي"],
    "Dell": ["dell", "ديل"],
    "ASUS": ["asus", "اسوس", "ايسوس"],
    "Acer": ["acer", "ايسر"],
    "Sony": ["sony", "سوني"],
    "JBL": ["jbl", "جي بي ال"],
    "Anker": ["anker", "soundcore", "انكر"],
}

PRIORITY_KEYWORDS = {
    "camera": ["camera", "photo", "photos", "photography", "selfie", "تصوير", "كاميرا", "صور"],
    "gaming": ["gaming", "games", "game", "pubg", "جيمنج", "جيمينج", "العاب", "لعب", "جيمز"],
    "battery": ["battery", "بطاريه", "بطارية"],
    "display": ["display", "screen", "oled", "شاشه"],
    "performance": ["performance", "fast", "speed", "اداء", "سريع"],
    "programming": ["programming", "coding", "developer", "development", "برمجه", "برمجة"],
    "portability": ["portable", "portability", "lightweight", "light", "خفيف", "محمول"],
    "sound": ["sound", "bass", "audio", "صوت", "باس"],
    "anc": ["anc", "noise cancelling", "noise-cancelling", "noise cancellation", "عزل"],
    "storage": ["storage", "تخزين", "مساحه"],
}

MUST_HAVE_KEYWORDS = {
    "5g": ["5g"],
    "anc": ["anc", "noise cancelling", "noise-cancelling", "عزل"],
    "oled": ["oled"],
    "gpu": ["dedicated gpu", "كارت شاشه", "كرت شاشه", "rtx"],
}

INTENT_COMPARE = ["compare", " vs ", "versus", "difference between", "قارن", "مقارنه", "ولا", "الفرق"]
INTENT_REVIEWS = ["review", "reviews", "opinion", "opinions", "what do people think", "what do customers", "feedback", "ريفيو", "اراء", "رايكم", "تقييمات", "رأي الناس", "راي الناس", "الناس بتقول"]
INTENT_LIST = ["shopping list", "build a list", "make a list", "قائمه مشتريات", "قائمه شراء", "اعملي قائمه", "ليستة"]
INTENT_RESET = ["reset preferences", "clear preferences", "start over", "امسح التفضيلات", "ابدا من جديد"]
GREETINGS = ["hi", "hello", "hey", "مرحبا", "اهلا", "السلام عليكم", "ازيك", "صباح الخير", "مساء الخير", "هاي"]
NO_BUDGET = ["any budget", "no budget", "budget doesn't matter", "مفيش ميزانيه", "ميزانيتي مفتوحه", "مش مهم السعر"]

UNIT_AFTER = r"(?!\s*(?:gb|g\b|mah|inch|in\b|mp|hours?|hrs?|h\b|kg|hz|mm|w\b|tb|ram))"
NUM = r"(?<![\d,.])(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)(?!\d)"
MULT = r"\s*(k|thousand|الف|ألف)?"


def to_number(raw: str, mult: str | None) -> float:
    value = float(raw.replace(",", ""))
    if mult:
        value *= 1000
    return value


def has_word(text: str, word: str) -> bool:
    if re.search(r"[؀-ۿ]", word):
        return word in text
    return re.search(rf"(?<![a-z0-9]){re.escape(word)}(?![a-z0-9])", text) is not None


@dataclass
class Requirements:
    message: str = ""
    language: str = "en"
    intent: str = "recommend"
    categories: list = field(default_factory=list)
    budget: float | None = None
    min_price: float | None = None
    brands: list = field(default_factory=list)
    priorities: list = field(default_factory=list)
    must_have: list = field(default_factory=list)
    product_names: list = field(default_factory=list)
    no_budget: bool = False
    reset: bool = False

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items()}


def extract_budget(text: str):
    between = re.search(rf"(?:between|بين)\s*{NUM}{MULT}\s*(?:and|و|الي|to|-)\s*{NUM}{MULT}", text)
    if between:
        low = to_number(between.group(1), between.group(2))
        high = to_number(between.group(3), between.group(4) or between.group(2))
        return min(low, high), max(low, high)
    candidates = []
    for m in re.finditer(NUM + MULT + UNIT_AFTER, text):
        value = to_number(m.group(1), m.group(2))
        context = text[max(0, m.start() - 25): m.end() + 15]
        marked = bool(m.group(2)) or re.search(r"egp|le\b|جنيه|ج\b|budget|ميزاني|under|below|max|بحدود|حوالي|اقل من|تحت|في حدود|around|up to|within", context)
        currency_after = re.search(r"^\s*(egp|le\b|جنيه|ج\b)", text[m.end():])
        if currency_after and value >= 50:
            candidates.append(value)
        elif value >= 1000 and (marked or value >= 2000) and not re.match(r"20[12]\d$", m.group(1)):
            candidates.append(value)
        elif m.group(2) and 1 <= value < 1000:
            candidates.append(value)
    if candidates:
        return None, candidates[-1]
    return None, None


def extract_requirements(message: str, product_service=None, stored: dict | None = None) -> Requirements:
    raw = message or ""
    text = normalize(raw)
    req = Requirements(message=raw, language="ar" if is_arabic(raw) else "en")

    for cat, words in CATEGORY_KEYWORDS.items():
        if any(has_word(text, normalize(w)) for w in words):
            req.categories.append(cat)

    for brand, words in BRAND_KEYWORDS.items():
        if any(has_word(text, normalize(w)) for w in words):
            req.brands.append(brand)

    for pri, words in PRIORITY_KEYWORDS.items():
        if any(has_word(text, normalize(w)) for w in words):
            req.priorities.append(pri)
    if "anc" in req.priorities and "sound" in req.priorities and "headphones" not in req.categories:
        pass

    for feat, words in MUST_HAVE_KEYWORDS.items():
        if any(has_word(text, normalize(w)) for w in words):
            req.must_have.append(feat)

    low, high = extract_budget(text)
    req.min_price, req.budget = low, high
    req.no_budget = any(normalize(w) in text for w in NO_BUDGET)

    if product_service is not None:
        req.product_names = [p["id"] for p in product_service.find_by_names(raw)]

    padded = f" {text} "
    if any(normalize(w) in padded for w in INTENT_RESET):
        req.reset = True
        req.intent = "reset"
    elif any(normalize(w) in padded for w in INTENT_LIST):
        req.intent = "shopping_list"
    elif len(req.categories) >= 2 and (req.budget or any(w in text for w in ["and", " و"])) and not req.product_names:
        req.intent = "shopping_list"
    elif any(normalize(w) in padded for w in INTENT_REVIEWS):
        req.intent = "reviews"
    elif len(req.product_names) >= 2 or (any(normalize(w) in padded for w in INTENT_COMPARE) and req.product_names):
        req.intent = "compare"
    elif req.product_names and not (req.budget or req.priorities):
        req.intent = "compare"
    elif not (req.categories or req.budget or req.brands or req.priorities or req.must_have or req.product_names):
        words = text.split()
        if any(has_word(text, normalize(g)) for g in GREETINGS) and len(words) <= 6:
            req.intent = "greeting"
        elif stored and (stored.get("preferred_categories") or stored.get("budget")) and any(w in text for w in ["best", "show", "recommend", "افضل", "وريني", "اختار", "احسن"]):
            req.intent = "recommend"
        else:
            req.intent = "clarify"
    else:
        req.intent = "recommend"
    return req
