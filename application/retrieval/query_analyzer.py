import re
from dataclasses import dataclass, field
from typing import Optional, List


LEGAL_PHRASES = [
    "miễn tiền chậm nộp",
    "xử phạt chậm nộp",
    "chậm nộp thuế",
    "quản lý thuế quốc tế",
    "đăng ký thuế",
    "khai thuế",
    "nộp thuế",
    "hoàn thuế",
    "gia hạn nộp thuế",
    "kiểm tra thuế",
    "quản lý rủi ro",
    "cưỡng chế thi hành quyết định hành chính về quản lý thuế",
    "hóa đơn điện tử",
    "biên lai thu tiền phạt",
    "hộ kinh doanh",
    "cá nhân kinh doanh",
]


@dataclass
class QueryInfo:
    raw_question: str
    cau_hoi_chuan_hoa: str

    # Legal hierarchy
    dieu: Optional[int] = None
    khoan: Optional[int] = None
    diem: Optional[str] = None
    chuong: Optional[str] = None

    # Query intent
    y_dinh: Optional[str] = None

    # Retrieval helpers
    cum_tu_chinh_xac: List[str] = field(default_factory=list)
    loai_van_ban: Optional[str] = None
    chu_de: Optional[str] = None

    # Backward-compatible aliases
    @property
    def normalized_question(self) -> str:
        return self.cau_hoi_chuan_hoa

    @property
    def article(self) -> Optional[int]:
        return self.dieu

    @property
    def clause(self) -> Optional[int]:
        return self.khoan

    @property
    def point(self) -> Optional[str]:
        return self.diem

    @property
    def chapter(self) -> Optional[str]:
        return self.chuong

    @property
    def intent(self) -> Optional[str]:
        return self.y_dinh

    @property
    def exact_phrases(self) -> List[str]:
        return self.cum_tu_chinh_xac


def detect_intent(q: str) -> Optional[str]:
    if any(x in q for x in ["là gì", "khái niệm", "định nghĩa", "nội dung là gì", "hiểu như thế nào"]):
        return "định_nghĩa"

    if any(x in q for x in ["trường hợp nào", "điều kiện", "khi nào", "được miễn", "được hoàn", "được giảm"]):
        return "điều_kiện"

    if any(x in q for x in ["thủ tục", "quy trình", "cách thực hiện", "hồ sơ", "cần giấy tờ gì"]):
        return "thủ_tục"

    if any(x in q for x in ["xử phạt", "mức phạt", "vi phạm", "chậm nộp", "tiền phạt"]):
        return "xử_phạt"

    if any(x in q for x in ["nghĩa vụ", "phải làm gì", "trách nhiệm"]):
        return "nghĩa_vụ"

    return None


def detect_document_type(q: str) -> Optional[str]:
    if "luật" in q:
        return "luật"
    if "nghị định" in q or "nghi dinh" in q:
        return "nghị_định"
    if "thông tư" in q or "thong tu" in q:
        return "thông_tư"
    if "công văn" in q or "cong van" in q:
        return "công_văn"
    return None


def detect_topic(q: str) -> Optional[str]:
    topic_patterns = [
        ("chậm nộp", "chậm_nộp_thuế"),
        ("hóa đơn điện tử", "hóa_đơn_điện_tử"),
        ("hoàn thuế", "hoàn_thuế"),
        ("khai thuế", "khai_thuế"),
        ("nộp thuế", "nộp_thuế"),
        ("đăng ký thuế", "đăng_ký_thuế"),
        ("tiền phạt", "thu_nộp_tiền_phạt_biên_lai"),
        ("biên lai", "thu_nộp_tiền_phạt_biên_lai"),
        ("hộ kinh doanh", "hộ_kinh_doanh"),
        ("cá nhân kinh doanh", "hộ_kinh_doanh"),
        ("quản lý thuế", "quản_lý_thuế"),
    ]

    for phrase, topic in topic_patterns:
        if phrase in q:
            return topic

    return None


def analyze_query(question: str) -> QueryInfo:
    q = (question or "").strip()
    q_norm = q.lower()

    dieu = None
    khoan = None
    diem = None
    chuong = None

    m = re.search(r"điều\s+(\d+)", q_norm)
    if m:
        dieu = int(m.group(1))

    m = re.search(r"khoản\s+(\d+)", q_norm)
    if m:
        khoan = int(m.group(1))

    m = re.search(r"điểm\s+([a-zđ])", q_norm)
    if m:
        diem = m.group(1)

    m = re.search(r"chương\s+([ivxlcdm0-9]+)", q_norm)
    if m:
        chuong = m.group(1).upper()

    phrases = [p for p in LEGAL_PHRASES if p in q_norm]

    return QueryInfo(
        raw_question=q,
        cau_hoi_chuan_hoa=q_norm,
        dieu=dieu,
        khoan=khoan,
        diem=diem,
        chuong=chuong,
        y_dinh=detect_intent(q_norm),
        cum_tu_chinh_xac=phrases,
        loai_van_ban=detect_document_type(q_norm),
        chu_de=detect_topic(q_norm),
    )
