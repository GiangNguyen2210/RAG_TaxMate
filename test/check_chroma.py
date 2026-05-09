import chromadb

CHROMA_PATH = "./chroma_db"  # sửa đúng path của bạn

client = chromadb.PersistentClient(path=CHROMA_PATH)

print("=== COLLECTIONS ===")
collections = client.list_collections()
print(collections)

if not collections:
    print("❌ Không có collection nào → bạn chưa add data")
    exit()

# lấy collection đầu tiên (hoặc sửa đúng tên nếu bạn biết)
collection = client.get_collection(name=collections[0].name)

print("\n=== COUNT ===")
count = collection.count()
print("Total records:", count)

if count == 0:
    print("❌ Collection tồn tại nhưng KHÔNG có data")
    exit()

print("\n=== SAMPLE DATA ===")
data = collection.get(limit=3, include=["documents"])

for i, doc in enumerate(data["documents"]):
    print(f"\n--- Document {i+1} ---")
    print(doc[:300])