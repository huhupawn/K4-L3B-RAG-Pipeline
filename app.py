import os
import sys
import time
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv

# Load biến môi trường
load_dotenv()

# Đường dẫn gốc project
ROOT_DIR = Path(__file__).parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="Trợ lý Pháp lý Hộ Kinh Doanh | RAG Pipeline",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS cho giao diện TÔNG SÁNG (Light Theme) phong cách Modern Indigo & Lavender + Phông Poppins
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

    /* Áp dụng phông chữ Poppins cho các phần tử văn bản (KHÔNG đè font icon) */
    html, body, p, h1, h2, h3, h4, h5, h6, .stMarkdown, .main-header, .sub-header, button, input, textarea {
        font-family: 'Poppins', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* Sửa triệt để lỗi icon Streamlit bị biến thành chữ .arrow_right */
    [data-testid="stIconMaterial"], [class*="material-symbols"], [class*="material-icons"], [data-testid="stExpanderToggleIcon"] {
        font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important;
    }

    /* Main Header with Gradient Indigo/Lavender */
    .main-header {
        font-size: 2.25rem;
        font-weight: 800;
        background: linear-gradient(135deg, #3730A3 0%, #4F46E5 50%, #7C3AED 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.35rem;
        letter-spacing: -0.02em;
    }

    .sub-header {
        font-size: 0.98rem;
        color: #475569;
        margin-bottom: 1.5rem;
        line-height: 1.6;
    }
    .sub-header b {
        color: #4338CA;
    }

    /* Sidebar Tông Sáng: Nền trắng tinh tế, đường viền mềm, chữ rõ ràng */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0;
    }
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label {
        color: #1E293B !important;
    }

    /* Modern Soft Badges (Tông sáng Pastel) */
    .badge-pill {
        display: inline-flex;
        align-items: center;
        padding: 0.25rem 0.65rem;
        font-size: 0.76rem;
        font-weight: 600;
        border-radius: 9999px;
        margin-right: 0.4rem;
        margin-bottom: 0.25rem;
    }
    .badge-hybrid { background-color: #EEF2FF; color: #4338CA; border: 1px solid #C7D2FE; }
    .badge-dense { background-color: #F5F3FF; color: #6D28D9; border: 1px solid #DDD6FE; }
    .badge-bm25 { background-color: #FFF1F2; color: #BE123C; border: 1px solid #FECDD3; }
    .badge-pageindex { background-color: #FAF5FF; color: #7E22CE; border: 1px solid #F3E8FF; }
    .badge-legal { background-color: #EDE9FE; color: #5B21B6; border: 1px solid #DDD6FE; }
    .badge-news { background-color: #ECFDF5; color: #047857; border: 1px solid #A7F3D0; }
    .badge-score { background-color: #FDF2F8; color: #BE185D; border: 1px solid #FBCFE8; }

    /* Source Card Styling (Tông sáng thanh lịch) */
    .source-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 0.95rem;
        margin-bottom: 0.85rem;
        border-left: 4px solid #6366F1;
        box-shadow: 0 2px 8px rgba(99, 102, 241, 0.06);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .source-card:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.12);
        border-color: #A5B4FC;
    }
    .source-title {
        font-weight: 700;
        color: #1E293B;
        font-size: 0.96rem;
        margin-bottom: 0.35rem;
    }
    .source-snippet {
        font-size: 0.86rem;
        color: #334155;
        background-color: #F8FAFC;
        padding: 0.65rem 0.8rem;
        border-radius: 6px;
        border: 1px solid #F1F5F9;
        margin-top: 0.5rem;
        line-height: 1.55;
    }

    /* Nút bấm câu hỏi nhanh (Quick Prompts) Tông Sáng */
    div.stButton > button {
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        background-color: #FFFFFF;
        color: #334155;
        font-family: 'Poppins', sans-serif !important;
        font-weight: 500;
        font-size: 0.86rem;
        padding: 0.55rem 0.85rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        border-color: #818CF8;
        background-color: #EEF2FF;
        color: #312E81;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.14);
        transform: translateY(-1px);
    }

    /* Link liên kết */
    a {
        color: #4F46E5 !important;
        text-decoration: none;
    }
    a:hover {
        color: #3730A3 !important;
        text-decoration: underline;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================
# MOCK GENERATOR (Dành cho việc test UI khi đồng đội chưa xong data)
# ==========================================
MOCK_DATABASE = [
    {
        "keywords": ["shopee", "tiktok", "thương mại điện tử", "tmđt", "100 triệu", "sàn"],
        "answer": (
            "Căn cứ theo quy định tại **Thông tư 40/2021/TT-BTC** và **Nghị định 52/2013/NĐ-CP** (sửa đổi, bổ sung bởi Nghị định 85/2021/NĐ-CP):\n\n"
            "1. **Ngưỡng doanh thu chịu thuế**: Hộ kinh doanh, cá nhân kinh doanh trên các sàn thương mại điện tử (Shopee, TikTok Shop, Lazada...) có doanh thu trong năm dương lịch **trên 100 triệu đồng** thì bắt buộc phải nộp thuế [1]. Nếu doanh thu từ 100 triệu đồng/năm trở xuống thì thuộc đối tượng **miễn thuế GTGT và thuế TNCN** [1].\n\n"
            "2. **Các loại thuế và tỷ lệ nộp (đối với ngành phân phối, bán lẻ hàng hóa)**:\n"
            "   - **Thuế Giá trị gia tăng (GTGT)**: `1%` trên tổng doanh thu [2].\n"
            "   - **Thuế Thu nhập cá nhân (TNCN)**: `0.5%` trên tổng doanh thu [2].\n"
            "   - **Lệ phí môn bài**: Mức nộp từ `300.000đ` đến `1.000.000đ/năm` căn cứ theo bậc doanh thu thực tế hàng năm [1].\n\n"
            "3. **Trách nhiệm của sàn TMĐT**: Các sàn thương mại điện tử có trách nhiệm cung cấp thông tin giao dịch và thực hiện khấu trừ, nộp thuế thay cho cá nhân kinh doanh theo lộ trình hướng dẫn của cơ quan thuế [3]."
        ),
        "sources": [
            {
                "id": "tt40_d4_c1",
                "content": "Điều 4: Nguyên tắc tính thuế đối với hộ kinh doanh, cá nhân kinh doanh. Hộ kinh doanh, cá nhân kinh doanh có doanh thu từ hoạt động sản xuất, kinh doanh trong năm dương lịch từ 100 triệu đồng trở xuống thì thuộc trường hợp không phải nộp thuế GTGT và không phải nộp thuế TNCN theo quy định pháp luật về thuế GTGT và thuế TNCN.",
                "score": 0.92,
                "metadata": {
                    "title": "Thông tư 40/2021/TT-BTC - Hướng dẫn thuế GTGT, TNCN hộ kinh doanh",
                    "source": "legal/thong_tu_40_2021_TT_BTC.pdf",
                    "doc_type": "legal",
                    "url": "https://thuvienphapluat.vn/van-ban/Thue-Phi-Le-Phi/Thong-tu-40-2021-TT-BTC-huong-dan-thue-gia-tri-gia-tang-thu-nhap-ca-nhan-ho-kinh-doanh-476632.aspx",
                    "chunk_index": 4,
                },
                "retrieval_method": "hybrid",
            },
            {
                "id": "tt40_phuluc1_c2",
                "content": "Phụ lục 01: Danh mục ngành nghề tính thuế GTGT, thuế TNCN theo tỷ lệ % trên doanh thu. Hoạt động phân phối, cung cấp hàng hóa: Tỷ lệ % thuế GTGT tính trên doanh thu là 1%; Tỷ lệ % thuế TNCN tính trên doanh thu là 0.5%.",
                "score": 0.88,
                "metadata": {
                    "title": "Phụ lục 01 ban hành kèm Thông tư 40/2021/TT-BTC",
                    "source": "legal/thong_tu_40_phu_luc_01.pdf",
                    "doc_type": "legal",
                    "url": "https://thuvienphapluat.vn/van-ban/Thue-Phi-Le-Phi/Thong-tu-40-2021-TT-BTC-huong-dan-thue-gia-tri-gia-tang-thu-nhap-ca-nhan-ho-kinh-doanh-476632.aspx",
                    "chunk_index": 12,
                },
                "retrieval_method": "hybrid",
            },
            {
                "id": "news_tmdt_shopee_01",
                "content": "Hướng dẫn kê khai thuế cho nhà bán hàng trên sàn TMĐT: Theo quy định mới nhất, các sàn như Shopee, TikTok Shop phối hợp cung cấp dữ liệu định danh và dòng tiền của shop về cổng Tổng cục Thuế để đối soát dữ liệu kê khai thuế định kỳ.",
                "score": 0.81,
                "metadata": {
                    "title": "Hướng dẫn nghĩa vụ thuế cho chủ shop online trên sàn TMĐT",
                    "source": "news/huong_dan_thue_san_tmdt.json",
                    "doc_type": "news",
                    "url": "https://tapchithue.com.vn/nghia-vu-thue-tmdt",
                    "chunk_index": 2,
                },
                "retrieval_method": "hybrid",
            },
        ],
    },
    {
        "keywords": ["đăng ký", "hồ sơ", "thủ tục", "ubnd", "hộ kinh doanh cá thể", "quận", "huyện"],
        "answer": (
            "Căn cứ theo **Điều 87 Nghị định 01/2021/NĐ-CP** về đăng ký doanh nghiệp, thủ tục đăng ký thành lập hộ kinh doanh cá thể được thực hiện như sau:\n\n"
            "1. **Cơ quan tiếp nhận**: Cơ quan đăng ký kinh doanh cấp huyện thuộc **Ủy ban nhân dân cấp huyện** (quận, thị xã, thành phố thuộc tỉnh) nơi hộ kinh doanh đặt địa điểm hoạt động [1].\n\n"
            "2. **Hồ sơ hợp lệ bao gồm**:\n"
            "   - Giấy đề nghị đăng ký hộ kinh doanh (theo mẫu quy định) [1].\n"
            "   - Bản sao Căn cước công dân / Hộ chiếu hợp lệ của chủ hộ kinh doanh hoặc các thành viên hộ gia đình tham gia góp vốn [1].\n"
            "   - Bản sao biên bản họp thành viên hộ gia đình về việc thành lập hộ kinh doanh (áp dụng nếu do các thành viên hộ gia đình cùng thành lập) [2].\n"
            "   - Văn bản ủy quyền của các thành viên cho 1 người làm chủ hộ kinh doanh (nếu có) [2].\n\n"
            "3. **Thời hạn giải quyết**: Trong thời hạn **03 ngày làm việc** kể từ ngày nhận đủ hồ sơ hợp lệ, cơ quan ĐKKD cấp huyện sẽ cấp Giấy chứng nhận đăng ký hộ kinh doanh [1]."
        ),
        "sources": [
            {
                "id": "nd01_d87_c1",
                "content": "Điều 87: Đăng ký hộ kinh doanh. Hộ kinh doanh nộp 01 bộ hồ sơ tại Cơ quan đăng ký kinh doanh cấp huyện nơi đặt địa điểm kinh doanh. Hồ sơ gồm: Giấy đề nghị đăng ký hộ kinh doanh; Bản sao biên bản họp hộ gia đình; Bản sao CCCD của chủ hộ và các thành viên...",
                "score": 0.94,
                "metadata": {
                    "title": "Nghị định 01/2021/NĐ-CP về Đăng ký doanh nghiệp",
                    "source": "legal/nghi_dinh_01_2021_ND_CP.pdf",
                    "doc_type": "legal",
                    "url": "https://thuvienphapluat.vn/van-ban/Doanh-nghiep/Nghi-dinh-01-2021-ND-CP-dang-ky-doanh-nghiep-457388.aspx",
                    "chunk_index": 18,
                },
                "retrieval_method": "hybrid",
            },
            {
                "id": "nd01_d87_c2",
                "content": "Cơ quan đăng ký kinh doanh cấp huyện trao Giấy biên nhận và cấp Giấy chứng nhận đăng ký hộ kinh doanh cho hộ kinh doanh trong thời hạn 03 ngày làm việc kể từ ngày nhận hồ sơ nếu đủ điều kiện.",
                "score": 0.89,
                "metadata": {
                    "title": "Nghị định 01/2021/NĐ-CP về Đăng ký doanh nghiệp",
                    "source": "legal/nghi_dinh_01_2021_ND_CP.pdf",
                    "doc_type": "legal",
                    "url": "https://thuvienphapluat.vn/van-ban/Doanh-nghiep/Nghi-dinh-01-2021-ND-CP-dang-ky-doanh-nghiep-457388.aspx",
                    "chunk_index": 19,
                },
                "retrieval_method": "hybrid",
            },
        ],
    },
    {
        "keywords": ["hóa đơn", "điện tử", "máy tính tiền", "khoán", "kê khai"],
        "answer": (
            "Căn cứ theo **Nghị định 123/2020/NĐ-CP** và **Thông tư 78/2021/TT-BTC** về hóa đơn, chứng từ:\n\n"
            "1. **Hộ kinh doanh theo phương pháp kê khai**: Bắt buộc phải sử dụng hóa đơn điện tử có mã của cơ quan thuế khi bán hàng hóa, cung cấp dịch vụ [1].\n\n"
            "2. **Hộ kinh doanh nộp thuế theo phương pháp khoán**:\n"
            "   - Không bắt buộc phải xuất hóa đơn điện tử cho từng lần bán hàng thông thường [1].\n"
            "   - Trong trường hợp khách hàng có nhu cầu lấy hóa đơn, hộ kinh doanh lập hồ sơ đề nghị cơ quan thuế cấp hóa đơn điện tử có mã theo từng lần phát sinh [2].\n\n"
            "3. **Hóa đơn điện tử khởi tạo từ máy tính tiền**: Áp dụng bắt buộc đối với các hộ kinh doanh nộp thuế theo phương pháp kê khai trong các ngành nghề bán hàng trực tiếp đến người tiêu dùng như: nhà hàng, quán ăn, khách sạn, bán lẻ tân dược, bán lẻ hàng hóa tiêu dùng, trung tâm thương mại... có kết nối dữ liệu trực tiếp với cơ quan thuế [1]."
        ),
        "sources": [
            {
                "id": "nd123_d11_c1",
                "content": "Nghị định 123/2020/NĐ-CP Điều 11: Áp dụng hóa đơn điện tử khi bán hàng hóa, cung ứng dịch vụ. Hộ kinh doanh, cá nhân kinh doanh nộp thuế theo phương pháp kê khai phải sử dụng hóa đơn điện tử có mã của cơ quan thuế...",
                "score": 0.90,
                "metadata": {
                    "title": "Nghị định 123/2020/NĐ-CP về Hóa đơn, Chứng từ",
                    "source": "legal/nghi_dinh_123_2020_ND_CP.pdf",
                    "doc_type": "legal",
                    "url": "https://thuvienphapluat.vn/van-ban/Thue-Phi-Le-Phi/Nghi-dinh-123-2020-ND-CP-hoa-don-chung-tu-454558.aspx",
                    "chunk_index": 8,
                },
                "retrieval_method": "hybrid",
            },
            {
                "id": "tt78_d8_c2",
                "content": "Thông tư 78/2021/TT-BTC Điều 8: Hóa đơn điện tử có mã của cơ quan thuế được khởi tạo từ máy tính tiền có kết nối chuyển dữ liệu điện tử với cơ quan thuế áp dụng cho hộ kinh doanh bán lẻ, dịch vụ ăn uống...",
                "score": 0.86,
                "metadata": {
                    "title": "Thông tư 78/2021/TT-BTC Hướng dẫn Nghị định 123/2020/NĐ-CP",
                    "source": "legal/thong_tu_78_2021_TT_BTC.pdf",
                    "doc_type": "legal",
                    "url": "https://thuvienphapluat.vn/van-ban/Thue-Phi-Le-Phi/Thong-tu-78-2021-TT-BTC-huong-dan-thuc-hien-Nghi-dinh-123-2020-ND-CP-hoa-don-chung-tu-489063.aspx",
                    "chunk_index": 14,
                },
                "retrieval_method": "hybrid",
            },
        ],
    },
]


def mock_generate_with_citation(query: str, top_k: int = 5) -> dict:
    """Tạo câu trả lời giả lập chính xác về pháp luật hộ kinh doanh khi test UI."""
    time.sleep(0.6)  # Mô phỏng độ trễ gọi pipeline
    query_lower = query.lower()

    # Kiểm tra truy vấn out-of-domain để kiểm thử Safe Refusal
    out_of_domain_words = ["thời tiết", "bóng đá", "tổng thống", "ca sĩ", "nấu ăn", "phim"]
    if any(w in query_lower for w in out_of_domain_words):
        return {
            "answer": "Rất tiếc, tôi không tìm thấy căn cứ pháp lý hoặc bài viết hướng dẫn phù hợp trong cơ sở dữ liệu chuyên ngành hộ kinh doanh để trả lời câu hỏi này. Hệ thống được chuyên biệt hóa cho các quy định về đăng ký kinh doanh, thuế, hóa đơn và thương mại điện tử.",
            "sources": [],
            "retrieval_source": "none",
        }

    # Đối chiếu từ khóa mẫu trong mock database
    for entry in MOCK_DATABASE:
        if any(keyword in query_lower for keyword in entry["keywords"]):
            return {
                "answer": entry["answer"],
                "sources": entry["sources"][:top_k],
                "retrieval_source": "hybrid",
            }

    # Trả về câu trả lời mặc định đúng format
    default_sources = MOCK_DATABASE[0]["sources"][:top_k]
    return {
        "answer": (
            f"Về câu hỏi **'{query}'**, theo các quy định pháp luật hiện hành đối với hộ kinh doanh:\n\n"
            "- Các hoạt động sản xuất, kinh doanh phải được đăng ký và tuân thủ các quy định tại Nghị định 01/2021/NĐ-CP [1].\n"
            "- Nghĩa vụ về thuế GTGT, TNCN thực hiện theo Thông tư 40/2021/TT-BTC dựa trên doanh thu thực tế [2].\n"
            "- Đề nghị người nộp thuế liên hệ Đội thuế liên xã, phường hoặc Chi cục Thuế quản lý trực tiếp để được hướng dẫn chi tiết."
        ),
        "sources": default_sources,
        "retrieval_source": "hybrid",
    }


def query_rag_pipeline(query: str, top_k: int, mode_preference: str) -> dict:
    """
    Gọi pipeline thật nếu khả dụng (src.task10_generation);
    tự động fallback sang mock nếu đồng đội chưa build xong database.
    """
    if mode_preference == "mock":
        return mock_generate_with_citation(query, top_k=top_k)

    try:
        from src.task10_generation import generate_with_citation

        result = generate_with_citation(query, top_k=top_k)
        if isinstance(result, dict) and "answer" in result:
            return result
    except (ImportError, NotImplementedError, Exception) as e:
        if mode_preference == "real":
            return {
                "answer": f"⚠️ Pipeline thực tế chưa hoàn thiện hoặc chưa có dữ liệu: {e}. Vui lòng chuyển sang 'Chế độ Demo Mock' ở sidebar để kiểm thử giao diện.",
                "sources": [],
                "retrieval_source": "none",
            }

    # Mặc định auto-fallback sang mock
    return mock_generate_with_citation(query, top_k=top_k)


# ==========================================
# KHỞI TẠO SESSION STATE
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "quick_prompt" not in st.session_state:
    st.session_state.quick_prompt = None


# ==========================================
# SIDEBAR: CẤU HÌNH & THÔNG TIN DỰ ÁN
# ==========================================
with st.sidebar:
    st.markdown("### ⚖️ Trợ Lý Pháp Lý HKD")
    st.caption("VinUni AI20k • K4 - L3B RAG Pipeline")

    st.markdown("---")
    st.markdown("#### ⚙️ Cấu hình Retrieval")

    retrieval_strategy = st.selectbox(
        "Chiến lược truy xuất:",
        ["Hybrid (Dense + BM25 + RRF)", "Dense only (ChromaDB)", "Lexical only (BM25)"],
        index=0,
        help="Chọn chiến lược truy xuất văn bản để đánh giá hoặc so sánh A/B",
    )

    top_k = st.slider(
        "Số lượng chunks trích xuất (top_k):",
        min_value=1,
        max_value=10,
        value=5,
        step=1,
        help="Số lượng đoạn văn bản tối đa gửi vào LLM",
    )

    score_threshold = st.slider(
        "Ngưỡng tin cậy (Cosine threshold):",
        min_value=0.1,
        max_value=0.9,
        value=0.3,
        step=0.05,
        help="Nếu điểm tương đồng dưới ngưỡng này, hệ thống kích hoạt fallback",
    )

    st.markdown("---")
    st.markdown("#### 🔌 Nguồn dữ liệu & Backend")
    backend_mode = st.radio(
        "Chế độ chạy:",
        ["Tự động (Ưu tiên Real Pipeline, fallback Mock)", "Chế độ Demo Mock", "Chế độ Real Pipeline"],
        index=0,
    )
    mode_code = "auto"
    if "Demo Mock" in backend_mode:
        mode_code = "mock"
    elif "Real Pipeline" in backend_mode:
        mode_code = "real"

    st.markdown("---")
    st.markdown("#### 📚 Cơ sở tri thức nhóm")
    with st.expander("Xem danh mục tài liệu nạp vào DB", expanded=False):
        st.markdown(
            """
            **1. Văn bản Pháp lý (`legal`):**
            - 📜 *Nghị định 01/2021/NĐ-CP* (Đăng ký doanh nghiệp, Hộ KD)
            - 📜 *Thông tư 40/2021/TT-BTC* (Thuế GTGT, TNCN hộ kinh doanh)
            - 📜 *Nghị định 123/2020/NĐ-CP* (Hóa đơn điện tử, chứng từ)

            **2. Hướng dẫn & Tin tức (`news`):**
            - 📰 *Nghĩa vụ thuế khi bán hàng Shopee, TikTok Shop*
            - 📰 *Quy định hóa đơn điện tử khởi tạo từ máy tính tiền*
            - 📰 *Hướng dẫn thủ tục kê khai thuế khoán online*
            """
        )

    if st.button("🗑️ Xóa lịch sử chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.quick_prompt = None
        st.rerun()


# ==========================================
# GIAO DIỆN CHÍNH (MAIN VIEW)
# ==========================================
st.markdown('<div class="main-header">⚖️ Trợ Lý Pháp Lý Hộ Kinh Doanh</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Tư vấn thông minh về <b>Đăng ký kinh doanh</b>, <b>Thuế hộ kinh doanh</b>, <b>Hóa đơn điện tử</b> và <b>Thương mại điện tử (Shopee, TikTok Shop)</b> dựa trên RAG Pipeline.</div>',
    unsafe_allow_html=True,
)

# Gợi ý câu hỏi nhanh (Quick Prompts)
st.markdown("##### 💡 Gợi ý câu hỏi thường gặp:")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🛒 Bán hàng Shopee >100tr", use_container_width=True):
        st.session_state.quick_prompt = "Bán hàng trên Shopee, TikTok Shop doanh thu trên 100 triệu phải đóng những loại thuế nào và tỷ lệ bao nhiêu?"

with col2:
    if st.button("📝 Thủ tục ĐKKD cấp huyện", use_container_width=True):
        st.session_state.quick_prompt = "Hồ sơ và thủ tục đăng ký hộ kinh doanh cá thể tại UBND cấp huyện cần những giấy tờ gì?"

with col3:
    if st.button("🧾 Hóa đơn máy tính tiền", use_container_width=True):
        st.session_state.quick_prompt = "Hộ kinh doanh theo phương pháp khoán có bắt buộc dùng hóa đơn điện tử khởi tạo từ máy tính tiền không?"

with col4:
    if st.button("❓ Test câu hỏi ngoài lề", use_container_width=True):
        st.session_state.quick_prompt = "Thời tiết hôm nay tại Hà Nội thế nào?"

st.markdown("---")


# ==========================================
# HIỂN THỊ LỊCH SỬ CHAT
# ==========================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        # Nếu là câu trả lời của Bot và có sources, hiển thị trích dẫn nguồn
        if msg["role"] == "assistant" and msg.get("sources"):
            retrieval_method = msg.get("retrieval_source", "hybrid")
            badge_class = f"badge-{retrieval_method}"

            st.markdown(
                f"""
                <div style="margin-top: 0.5rem; margin-bottom: 0.5rem;">
                    <span class="badge-pill {badge_class}">🔍 Nguồn: {retrieval_method.upper()}</span>
                    <span class="badge-pill badge-legal">📚 {len(msg['sources'])} tài liệu tham chiếu</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.expander(f"📎 Xem chi tiết {len(msg['sources'])} căn cứ pháp lý & nguồn trích dẫn", expanded=False):
                for idx, src in enumerate(msg["sources"], 1):
                    meta = src.get("metadata", {})
                    title = meta.get("title", "Tài liệu tham khảo")
                    doc_type = meta.get("doc_type", "legal")
                    doc_type_label = "⚖️ Văn bản Pháp lý" if doc_type == "legal" else "📰 Tin tức/Hướng dẫn"
                    doc_type_class = "badge-legal" if doc_type == "legal" else "badge-news"
                    score = src.get("score", 0.0)
                    url = meta.get("url")

                    st.markdown(
                        f"""
                        <div class="source-card">
                            <div class="source-title">[{idx}] {title}</div>
                            <div>
                                <span class="badge-pill {doc_type_class}">{doc_type_label}</span>
                                <span class="badge-pill badge-score">Độ khớp: {score:.2f}</span>
                                <span class="badge-pill badge-bm25">Chunk #{meta.get('chunk_index', 0)}</span>
                            </div>
                            <div class="source-snippet">{src.get('content', '')}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if url:
                        st.markdown(f"🔗 [Tra cứu toàn văn văn bản gốc]({url})")


# ==========================================
# XỬ LÝ TRUY VẤN MỚI
# ==========================================
query_input = st.chat_input("Nhập câu hỏi pháp lý cho hộ kinh doanh của bạn...")

# Lấy query từ quick prompt nếu có
active_query = None
if query_input:
    active_query = query_input
elif st.session_state.quick_prompt:
    active_query = st.session_state.quick_prompt
    st.session_state.quick_prompt = None

if active_query:
    # 1. Thêm câu hỏi người dùng
    st.session_state.messages.append({"role": "user", "content": active_query})
    with st.chat_message("user"):
        st.markdown(active_query)

    # 2. Xử lý câu trả lời từ RAG Pipeline
    with st.chat_message("assistant"):
        with st.spinner("Đang tra cứu cơ sở dữ liệu pháp luật và tổng hợp câu trả lời..."):
            result = query_rag_pipeline(
                query=active_query,
                top_k=top_k,
                mode_preference=mode_code,
            )

            answer = result.get("answer", "Không thể tạo câu trả lời.")
            sources = result.get("sources", [])
            retrieval_src = result.get("retrieval_source", "hybrid")

            st.markdown(answer)

            # Hiển thị sources
            if sources:
                badge_class = f"badge-{retrieval_src}"
                st.markdown(
                    f"""
                    <div style="margin-top: 0.5rem; margin-bottom: 0.5rem;">
                        <span class="badge-pill {badge_class}">🔍 Nguồn: {retrieval_src.upper()}</span>
                        <span class="badge-pill badge-legal">📚 {len(sources)} tài liệu tham chiếu</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                with st.expander(f"📎 Xem chi tiết {len(sources)} căn cứ pháp lý & nguồn trích dẫn", expanded=False):
                    for idx, src in enumerate(sources, 1):
                        meta = src.get("metadata", {})
                        title = meta.get("title", "Tài liệu tham khảo")
                        doc_type = meta.get("doc_type", "legal")
                        doc_type_label = "⚖️ Văn bản Pháp lý" if doc_type == "legal" else "📰 Tin tức/Hướng dẫn"
                        doc_type_class = "badge-legal" if doc_type == "legal" else "badge-news"
                        score = src.get("score", 0.0)
                        url = meta.get("url")

                        st.markdown(
                            f"""
                            <div class="source-card">
                                <div class="source-title">[{idx}] {title}</div>
                                <div>
                                    <span class="badge-pill {doc_type_class}">{doc_type_label}</span>
                                    <span class="badge-pill badge-score">Độ khớp: {score:.2f}</span>
                                    <span class="badge-pill badge-bm25">Chunk #{meta.get('chunk_index', 0)}</span>
                                </div>
                                <div class="source-snippet">{src.get('content', '')}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        if url:
                            st.markdown(f"🔗 [Tra cứu toàn văn văn bản gốc]({url})")

    # 3. Lưu vào session state
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": sources,
            "retrieval_source": retrieval_src,
        }
    )
    st.rerun()
