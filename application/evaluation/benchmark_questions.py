BENCHMARK_QUESTIONS = [
    # # article_lookup
    # {
    #     "id": "LAW_001",
    #     "question": "Khoản 2 Điều 5 của Luật quản lý thuế quy định những nội dung quản lý thuế nào?",
    #     "expected_document": "Luật quản lý thuế 108/2025/QH15",
    #     "expected_dieu": 5,
    #     "expected_khoan": 2,
    #     "acceptable_dieu": [5],
    #     "acceptable_khoan": [2, ""],
    #     "expected_keywords": ["đăng ký thuế", "khai thuế", "nộp thuế", "hóa đơn"],
    #     "expected_citation": ["Khoản 2 Điều 5"],
    #     "category": "article_lookup",
    # },
    # {
    #     "id": "LAW_002",
    #     "question": "Điều 1 của Luật quản lý thuế quy định phạm vi điều chỉnh như thế nào?",
    #     "expected_document": "Luật quản lý thuế 108/2025/QH15",
    #     "expected_dieu": 1,
    #     "acceptable_dieu": [1],
    #     "expected_keywords": ["quản lý các loại thuế", "ngân sách nhà nước"],
    #     "expected_citation": ["Điều 1"],
    #     "category": "article_lookup",
    # },
    # {
    #     "id": "LAW_003",
    #     "question": "Điều 30 Luật quản lý thuế quy định những nội dung nào về quản lý thuế quốc tế?",
    #     "expected_document": "Luật quản lý thuế 108/2025/QH15",
    #     "expected_dieu": 30,
    #     "acceptable_dieu": [30],
    #     "expected_keywords": ["quản lý thuế quốc tế", "điều ước quốc tế", "thỏa thuận quốc tế"],
    #     "expected_citation": ["Điều 30"],
    #     "category": "article_lookup",
    # },

    # # condition
    # {
    #     "id": "COND_001",
    #     "question": "trường hợp nào được miễn tiền chậm nộp theo Luật quản lý thuế?",
    #     "expected_document": "Luật quản lý thuế 108/2025/QH15",
    #     "expected_dieu": 16,
    #     "expected_khoan": 5,
    #     "acceptable_dieu": [16],
    #     "acceptable_khoan": [5, ""],
    #     "expected_keywords": ["miễn tiền chậm nộp", "bất khả kháng"],
    #     "expected_citation": ["Khoản 5 Điều 16"],
    #     "category": "condition",
    # },
    # {
    #     "id": "COND_002",
    #     "question": "khi nào hộ kinh doanh phát sinh nghĩa vụ khai thuế, nộp thuế theo Nghị định 68?",
    #     "expected_document": "68-2026-ND-CP",
    #     "acceptable_dieu": [8, 9, 10],
    #     "acceptable_khoan": [1, 2, ""],
    #     "expected_keywords": ["01 tỷ đồng", "khai thuế", "nộp thuế"],
    #     "expected_citation": ["Nghị định 68"],
    #     "category": "condition",
    # },
    # {
    #     "id": "COND_003",
    #     "question": "trường hợp nào không tính tiền chậm nộp phạt vi phạm hành chính?",
    #     "expected_document": "Thông tư 18/2023/TT-BTC",
    #     "expected_dieu": 5,
    #     "acceptable_dieu": [5],
    #     "expected_keywords": ["không tính tiền chậm nộp phạt", "hoãn thi hành", "giảm", "miễn"],
    #     "expected_citation": ["Điều 5"],
    #     "category": "condition",
    # },

    # # procedure
    # {
    #     "id": "PROC_001",
    #     "question": "thủ tục đăng ký thuế gồm những nội dung nào theo Luật quản lý thuế?",
    #     "expected_document": "Luật quản lý thuế 108/2025/QH15",
    #     "expected_dieu": 10,
    #     "acceptable_dieu": [10],
    #     "expected_keywords": ["đăng ký thuế lần đầu", "thay đổi thông tin", "chấm dứt hiệu lực mã số thuế"],
    #     "expected_citation": ["Điều 10"],
    #     "category": "procedure",
    # },
    # {
    #     "id": "PROC_002",
    #     "question": "hộ kinh doanh có doanh thu từ 1 tỷ đồng trở xuống phải làm gì với doanh thu thực tế phát sinh?",
    #     "expected_document": "68-2026-ND-CP",
    #     "acceptable_dieu": [8, 9],
    #     "expected_keywords": ["thông báo doanh thu thực tế", "cơ quan thuế", "31 tháng 01"],
    #     "expected_citation": ["Nghị định 68"],
    #     "category": "procedure",
    # },
    # {
    #     "id": "PROC_003",
    #     "question": "thủ tục thu nộp tiền phạt vi phạm hành chính được quy định như thế nào?",
    #     "expected_document": "Thông tư 18/2023/TT-BTC",
    #     "acceptable_dieu": [3, 4, 5],
    #     "expected_keywords": ["thu tiền phạt", "nộp tiền phạt", "ngân sách nhà nước"],
    #     "expected_citation": ["Thông tư 18"],
    #     "category": "procedure",
    # },

    # # invoice
    # {
    #     "id": "INV_001",
    #     "question": "hộ kinh doanh nào phải sử dụng hóa đơn điện tử khởi tạo từ máy tính tiền?",
    #     "expected_document": "70-2025-ND-CP",
    #     "expected_dieu": 11,
    #     "expected_khoan": 1,
    #     "acceptable_dieu": [11],
    #     "acceptable_khoan": [1, ""],
    #     "expected_keywords": ["01 tỷ đồng", "máy tính tiền", "người tiêu dùng"],
    #     "expected_citation": ["Khoản 1 Điều 11"],
    #     "must_not_contain": ["doanh nghiệp có hoạt động"],
    #     "category": "invoice",
    # },
    # {
    #     "id": "INV_002",
    #     "question": "hóa đơn điện tử khởi tạo từ máy tính tiền là gì?",
    #     "expected_document": "70-2025-ND-CP",
    #     "expected_dieu": 11,
    #     "acceptable_dieu": [11],
    #     "expected_keywords": ["hóa đơn điện tử", "máy tính tiền", "chuyển dữ liệu"],
    #     "expected_citation": ["Điều 11"],
    #     "category": "invoice",
    # },
    # {
    #     "id": "INV_003",
    #     "question": "nội dung của hóa đơn điện tử khởi tạo từ máy tính tiền gồm những gì?",
    #     "expected_document": "70-2025-ND-CP",
    #     "expected_dieu": 11,
    #     "acceptable_dieu": [11],
    #     "expected_keywords": ["tên người bán", "mã số thuế", "tên hàng hóa", "dịch vụ"],
    #     "expected_citation": ["Điều 11"],
    #     "category": "invoice",
    # },
    # {
    #     "id": "INV_004",
    #     "question": "người bán sử dụng hóa đơn điện tử có trách nhiệm gì?",
    #     "expected_document": "70-2025-ND-CP",
    #     "acceptable_dieu": [11, 12, 13],
    #     "expected_keywords": ["hóa đơn điện tử", "người bán", "cơ quan thuế"],
    #     "expected_citation": ["Nghị định 70"],
    #     "category": "invoice",
    # },

    # # penalty
    # {
    #     "id": "PEN_001",
    #     "question": "tiền chậm nộp phạt vi phạm hành chính được tính như thế nào?",
    #     "expected_document": "Thông tư 18/2023/TT-BTC",
    #     "expected_dieu": 5,
    #     "expected_khoan": 1,
    #     "acceptable_dieu": [5],
    #     "acceptable_khoan": [1, ""],
    #     "expected_keywords": ["0,05%", "chậm nộp phạt", "ngày chậm nộp"],
    #     "expected_citation": ["Điều 5"],
    #     "category": "penalty",
    # },
    # {
    #     "id": "PEN_002",
    #     "question": "tiền chậm nộp thuế và tiền chậm nộp phạt vi phạm hành chính khác nhau như thế nào?",
    #     "expected_document": None,
    #     "acceptable_dieu": [5, 16],
    #     "expected_keywords": ["tiền chậm nộp", "chậm nộp phạt", "thuế"],
    #     "expected_citation": [],
    #     "category": "penalty",
    # },
    # {
    #     "id": "PEN_003",
    #     "question": "cá nhân tổ chức chậm nộp tiền phạt thì phải nộp thêm bao nhiêu phần trăm mỗi ngày?",
    #     "expected_document": "Thông tư 18/2023/TT-BTC",
    #     "expected_dieu": 5,
    #     "acceptable_dieu": [5],
    #     "expected_keywords": ["0,05%", "mỗi ngày", "tiền phạt chưa nộp"],
    #     "expected_citation": ["Điều 5"],
    #     "category": "penalty",
    # },

    # # anti_hallucination
    # {
    #     "id": "ANTI_001",
    #     "question": "hộ kinh doanh, cá nhân kinh doanh có doanh thu dưới 1 tỷ đồng thì có phải nộp thuế giá trị gia tăng không?",
    #     "expected_document": "68-2026-ND-CP",
    #     "acceptable_dieu": [8, 9, 10],
    #     "acceptable_khoan": [1, 2, ""],
    #     "expected_keywords": ["thông báo doanh thu", "1 tỷ đồng", "khai thuế"],
    #     "expected_citation": ["Nghị định 68"],
    #     "must_contain": ["chưa đủ để kết luận"],
    #     "must_not_contain": ["không phải nộp thuế giá trị gia tăng", "không phải nộp thuế gtgt"],
    #     "category": "anti_hallucination",
    # },
    # {
    #     "id": "ANTI_002",
    #     "question": "nếu context không nói rõ thì có thể kết luận hộ kinh doanh được miễn thuế không?",
    #     "expected_document": None,
    #     "expected_keywords": ["không đủ", "không thể kết luận", "context"],
    #     "must_contain": ["không"],
    #     "must_not_contain": ["được miễn thuế"],
    #     "category": "anti_hallucination",
    # },
    # {
    #     "id": "ANTI_003",
    #     "question": "hộ kinh doanh dưới 1 tỷ có chắc chắn không cần dùng hóa đơn điện tử không?",
    #     "expected_document": "70-2025-ND-CP",
    #     "acceptable_dieu": [11],
    #     "expected_keywords": ["hóa đơn điện tử", "01 tỷ đồng", "máy tính tiền"],
    #     "must_not_contain": ["chắc chắn không cần dùng hóa đơn điện tử"],
    #     "category": "anti_hallucination",
    # },

    # # cross_document
    # {
    #     "id": "CROSS_001",
    #     "question": "Luật quản lý thuế và Nghị định 68 quy định thế nào về khai thuế, nộp thuế của hộ kinh doanh?",
    #     "expected_document": None,
    #     "expected_keywords": ["Luật quản lý thuế", "Nghị định 68", "khai thuế", "nộp thuế"],
    #     "expected_citation": ["Nghị định 68"],
    #     "category": "cross_document",
    # },
    # {
    #     "id": "CROSS_002",
    #     "question": "hộ kinh doanh có cần dùng hóa đơn điện tử không theo Nghị định 68 và Nghị định 70?",
    #     "expected_document": None,
    #     "expected_keywords": ["Nghị định 68", "Nghị định 70", "hóa đơn điện tử"],
    #     "expected_citation": ["Nghị định"],
    #     "category": "cross_document",
    # },
    # {
    #     "id": "CROSS_003",
    #     "question": "khi hộ kinh doanh chậm nộp thuế hoặc chậm nộp phạt thì cần xem những văn bản nào?",
    #     "expected_document": None,
    #     "expected_keywords": ["Luật quản lý thuế", "Thông tư 18", "chậm nộp"],
    #     "expected_citation": [],
    #     "category": "cross_document",
    # },

    # # missing_context
    # {
    #     "id": "MISS_001",
    #     "question": "khoản 21 Điều 4 của Luật quản lý thuế định nghĩa bất khả kháng như thế nào?",
    #     "expected_document": "Luật quản lý thuế 108/2025/QH15",
    #     "acceptable_dieu": [4],
    #     "expected_keywords": ["bất khả kháng"],
    #     "must_contain": ["không đủ", "context"],
    #     "category": "missing_context",
    # },
    # {
    #     "id": "MISS_002",
    #     "question": "Nghị định 68 có quy định cách tính thuế cho từng ngành nghề cụ thể không?",
    #     "expected_document": "68-2026-ND-CP",
    #     "expected_keywords": ["không đủ", "context"],
    #     "must_contain": ["không đủ"],
    #     "category": "missing_context",
    # },
    # {
    #     "id": "MISS_003",
    #     "question": "hộ kinh doanh có được hoàn thuế giá trị gia tăng trong mọi trường hợp không?",
    #     "expected_document": None,
    #     "expected_keywords": ["không đủ", "không thể kết luận"],
    #     "must_not_contain": ["được hoàn thuế trong mọi trường hợp"],
    #     "category": "missing_context",
    # },

    # # terminology fidelity
    # {
    #     "id": "TERM_001",
    #     "question": "không phải khai thuế có đồng nghĩa với không phải nộp thuế không?",
    #     "expected_document": None,
    #     "expected_keywords": ["không đồng nghĩa", "khai thuế", "nộp thuế"],
    #     "must_not_contain": ["đồng nghĩa"],
    #     "category": "terminology",
    # },
    # {
    #     "id": "TERM_002",
    #     "question": "miễn tiền chậm nộp có đồng nghĩa với miễn nghĩa vụ thuế không?",
    #     "expected_document": "Luật quản lý thuế 108/2025/QH15",
    #     "expected_keywords": ["không đồng nghĩa", "miễn tiền chậm nộp", "nghĩa vụ thuế"],
    #     "must_not_contain": ["đồng nghĩa"],
    #     "category": "terminology",
    # },
    # {
    #     "id": "TERM_003",
    #     "question": "tiền chậm nộp thuế có giống tiền chậm nộp phạt vi phạm hành chính không?",
    #     "expected_document": None,
    #     "expected_keywords": ["khác", "tiền chậm nộp thuế", "tiền chậm nộp phạt"],
    #     "category": "terminology",
    # },
    # {
    #     "id": "VAT_001",
    #     "question": "Đối tượng chịu thuế giá trị gia tăng là gì?",
    #     "expected_document": "Luật Thuế giá trị gia tăng 48/2024/QH15",
    #     "acceptable_dieu": [4],
    #     "expected_keywords": [
    #         "hàng hóa",
    #         "dịch vụ",
    #         "sản xuất",
    #         "kinh doanh"
    #     ],
    #     "category": "vat",
    # },
    # {
    #     "id": "VAT_002",
    #     "question": "Ai là người nộp thuế giá trị gia tăng?",
    #     "expected_document": "Luật Thuế giá trị gia tăng 48/2024/QH15",
    #     "acceptable_dieu": [5],
    #     "expected_keywords": [
    #         "người nộp thuế",
    #         "tổ chức",
    #         "cá nhân"
    #     ],
    #     "category": "vat",
    # },
    # {
    #     "id": "VAT_003",
    #     "question": "Các đối tượng không chịu thuế GTGT được quy định ở đâu?",
    #     "expected_document": "Luật Thuế giá trị gia tăng 48/2024/QH15",
    #     "acceptable_dieu": [5, 6, 7],
    #     "expected_keywords": [
    #         "không chịu thuế"
    #     ],
    #     "category": "vat",
    # },
    # {
    #     "id": "VAT_004",
    #     "question": "Hoàn thuế giá trị gia tăng được áp dụng trong những trường hợp nào?",
    #     "expected_document": "Luật Thuế giá trị gia tăng 48/2024/QH15",
    #     "expected_keywords": [
    #         "hoàn thuế"
    #     ],
    #     "category": "vat",
    # },
    # {
    #     "id": "PIT_001",
    #     "question": "Ai là người nộp thuế thu nhập cá nhân?",
    #     "expected_document": "Luật Thuế thu nhập cá nhân 109/2025/QH15",
    #     "expected_keywords": [
    #         "cá nhân cư trú",
    #         "cá nhân không cư trú"
    #     ],
    #     "category": "pit",
    # },
    # {
    #     "id": "PIT_002",
    #     "question": "Thu nhập từ hoạt động kinh doanh có thuộc thu nhập chịu thuế không?",
    #     "expected_document": "Luật Thuế thu nhập cá nhân 109/2025/QH15",
    #     "expected_keywords": [
    #         "thu nhập từ kinh doanh"
    #     ],
    #     "category": "pit",
    # },
    # {
    #     "id": "PIT_003",
    #     "question": "Các loại thu nhập chịu thuế thu nhập cá nhân bao gồm những gì?",
    #     "expected_document": "Luật Thuế thu nhập cá nhân 109/2025/QH15",
    #     "expected_keywords": [
    #         "thu nhập chịu thuế"
    #     ],
    #     "category": "pit",
    # },
    {
        "id": "NR198_001",
        "question": "Nghị quyết 198 quy định gì về hộ kinh doanh?",
        "expected_document": "Nghị quyết 198/2025/QH15",
        "expected_keywords": [
            "hộ kinh doanh"
        ],
        "category": "resolution",
    },
    {
        "id": "NR198_002",
        "question": "Nghị quyết 198 có định hướng gì đối với thuế khoán?",
        "expected_document": "Nghị quyết 198/2025/QH15",
        "expected_keywords": [
            "thuế khoán"
        ],
        "category": "resolution",
    },
    {
        "id": "NR198_003",
        "question": "Nghị quyết 198 có quy định gì về lệ phí môn bài?",
        "expected_document": "Nghị quyết 198/2025/QH15",
        "expected_keywords": [
            "lệ phí môn bài"
        ],
        "category": "resolution",
    },
    {
        "id": "CROSS_004",
        "question": "Doanh thu dưới 1 tỷ đồng thì nghĩa vụ thuế của hộ kinh doanh được quy định ở những văn bản nào?",
        "expected_keywords": [
            "Nghị định 68",
            "Nghị định 141"
        ],
        "category": "cross_document",
    },
    {
        "id": "CROSS_005",
        "question": "Hộ kinh doanh sử dụng hóa đơn điện tử cần tham khảo những văn bản nào?",
        "expected_keywords": [
            "Nghị định 70",
            "Thông tư 32"
        ],
        "category": "cross_document",
    },
    {
        "id": "CROSS_006",
        "question": "Khi chậm nộp thuế hoặc chậm nộp tiền phạt thì cần tham khảo những văn bản nào?",
        "expected_keywords": [
            "Luật quản lý thuế",
            "Thông tư 18"
        ],
        "category": "cross_document",
    },
]