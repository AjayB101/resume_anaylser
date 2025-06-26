import uuid
from typing import Any, List
from chromadb import PersistentClient
from chromadb.config import Settings

# Setup ChromaDB client and collection
client = PersistentClient(
    path="my_chroma_db", settings=Settings(allow_reset=True))
collection = client.get_or_create_collection("behavioral_qna")


def add_question_if_missing(question: str, sample_answer: str, source: str) -> bool:
    """
    Add question to ChromaDB only if it doesn't already exist.
    Returns True if added, False if already existed.
    """
    try:
        result = collection.query(query_texts=[question], n_results=5)
        documents = result.get("documents")

        if not documents or not isinstance(documents, list) or not documents[0]:
            existing_questions = []
        else:
            existing_questions = documents[0]

        if any(q.strip().lower() == question.strip().lower() for q in existing_questions):
            print("✅ Question already exists. Skipping.")
            return False

        # Add new question with metadata
        collection.add(
            documents=[question],
            metadatas=[{
                "sample_answer": sample_answer,
                "source": source
            }],
            ids=[str(uuid.uuid4())]
        )
        print("✅ New question added to ChromaDB.")
        return True

    except Exception as e:
        print(f"❌ Error adding question: {e}")
        return False


def save_questions_if_new(questions: List[dict]):
    for item in questions:
        question = item.get("question")
        answer = item.get("answer")  # note: 'answer' key from your response
        source = item.get("source")

        if question and answer and source:
            try:
                existing = collection.query(
                    query_texts=[question], n_results=3)
                documents = existing.get("documents") or [[]]

                found = documents[0] if documents and isinstance(
                    documents, list) and documents[0] else []

                if any(q.lower().strip() == question.lower().strip() for q in found):
                    print("⚠️ Question already exists. Skipping.")
                    continue

                collection.add(
                    documents=[question],
                    metadatas=[{"sample_answer": answer, "source": source}],
                    ids=[str(uuid.uuid4())],
                )
                print("✅ Question added.")
            except Exception as e:
                print(f"❌ Error checking/adding question: {e}")


def get_top_matches(query: str, n_results: int = 3) -> List[Any]:
    """
    Search ChromaDB for top N similar questions.
    Returns a list of metadata dicts.
    """
    try:
        result = collection.query(query_texts=[query], n_results=n_results)
        metadatas = result.get("metadatas")

        if not metadatas or not isinstance(metadatas, list) or not metadatas[0]:
            return []

        return metadatas[0]  # list[dict]

    except Exception as e:
        print(f"❌ Error during search: {e}")
        return []
