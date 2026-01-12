from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from llama_parse import LlamaParse
from pathlib import Path
import config
import re


class RAGEngine:
    """
    Generic RAG engine using LlamaParse for high-quality document parsing
    """
    import os

    print("LLAMA KEY FOUND:", bool(os.getenv("LLAMA_CLOUD_API_KEY")))

    def __init__(self, persist_directory=config.VECTOR_STORE_PATH):
        self.persist_directory = persist_directory
        Path(persist_directory).mkdir(parents=True, exist_ok=True)

        print("Loading embedding model...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=config.EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"}
        )

        #  Smaller chunks = less noise
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=600,
            chunk_overlap=120,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        #  LlamaParse replaces pypdf
        self.parser = LlamaParse(
            result_type="text",     # clean text output
            verbose=False
        )

        self.vector_stores = {}

    # ------------------------------------------------------------------
    # DOCUMENT LOADING (LLAMAPARSE)
    # ------------------------------------------------------------------
    def load_pdf(self, pdf_path: str) -> str:
        try:
            #  HARD TIMEOUT (2 minutes)
            documents = self.parser.load_data(
                pdf_path,
                timeout=120
            )
            return "\n".join(doc.text for doc in documents)

        except Exception as e:
            print("LlamaParse failed or timed out. Falling back to pypdf.")
            print(e)

            # 🔁 FALLBACK (never hangs)
            import pypdf
            reader = pypdf.PdfReader(pdf_path)
            return "\n".join(page.extract_text() or "" for page in reader.pages)


    # ------------------------------------------------------------------
    # DOCUMENT PROCESSING
    # ------------------------------------------------------------------
    def process_document(self, text: str, metadata: dict = None):
        chunks = self.text_splitter.split_text(text)
        docs = []

        for i, chunk in enumerate(chunks):
            meta = metadata.copy() if metadata else {}
            meta.update({
                "chunk_id": i,
                "chunk_length": len(chunk)
            })
            docs.append(Document(page_content=chunk.strip(), metadata=meta))

        return docs

    # ------------------------------------------------------------------
    # INDEXING
    # ------------------------------------------------------------------
    def index_document(self, ticker: str, text: str, metadata: dict = None):
        if not text or len(text) < 500:
            print(f"⚠️ Document for {ticker} is too short or empty")
            return False

        metadata = metadata or {}
        metadata["ticker"] = ticker.upper()

        documents = self.process_document(text, metadata)
        collection_name = f"company_{ticker.lower()}"

        try:
            self.vector_stores[ticker] = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                collection_name=collection_name,
                persist_directory=self.persist_directory
            )
            print(f"✓ Indexed {ticker}: {len(documents)} chunks")
            return True
        except Exception as e:
            print(f"✗ Indexing error: {e}")
            return False

    # ------------------------------------------------------------------
    # QUERYING
    # ------------------------------------------------------------------
    def query_document(self, ticker: str, question: str, k: int = config.TOP_K_RESULTS):

        if ticker not in self.vector_stores:
            try:
                self.vector_stores[ticker] = Chroma(
                    collection_name=f"company_{ticker.lower()}",
                    embedding_function=self.embeddings,
                    persist_directory=self.persist_directory
                )
            except:
                return {
                    "answer": f"No indexed document for {ticker}.",
                    "sources": [],
                    "context": ""
                }

        if self._is_fact_question(question.lower()):
            k = 1

        results = self.vector_stores[ticker].similarity_search_with_score(
            question, k=k
        )

        if not results:
            return {
                "answer": "No relevant information found.",
                "sources": [],
                "context": ""
            }

        
        best_doc, score = results[0]

        answer = self._generate_answer(question, best_doc.page_content)

        return {
            "answer": answer,
            "sources": [{
                "content": best_doc.page_content,   
                "chunk_id": best_doc.metadata.get("chunk_id"),
                "relevance_score": float(score)
            }],
            "context": best_doc.page_content[:2000]
        }


    # ------------------------------------------------------------------
    # ANSWER GENERATION
    # ------------------------------------------------------------------
    def _generate_answer(self, question: str, context: str) -> str:
        question_lower = question.lower()
        keywords = self._extract_keywords(question_lower)

        sentences = re.split(r'(?<=[.!?])\s+', context)
        scored = []

        for s in sentences:
            s_lower = s.lower()
            score = sum(1 for kw in keywords if kw in s_lower)

            if re.search(r"\b(18|19|20)\d{2}\b", s):
                score += 2

            if score > 0 and len(s) > 30:
                scored.append((score, s.strip()))

        if not scored:
            return "The document does not provide a direct answer to this question."

        scored.sort(reverse=True, key=lambda x: x[0])

        # Fact → single sentence
        if self._is_fact_question(question_lower):
            return scored[0][1]

        # Descriptive → up to 2 sentences
        return " ".join(s for _, s in scored[:2])

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------
    def _extract_keywords(self, question: str):
        stop_words = {
            "what", "when", "where", "who", "how",
            "is", "are", "the", "a", "an", "their", "them"
        }
        return [
            w for w in re.findall(r"\b[a-zA-Z]{3,}\b", question)
            if w not in stop_words
        ]

    def _is_fact_question(self, question: str):
        return any(
            kw in question for kw in
            ["year", "when", "how many", "number", "date", "incorporated", "founded"]
        )

    # ------------------------------------------------------------------
    # UTILS
    # ------------------------------------------------------------------
    def list_indexed_companies(self):
        return list(self.vector_stores.keys())

    def get_document_stats(self, ticker: str):
        if ticker not in self.vector_stores:
            return None
        try:
            count = self.vector_stores[ticker]._collection.count()
            return {"ticker": ticker, "chunk_count": count}
        except:
            return None
