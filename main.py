import os
import sys
import yaml
import argparse
import json
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

from logger import get_logger
from utils import (
    find_files, load_documents, split_documents,
    build_or_load_faiss, make_retriever, make_rag_chain,
    extract_product_info, format_sources
)


# ------------------------
# Config & Env
# ------------------------
def load_config(config_path: str = "config.yaml") -> dict:
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        sys.exit(f"[ERROR] Config file not found: {config_path}")
    except yaml.YAMLError as e:
        sys.exit(f"[ERROR] Failed to parse config file: {e}")


def parse_args():
    parser = argparse.ArgumentParser(description="RAG Application")
    parser.add_argument("--rebuild", action="store_true", help="Force rebuild of FAISS index")
    parser.add_argument("--docs", type=str, help="Path to documents directory")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to config.yaml")
    return parser.parse_args()


# ------------------------
# Conversation History
# ------------------------
def save_conversation(history_file: Path, query: str, answer: str, sources: list, product_info: dict):
    """Append conversation data into a JSON log file."""
    history_file.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "query": query,
        "answer": answer,
        "sources": sources,
        "products": product_info
    }

    if history_file.exists():
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = []
    else:
        data = []

    data.append(record)

    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ------------------------
# Main Application
# ------------------------
def main():
    # Load .env
    load_dotenv()
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if not GOOGLE_API_KEY or not GROQ_API_KEY:
        sys.exit("[ERROR] Missing API keys in .env file")

    # Parse config + args
    args = parse_args()
    config = load_config(args.config)

    if args.docs:
        config["paths"]["docs"] = args.docs
    if args.rebuild:
        config["index"]["rebuild"] = True

    logger = get_logger("RAG-App", config["logging"]["file"], config["logging"]["level"])
    history_file = Path(config["logging"].get("history_file", "logs/history.json"))

    logger.info("🚀 Starting RAG pipeline...")

    docs_path = Path(config["paths"]["docs"])
    index_path = Path(config["paths"]["index"])
    rebuild_index = config["index"]["rebuild"]

    chunks = []
    if rebuild_index:
        logger.info(f"📂 Scanning docs in {docs_path}")
        files = find_files(docs_path)
        if not files:
            logger.error("❌ No documents found in dataset folder")
            return
        logger.info(f"✅ Found {len(files)} files. Loading...")

        docs = load_documents(files)
        logger.info(f"✅ Loaded {len(docs)} documents. Splitting...")

        chunks = split_documents(docs, config["splitter"])
        logger.info(f"✅ Created {len(chunks)} chunks.")

    logger.info("🔍 Building/Loading FAISS index...")
    vectorstore = build_or_load_faiss(
        chunks, rebuild_index, index_path, config["models"]["embedding"]
    )
    logger.info("✅ Vectorstore ready")

    retriever = make_retriever(vectorstore, config["retriever"])
    rag_chain = make_rag_chain(retriever, config["models"]["chat"])

    logger.info("✅ RAG setup complete. Entering interactive mode.")

    # Interactive Loop
    try:
        while True:
            query = input("\n❓ Your question (type 'exit' to quit): ")
            if query.lower() in ("exit", "quit"):
                print("👋 Goodbye!")
                logger.info("Application terminated by user")
                break

            try:
                logger.info(f"📝 New Query: {query}")
                result = rag_chain.invoke({"input": query})
                ctx = result.get("context", [])
                product_info = extract_product_info(ctx)

                # Decide on answer
                if product_info:
                    answer = "Product info extracted"
                    print("\n📦 Product Info:")
                    for product, entries in product_info.items():
                        print(f" {product}")
                        for e in entries:
                            print(f"  - {e['source']}: {e['price']} ({e['discount']} → {e['discounted_price']})")
                else:
                    answer = result.get("answer") or result.get("output") or str(result)
                    print("\n💡 Answer:", answer.strip())

                sources = format_sources(ctx) if ctx else []
                if sources:
                    print("\n📚 Sources:", sources)

                # Save conversation history
                save_conversation(history_file, query, answer, sources, product_info)
                logger.info(f"💾 Saved query & response to {history_file}")

            except Exception as e:
                logger.exception(f"❌ Query failed: {e}")
                print("[ERROR] Query failed. See logs for details.")

    except KeyboardInterrupt:
        print("\n👋 Exiting gracefully...")
        logger.info("Interrupted by user")


if __name__ == "__main__":
    main()