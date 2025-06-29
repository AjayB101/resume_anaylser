import uuid
import json
from typing import Any, List, Optional
from chromadb import PersistentClient
from chromadb.config import Settings

# Setup ChromaDB client and collection
client = PersistentClient(
    path="my_chroma_db",
    settings=Settings(allow_reset=True)
)

# Collection for behavioral interview Q&A
behavioral_qna_collection = client.get_or_create_collection("behavioral_qna")


def save_qna_for_category(questions: List[dict], min_count: int = 2) -> None:
    """
    Save behavioral interview Q&A to ChromaDB if category doesn't have enough items.

    Args:
        questions: List of dicts with keys: question, answer, source, category
        min_count: Minimum number of items that should exist in category before skipping

    Returns:
        None
    """
    if not questions:
        print("📝 No questions to save")
        return

    # Group questions by category to check counts efficiently
    questions_by_category = {}
    for item in questions:
        category = item.get("category")
        if category:
            if category not in questions_by_category:
                questions_by_category[category] = []
            questions_by_category[category].append(item)

    for category, category_questions in questions_by_category.items():
        try:
            # Check existing count for this category
            existing_result = behavioral_qna_collection.query(
                query_texts=[category],
                n_results=1000,  # Get all items to count accurately
                where={"category": category}
            )

            existing_count = 0
            if existing_result and existing_result.get("documents"):
                documents = existing_result.get("documents", [[]])
                if documents and len(documents) > 0:
                    existing_count = len(documents[0])

            print(
                f"📊 Category '{category}' has {existing_count} existing items (min required: {min_count})")

            # Skip if already have enough items
            if existing_count >= min_count:
                print(
                    f"✅ Category '{category}' already has sufficient items ({existing_count} >= {min_count}). Skipping.")
                continue

            # Get existing questions for duplicate checking
            existing_questions = []
            if existing_result and existing_result.get("documents"):
                documents = existing_result.get("documents", [[]])
                if documents and len(documents) > 0:
                    existing_questions = [q.lower().strip()
                                          for q in documents[0]]

            # Process each question in this category
            added_count = 0
            for item in category_questions:
                question = item.get("question")
                answer = item.get("answer")
                source = item.get("source")

                # Skip items with missing required fields
                if not all([question, answer, source, category]):
                    print(f"⚠️ Skipping item with missing fields: {item}")
                    continue

                # Check for exact duplicates within category
                question_normalized = question.lower().strip()
                if question_normalized in existing_questions:
                    print(
                        f"🔄 Question already exists in category '{category}'. Skipping: {question[:50]}...")
                    continue

                # Add to collection
                try:
                    behavioral_qna_collection.add(
                        documents=[question],
                        metadatas=[{
                            "sample_answer": answer,
                            "source": source,
                            "category": category
                        }],
                        ids=[str(uuid.uuid4())],
                    )
                    existing_questions.append(
                        question_normalized)  # Update local cache
                    added_count += 1
                    print(
                        f"✅ Added question to category '{category}': {question[:50]}...")

                except Exception as e:
                    print(f"❌ Error adding question: {e}")

            print(
                f"📝 Added {added_count} new questions to category '{category}'")

        except Exception as e:
            print(f"❌ Error processing category '{category}': {e}")


def get_qna_by_category(category: str) -> List[dict]:
    """
    Retrieve all behavioral interview Q&A for a specific category.

    Args:
        category: The category to filter by

    Returns:
        List of dicts with keys: question, answer, source, category
    """
    try:
        # Query for all items in the specified category
        result = behavioral_qna_collection.query(
            query_texts=[category],
            n_results=4,  # Get all items
            where={"category": category}
        )

        # Handle case where result is None
        if result is None:
            print(
                f"❌ No results returned from collection query for category '{category}'")
            return []

        # Extract metadatas and documents with proper None handling
        metadatas_raw = result.get("metadatas", [[]])
        documents_raw = result.get("documents", [[]])

        metadatas = metadatas_raw[0] if metadatas_raw and len(
            metadatas_raw) > 0 else []
        documents = documents_raw[0] if documents_raw and len(
            documents_raw) > 0 else []

        # Ensure both lists have the same length to avoid index errors
        if len(metadatas) != len(documents):
            print(
                f"⚠️ Warning: Metadata count ({len(metadatas)}) doesn't match document count ({len(documents)})")
            min_length = min(len(metadatas), len(documents))
            metadatas = metadatas[:min_length]
            documents = documents[:min_length]

        # Build result list
        matching_questions = []
        for doc, meta in zip(documents, metadatas):
            # Ensure meta is not None and has the required fields
            if meta and meta.get("category") == category:
                matching_questions.append({
                    "question": doc,
                    "answer": meta.get("sample_answer"),
                    "source": meta.get("source"),
                    "category": meta.get("category")
                })

        print(
            f"🎯 Found {len(matching_questions)} questions in category '{category}'")
        return matching_questions

    except Exception as e:
        print(f"❌ Error fetching questions for category '{category}': {e}")
        return []
