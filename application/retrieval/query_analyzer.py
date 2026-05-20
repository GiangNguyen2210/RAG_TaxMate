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
    "hóa đơn điện tử khởi tạo từ máy tính tiền",
    "biên lai thu tiền phạt",
    "tiền chậm nộp phạt",
    "chậm nộp phạt",
    "hộ kinh doanh",
    "cá nhân kinh doanh",
]


@dataclass
class QueryInfo:
    raw_question: str
    cau_hoi_chuan_hoa: str

    dieu: Optional[int] = None
    khoan: Optional[int] = None
    diem: Optional[str] = None
    chuong: Optional[str] = None

    y_dinh: Optional[str] = None

    ma_van_ban: Optional[str] = None
    ten_van_ban: Optional[str] = None
    loai_van_ban: Optional[str] = None

    cum_tu_chinh_xac: List[str] = field(default_factory=list)
    chu_de: Optional[str] = None
    legal_topic: Optional[str] = None

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


def detect_document(q: str) -> dict:
    if "luật quản lý thuế" in q or "108/2025" in q or "108-2025" in q:
        return {
            "ma_van_ban": "108_2025_QH15",
            "ten_van_ban": "Luật quản lý thuế 108/2025/QH15",
            "loai_van_ban": "luật",
        }

    if "68/2026" in q or "68-2026" in q or "nghị định 68" in q:
        return {
            "ma_van_ban": "68_2026_ND_CP",
            "ten_van_ban": "68-2026-ND-CP",
            "loai_van_ban": "nghị_định",
        }

    if "70/2025" in q or "70-2025" in q or "nghị định 70" in q:
        return {
            "ma_van_ban": "70_2025_ND_CP",
            "ten_van_ban": "70-2025-ND-CP",
            "loai_van_ban": "nghị_định",
        }

    if "18/2023" in q or "18-2023" in q or "thông tư 18" in q:
        return {
            "ma_van_ban": "18_2023_TT_BTC",
            "ten_van_ban": "Thông tư 18/2023/TT-BTC",
            "loai_van_ban": "thông_tư",
        }

    return {}


def detect_intent(q: str) -> Optional[str]:
    if any(x in q for x in ["là gì", "khái niệm", "định nghĩa", "nội dung là gì", "hiểu như thế nào"]):
        return "định_nghĩa"

    if any(x in q for x in ["trường hợp nào", "điều kiện", "khi nào", "được miễn", "được hoàn", "được giảm"]):
        return "điều_kiện"

    if any(x in q for x in ["thủ tục", "quy trình", "cách thực hiện", "hồ sơ", "cần giấy tờ gì"]):
        return "thủ_tục"

    if any(x in q for x in ["xử phạt", "mức phạt", "vi phạm", "chậm nộp phạt", "tiền phạt"]):
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
    if "quản lý thuế" in q:
        return "quản_lý_thuế"
    if "hóa đơn" in q:
        return "hóa_đơn_chứng_từ"
    if "hộ kinh doanh" in q or "cá nhân kinh doanh" in q:
        return "hộ_kinh_doanh"
    if "tiền phạt" in q or "biên lai" in q:
        return "thu_nộp_tiền_phạt_biên_lai"
    return None


def detect_legal_topic(q: str) -> Optional[str]:
    if "miễn tiền chậm nộp" in q:
        return "mien_tien_cham_nop"

    if "tiền chậm nộp phạt" in q or "chậm nộp phạt" in q:
        return "tien_cham_nop_phat"

    if "hóa đơn điện tử khởi tạo từ máy tính tiền" in q or "máy tính tiền" in q:
        return "hoa_don_may_tinh_tien"

    if "hóa đơn điện tử" in q:
        return "hoa_don_dien_tu"

    if "hộ kinh doanh" in q or "cá nhân kinh doanh" in q:
        return "ho_kinh_doanh"

    if "đăng ký thuế" in q:
        return "dang_ky_thue"

    if "quản lý thuế quốc tế" in q:
        return "quan_ly_thue_quoc_te"

    if "khai thuế" in q or "nộp thuế" in q:
        return "khai_nop_thue"

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
    doc_info = detect_document(q_norm)

    return QueryInfo(
        raw_question=q,
        cau_hoi_chuan_hoa=q_norm,
        dieu=dieu,
        khoan=khoan,
        diem=diem,
        chuong=chuong,
        y_dinh=detect_intent(q_norm),
        ma_van_ban=doc_info.get("ma_van_ban"),
        ten_van_ban=doc_info.get("ten_van_ban"),
        loai_van_ban=doc_info.get("loai_van_ban") or detect_document_type(q_norm),
        cum_tu_chinh_xac=phrases,
        chu_de=detect_topic(q_norm),
        legal_topic=detect_legal_topic(q_norm),
    )