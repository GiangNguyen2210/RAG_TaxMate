import pickle

with open("./chroma_db/9d0fd4b0-7d3d-4d0e-85f7-ab777c9e54ac/index_metadata.pickle", "rb") as f:
    metadata = pickle.load(f)

print(type(metadata))

if isinstance(metadata, dict):
    print("\nALL KEYS:")
    for k in metadata.keys():
        print(k)