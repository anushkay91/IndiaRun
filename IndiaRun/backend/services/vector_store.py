# pyrefly: ignore [missing-import]
import numpy as np
# pyrefly: ignore [missing-import]
import faiss
from typing import List, Tuple, Dict

class VectorStore:
    def __init__(self, dimension: int = 3072):
        """Initialize the FAISS index with the specified dimension (3072 for models/gemini-embedding-2)."""
        self.dimension = dimension
        # Use IndexFlatIP (Inner Product) which behaves as Cosine Similarity when vectors are normalized
        self.index = faiss.IndexFlatIP(self.dimension)
        # Map sequential FAISS internal indices to actual SQLite Candidate IDs
        self.vector_id_to_candidate_id: List[int] = []

    def _normalize_vector(self, vector: List[float]) -> np.ndarray:
        """Convert a list of floats to a normalized numpy float32 array."""
        arr = np.array(vector, dtype=np.float32)
        if len(arr.shape) == 1:
            arr = np.expand_dims(arr, axis=0)
        norm = np.linalg.norm(arr, axis=1, keepdims=True)
        # Avoid division by zero
        norm = np.where(norm == 0, 1.0, norm)
        return arr / norm

    def add_candidate(self, candidate_id: int, embedding: List[float]) -> None:
        """Add a single candidate embedding to the FAISS index."""
        normalized_vector = self._normalize_vector(embedding)
        self.index.add(normalized_vector)
        self.vector_id_to_candidate_id.append(candidate_id)

    def search(self, query_embedding: List[float], top_n: int = 5) -> List[Tuple[int, float]]:
        """Search the FAISS index for the top_n most similar candidates.
        
        Returns a list of tuples containing (candidate_id, score).
        """
        if self.index.ntotal == 0:
            return []

        normalized_query = self._normalize_vector(query_embedding)
        
        # Limit top_n to the total number of items indexed
        actual_top_n = min(top_n, self.index.ntotal)
        if actual_top_n == 0:
            return []

        # D: distances (similarity scores), I: internal FAISS indices
        D, I = self.index.search(normalized_query, actual_top_n)
        
        results = []
        for score, internal_idx in zip(D[0], I[0]):
            if internal_idx == -1:
                continue
            # Map back to SQLite candidate ID
            candidate_id = self.vector_id_to_candidate_id[internal_idx]
            # Convert float32 to python float
            results.append((candidate_id, float(score)))
            
        return results

    def rebuild(self, candidates_data: List[Tuple[int, List[float]]]) -> None:
        """Rebuild the entire FAISS index from scratch with the provided data.
        
        candidates_data is a list of tuples: (candidate_id, embedding_vector)
        """
        self.index = faiss.IndexFlatIP(self.dimension)
        self.vector_id_to_candidate_id = []
        
        if not candidates_data:
            return

        embeddings = []
        for cid, emb in candidates_data:
            self.vector_id_to_candidate_id.append(cid)
            embeddings.append(emb)
            
        # Convert to numpy matrix and normalize all vectors
        emb_matrix = np.array(embeddings, dtype=np.float32)
        norms = np.linalg.norm(emb_matrix, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1.0, norms)
        normalized_embeddings = emb_matrix / norms
        
        self.index.add(normalized_embeddings)

    @property
    def total_vectors(self) -> int:
        return self.index.ntotal

# Global instance of VectorStore
vector_store = VectorStore()

