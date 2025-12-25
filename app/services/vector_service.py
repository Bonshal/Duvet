from sentence_transformers import SentenceTransformer

# 1. Load the model once when the server starts.
# 'all-MiniLM-L6-v2' is chosen because it's fast and free (80MB).
model = SentenceTransformer('all-MiniLM-L6-v2')

def generate_embedding(text: str) -> list[float]:
    """
    Converts a string like "Vitamin C Serum" into a list of 384 numbers.
    """
    if not text:
        return []
        
    # The model returns a numpy array, we convert it to a standard Python list
    embedding = model.encode(text).tolist()
    return embedding