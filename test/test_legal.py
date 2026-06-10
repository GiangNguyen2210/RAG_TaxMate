from application.retrieval.query_analyzer import analyze_query

queries = [
    "hộ kinh doanh dưới 1 tỷ có phải nộp thuế không",
    "doanh thu dưới 1 tỷ đồng",
    "ngưỡng doanh thu chịu thuế",
    "ngưỡng doanh thu hóa đơn điện tử",
]

for q in queries:
    print("=" * 80)
    print(q)
    print(analyze_query(q))