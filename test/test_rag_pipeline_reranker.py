from application.pipelines.rag_pipeline import RAGPipeline


def main():
    pipeline = RAGPipeline()

    questions = [
        # 1. Luật quản lý thuế 108/2025/QH15
        # "cho mình biết nội dung Điều 1 của Luật quản lý thuế",
        "Khoản 2 Điều 5 của Luật quản lý thuế quy định những nội dung quản lý thuế nào?",
        # "trường hợp nào được miễn tiền chậm nộp theo Luật quản lý thuế?",
        # "thủ tục đăng ký thuế gồm những nội dung nào theo Điều 10 Luật quản lý thuế?",
        # "quản lý thuế quốc tế gồm những nội dung nào theo Điều 30 Luật quản lý thuế?",

        # # 2. Nghị định 68/2026/NĐ-CP — hộ/cá nhân kinh doanh
        # "Nghị định 68/2026/NĐ-CP áp dụng cho những đối tượng nào?",
        "hộ kinh doanh, cá nhân kinh doanh có doanh thu dưới 500 triệu đồng thì có phải nộp thuế giá trị gia tăng không?",
        # "hộ kinh doanh, cá nhân kinh doanh có doanh thu dưới 500 triệu đồng thì có phải nộp thuế thu nhập cá nhân không?",
        # "doanh thu để xác định thuế thu nhập cá nhân của hộ kinh doanh được xác định như thế nào?",
        # "hộ kinh doanh khai thuế, tính thuế và nộp thuế theo nguyên tắc nào?",

        # # 3. Nghị định 70/2025/NĐ-CP — hóa đơn điện tử
        # "hóa đơn điện tử khởi tạo từ máy tính tiền là gì?",
        "hộ kinh doanh nào phải sử dụng hóa đơn điện tử khởi tạo từ máy tính tiền?",
        # "nội dung của hóa đơn điện tử khởi tạo từ máy tính tiền gồm những gì?",
        # "người bán hàng hóa, cung cấp dịch vụ sử dụng hóa đơn điện tử có trách nhiệm gì?",
        # "trường hợp nào bị ngừng sử dụng hóa đơn điện tử?",

        # # 4. Thông tư 18/2023/TT-BTC — tiền phạt, tiền chậm nộp phạt
        # "Thông tư 18/2023/TT-BTC điều chỉnh những nội dung nào?",
        # "đối tượng áp dụng của Thông tư 18/2023/TT-BTC gồm những ai?",
        # "thủ tục thu, nộp tiền phạt vi phạm hành chính được thực hiện như thế nào?",
        # "tiền chậm nộp phạt vi phạm hành chính được tính như thế nào?",
        # "trường hợp nào không tính tiền chậm nộp phạt vi phạm hành chính?",

        # # 5. Cross-document reasoning
        # "Luật quản lý thuế và Nghị định 68/2026/NĐ-CP quy định thế nào về hộ kinh doanh, cá nhân kinh doanh?",
        # "hộ kinh doanh có cần sử dụng hóa đơn điện tử không, căn cứ theo Nghị định 68/2026/NĐ-CP và Nghị định 70/2025/NĐ-CP?",
        # "nghĩa vụ khai thuế của hộ kinh doanh được quy định trong Luật quản lý thuế và Nghị định 68/2026/NĐ-CP như thế nào?",
        # "sự khác nhau giữa tiền chậm nộp thuế và tiền chậm nộp phạt vi phạm hành chính là gì?",
        # "khi hộ kinh doanh chậm nộp thuế hoặc chậm nộp phạt thì cần xem những văn bản nào?",
    ]

    for q in questions:
        print("\n" + "=" * 100)
        print("QUESTION:", q)

        result = pipeline.ask(q)

        print("\nANSWER:")
        print(result["answer"])

        print("\nSOURCES:")
        for s in result["sources"]:
            print({
                "source": s.get("retrieval_source"),
                "score": s.get("score"),
                "document": s.get("ten_van_ban"),
                "dieu": s.get("dieu"),
                "khoan": s.get("khoan"),
                "diem": s.get("diem"),
                "title": s.get("tieu_de_dieu"),
            })


if __name__ == "__main__":
    main()