from application.retrieval.query_analyzer import analyze_query

q = "Khoản 2 Điều 5 quy định gì về miễn tiền chậm nộp?"
info = analyze_query(q)
print(info)