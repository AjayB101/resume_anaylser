import uuid
import json
from typing import Any, List, Optional
from chromadb import PersistentClient
from chromadb.config import Settings

# Setup ChromaDB client and collections
client = PersistentClient(
    path="my_chroma_db", settings=Settings(allow_reset=True))

# Existing collection for individual questions
collection = client.get_or_create_collection("behavioral_qna")

# New collection for caching search queries with their questions
query_cache_collection = client.get_or_create_collection("query_cache")


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
    """Save individual questions to the main collection"""
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
                    print("✅ Question already exists. Skipping.")
                    continue

                collection.add(
                    documents=[question],
                    metadatas=[{"sample_answer": answer, "source": source}],
                    ids=[str(uuid.uuid4())],
                )
                print("✅ Question added.")
            except Exception as e:
                print(f"❌ Error checking/adding question: {e}")


def save_query_with_questions(search_query: str, questions: List[str], full_qna_data: List[dict]) -> bool:
    """
    Cache a search query with its generated questions to avoid future LLM calls.

    Args:
        search_query: The search query string
        questions: List of question strings only
        full_qna_data: Complete Q&A data with answers and sources

    Returns:
        True if successfully cached, False otherwise
    """
    try:
        # Check if this exact query is already cached
        existing = query_cache_collection.query(
            query_texts=[search_query],
            n_results=1
        )

        documents = existing.get("documents")
        if documents and documents[0] and len(documents[0]) > 0:
            # Check for exact match
            existing_doc = documents[0][0]
            if existing_doc.strip().lower() == search_query.strip().lower():
                print("🔄 Query already cached. Updating...")
                # You might want to update or skip based on your needs
                return False

        # Cache the query with its questions
        query_cache_collection.add(
            documents=[search_query],
            metadatas=[{
                "questions": json.dumps(questions),
                "full_data": json.dumps(full_qna_data),
                "question_count": len(questions),
                # Using UUID as timestamp alternative
                "cached_at": str(uuid.uuid4())
            }],
            ids=[str(uuid.uuid4())]
        )

        print(f"💾 Successfully cached query with {len(questions)} questions")
        return True

    except Exception as e:
        print(f"❌ Error caching query: {e}")
        return False


def get_cached_questions_by_query(search_query: str) -> Optional[List[str]]:
    """
    Retrieve cached questions for a given search query.

    Args:
        search_query: The search query to look up

    Returns:
        List of questions if found, None if not cached
    """
    try:
        # Search for similar queries (you can adjust similarity threshold)
        result = query_cache_collection.query(
            query_texts=[search_query],
            n_results=3  # Get top 3 similar queries
        )

        documents = result.get("documents")
        metadatas = result.get("metadatas")

        if not documents or not documents[0] or not metadatas or not metadatas[0]:
            return None

        # Check for exact or very similar matches
        for i, doc in enumerate(documents[0]):
            if doc.strip().lower() == search_query.strip().lower():
                # Exact match found
                metadata = metadatas[0][i]
                questions_json = metadata.get("questions")

                if questions_json and isinstance(questions_json, str):
                    try:
                        questions = json.loads(questions_json)
                        print(
                            f"🎯 Found exact match with {len(questions)} cached questions")
                        return questions
                    except json.JSONDecodeError:
                        print("❌ Error parsing cached questions JSON")
                        continue

        # If no exact match, you could implement similarity-based matching here
        # For now, we'll be strict and only return exact matches
        return None

    except Exception as e:
        print(f"❌ Error retrieving cached questions: {e}")
        return None


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


def clear_query_cache() -> bool:
    """
    Utility function to clear the query cache collection.
    Use with caution!
    """
    try:
        query_cache_collection.delete()
        print("🗑️ Query cache cleared successfully")
        return True
    except Exception as e:
        print(f"❌ Error clearing query cache: {e}")
        return False


def get_cache_stats() -> dict:
    """
    Get statistics about the query cache.
    """
    try:
        # Get count of cached queries
        result = query_cache_collection.get()

        if result and result.get("documents"):
            documents = result["documents"]
            if documents is not None:
                cached_queries_count = len(documents)
            else:
                cached_queries_count = 0

            # Calculate total questions cached
            total_questions = 0
            metadatas = result.get("metadatas", [])

            if metadatas:
                for metadata in metadatas:
                    if metadata and isinstance(metadata, dict):
                        question_count = metadata.get("question_count", 0)
                        if isinstance(question_count, (int, float)):
                            total_questions += int(question_count)

            return {
                "cached_queries": cached_queries_count,
                "total_cached_questions": total_questions,
                "average_questions_per_query": total_questions / cached_queries_count if cached_queries_count > 0 else 0
            }
        else:
            return {
                "cached_queries": 0,
                "total_cached_questions": 0,
                "average_questions_per_query": 0
            }

    except Exception as e:
        print(f"❌ Error getting cache stats: {e}")
        return {
            "cached_queries": 0,
            "total_cached_questions": 0,
            "average_questions_per_query": 0,
            "error": str(e)
        }
