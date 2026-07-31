from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from enum import Enum, auto

logger = logging.getLogger(__name__)


class QueryCategory(Enum):
    GREETING = auto()
    FAREWELL = auto()
    THANKS = auto()
    ASSISTANT_IDENTITY = auto()
    ASSISTANT_CAPABILITIES = auto()
    SYSTEM_INFORMATION = auto()
    DOCUMENT_QUERY = auto()
    OUT_OF_DOMAIN = auto()
    MIXED = auto()


_FAREWELL_MSG: str = "Goodbye! Feel free to come back if you need anything else."
_GRATITUDE_MSG: str = "You're welcome! Let me know if you have any other questions."
_GREETING_MSG: str = "Hello! How can I help you with your documents today?"


_GREETING_PATTERNS: list[re.Pattern] = [
    re.compile(
        r"^(hi|hello|hey|hey there|greetings|good\s*(morning|afternoon|evening))[\s\.,!]*$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^(what'?s up|sup|howdy|how are you|how'?s it going|how are things)[\s\?!]*$",
        re.IGNORECASE,
    ),
]

_FAREWELL_PATTERNS: list[re.Pattern] = [
    re.compile(
        r"^(bye|goodbye|see you|see ya|talk (to you )?later|cya|gotta go|take care)[\s\.,!]*$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^see you (later|soon|around|tomorrow)[\s\.,!]*$",
        re.IGNORECASE,
    ),
    re.compile(r"^(good night|goodnight|gn|night)[\s\.,!]*$", re.IGNORECASE),
]

_THANKS_PATTERNS: list[re.Pattern] = [
    re.compile(r"^(thanks|thank you|thankyou|ty|thx)[\s\.,!]*$", re.IGNORECASE),
    re.compile(
        r"^(that'?s helpful|appreciate it|much appreciated|thanks a lot|thank you so much)[\s\.,!]*$",
        re.IGNORECASE,
    ),
]

_IDENTITY_PATTERNS: list[re.Pattern] = [
    re.compile(
        r"^(who (are you|made you|created you)|what (are you|is your name))[\s\?!]*$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^tell me about yourself[\s\?!]*$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^are you\s+.*[\s\?!]*$",
        re.IGNORECASE,
    ),
]

_CAPABILITIES_PATTERNS: list[re.Pattern] = [
    re.compile(
        r"^(what (can you do|are your capabilities|are your features|"
        r"do you do|are your functions|kind of.*are you))[\s\?!]*$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^(how (can you help|do you work|are you useful))[\s\?!]*$",
        re.IGNORECASE,
    ),
    re.compile(
        r"^can you\s+(summariz|compar|answer|search|explain|help|read|analyz|interpret|"
        r"process|handle|work|deal|do|understand)[\s\?!]*"
        r"(?!.*\b(documents?|pdfs?|files?)\b)",
        re.IGNORECASE,
    ),
    re.compile(
        r"^(what (kinds?|types?) of (things|questions|topics|subjects).*(can|should) I)",
        re.IGNORECASE,
    ),
    re.compile(
        r"^(what\s+(file\s*types?|formats?|extensions?|kinds?|types?)\s+"
        r"(do\s+)?(you|it)\s+(support|accept|handle|process|read|understand|work\s*with))",
        re.IGNORECASE,
    ),
    re.compile(
        r"^(can\s+(you|it)\s+(read|process|handle|parse|index|analyze|understand|"
        r"deal\s+with|work\s+with)\s+.*"
        r"\b(pdfs?|images?|photos?|pictures?|docs?|docx|word|"
        r"excel|xls[xm]?|pptx?|powerpoint|txt|csv|json|md|markdown)\b)",
        re.IGNORECASE,
    ),
]

_MIXED_PATTERNS: list[re.Pattern] = [
    re.compile(
        r"\b(can you|how do you|can it|how does this)\b.*\b(documents?|pdfs?|files?|knowledge)"
        r"|"
        r"\b(documents?|pdfs?|files?|knowledge)\b.*\b(can you|how do you|can it|how does this)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(show|help) me (how|to|with|use|find|search|understand).*\b(documents?|pdfs?|files?)",
        re.IGNORECASE,
    ),
]

_OUT_OF_DOMAIN_PATTERNS: list[re.Pattern] = [
    re.compile(
        r"\b(weather (forecast|today|tomorrow|report)|what'?s the weather|what is the weather|"
        r"what'?s? (is )?todays? weather|weather (this|next) (week|month))\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(latest news|breaking news|current events|what'?s happening|"
        r"what'?s? (new|up) in the news)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(stock (price|market|ticker|symbol)|share price|market cap|"
        r"how is the (market|stock) doing)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(sports (score|game|match|result|team)|who won|cricket|"
        r"football (score|match|game|result)|basketball|baseball)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b((play|hear|recommend) (music|song|playlist|podcast))\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"^(set a timer|set a reminder|remind me|schedule|create an event)",
        re.IGNORECASE,
    ),
]

_DOCUMENT_QUERY_KEYWORDS: list[re.Pattern] = [
    re.compile(r"\b(summarize|compare|contrast|list|find|search)\b", re.IGNORECASE),
    re.compile(
        r"\b(what does (the|this|my) document say|tell me about|explain|overview|"
        r"describe|what (is|are|does) .*\b(in|from|according to) (the |these |my |our )?(documents?|"
        r"knowledge base|files?|notes?|content|text|information))\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"^\w+\s+(vs\.?|versus|compared? to|difference between)\s+\w+",
        re.IGNORECASE,
    ),
    re.compile(
        r"(how (to|do|can|would)|steps? to|process for|procedure|guide|walkthrough)",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(pros?|cons?|advantages?|disadvantages?|benefits?|drawbacks?|strengths?|weaknesses?)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(types? of|kinds? of|examples? of|categories? of)\b",
        re.IGNORECASE,
    ),
]

_SYSTEM_QUERY_KEYWORDS: list[tuple[re.Pattern, str]] = [
    (
        re.compile(
            r"\b(how many|number of|count of)\s*(vectors?|chunks?|embeddings?|documents?)\b",
            re.IGNORECASE,
        ),
        "vector_count",
    ),
    (
        re.compile(
            r"\b(what|which)\s+(llm|model|ai)\s+(are you|do you use|is running|you got|you using)\b",
            re.IGNORECASE,
        ),
        "llm_model",
    ),
    (
        re.compile(
            r"\b(what|which)\s+(embedding|embedding model)\s+(are you|do you use|)\b",
            re.IGNORECASE,
        ),
        "embedding_model",
    ),
    (
        re.compile(
            r"^(what|which)\s+(embedding|embedding model)[\s\?!]*$",
            re.IGNORECASE,
        ),
        "embedding_model",
    ),
    (
        re.compile(
            r"\b(what|which)\s+(vector (store|database)|database)\s+(are you|do you use)\b",
            re.IGNORECASE,
        ),
        "vector_store",
    ),
    (
        re.compile(
            r"\b(what version|which version|version number)[\s\?!]*$", re.IGNORECASE
        ),
        "version",
    ),
    (
        re.compile(
            r"\b(system status|are you healthy|health check|status check)\b",
            re.IGNORECASE,
        ),
        "system_status",
    ),
]


@dataclass
class ClassificationResult:
    category: QueryCategory
    system_intent: str | None = None


class QueryRouter:
    def classify(self, text: str) -> ClassificationResult:
        stripped = text.strip()
        if not stripped:
            return ClassificationResult(QueryCategory.GREETING)

        # 1. GREETING — exact match on greeting patterns
        if any(p.match(stripped) for p in _GREETING_PATTERNS):
            return ClassificationResult(QueryCategory.GREETING)

        # 2. FAREWELL
        if any(p.match(stripped) for p in _FAREWELL_PATTERNS):
            return ClassificationResult(QueryCategory.FAREWELL)

        # 3. THANKS
        if any(p.match(stripped) for p in _THANKS_PATTERNS):
            return ClassificationResult(QueryCategory.THANKS)

        # 4. SYSTEM_INFORMATION — before identity/capabilities because
        #    "what model are you" is a system query, not identity
        for pattern, intent in _SYSTEM_QUERY_KEYWORDS:
            if pattern.search(stripped):
                return ClassificationResult(QueryCategory.SYSTEM_INFORMATION, intent)

        # 5. ASSISTANT_IDENTITY — "who are you", "what are you"
        if any(p.match(stripped) for p in _IDENTITY_PATTERNS):
            return ClassificationResult(QueryCategory.ASSISTANT_IDENTITY)

        # 6. ASSISTANT_CAPABILITIES — "what can you do"
        if any(p.match(stripped) for p in _CAPABILITIES_PATTERNS):
            return ClassificationResult(QueryCategory.ASSISTANT_CAPABILITIES)

        # 7. MIXED — combines capability + document references
        if any(p.search(stripped) for p in _MIXED_PATTERNS):
            return ClassificationResult(QueryCategory.MIXED)

        # 8. OUT_OF_DOMAIN — clearly not about documents
        if any(p.search(stripped) for p in _OUT_OF_DOMAIN_PATTERNS):
            return ClassificationResult(QueryCategory.OUT_OF_DOMAIN)

        # 9. DOCUMENT_QUERY — keywords suggest document retrieval is needed
        if any(p.search(stripped) for p in _DOCUMENT_QUERY_KEYWORDS):
            return ClassificationResult(QueryCategory.DOCUMENT_QUERY)

        # Default: DOCUMENT_QUERY — assume any unclassified query is
        # about the documents (better to retrieve and be wrong than
        # to refuse a legitimate document question)
        return ClassificationResult(QueryCategory.DOCUMENT_QUERY)

    def get_static_response(self, category: QueryCategory) -> str | None:
        match category:
            case QueryCategory.GREETING:
                return _GREETING_MSG
            case QueryCategory.FAREWELL:
                return _FAREWELL_MSG
            case QueryCategory.THANKS:
                return _GRATITUDE_MSG
            case _:
                return None
