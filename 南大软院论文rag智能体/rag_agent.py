"""Paper RAG agent built with LlamaIndex and LangChain.

The script loads a paper PDF, builds a vector index with DashScope embeddings,
and exposes a document retrieval tool to a chat agent.
"""

from __future__ import annotations

import os
import pickle
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage
from langchain.tools import tool
from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.text_splitter import SentenceSplitter
from llama_index.embeddings.dashscope import DashScopeEmbedding
from llama_parse import LlamaParse


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
PDF_PATH = BASE_DIR / os.getenv(
    "PDF_PATH", "datas/From Mind to Machine The Rise of Manus AI as a Fully.pdf"
)
PARSED_CACHE_PATH = BASE_DIR / os.getenv("PARSED_CACHE_PATH", "parsed_documents.pkl")


def load_or_parse_documents():
    """Load cached parsed documents, or parse the PDF with LlamaParse."""
    if PARSED_CACHE_PATH.exists():
        with PARSED_CACHE_PATH.open("rb") as file:
            return pickle.load(file)

    if not PDF_PATH.exists():
        raise FileNotFoundError(f"PDF not found: {PDF_PATH}")

    parser = LlamaParse(
        api_key=os.getenv("LLAMA_PARSE_API_KEY"),
        result_type="markdown",
        verbose=True,
    )
    documents = SimpleDirectoryReader(
        input_files=[str(PDF_PATH)],
        file_extractor={".pdf": parser},
    ).load_data()

    with PARSED_CACHE_PATH.open("wb") as file:
        pickle.dump(documents, file)
    return documents


def init_retriever():
    """Initialize the LlamaIndex retriever."""
    documents = load_or_parse_documents()
    Settings.embed_model = DashScopeEmbedding(
        model_name=os.getenv("EMBED_MODEL_NAME", "text-embedding-v4"),
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        embed_batch_size=10,
        timeout=60,
    )
    splitter = SentenceSplitter(chunk_size=512, chunk_overlap=20)
    index = VectorStoreIndex.from_documents(
        documents=documents,
        text_splitter=splitter,
        show_progress=True,
    )
    top_k = int(os.getenv("RETRIEVER_TOP_K", "3"))
    return index.as_retriever(similarity_top_k=top_k)


llama_index_retriever = init_retriever()

llm = init_chat_model(
    model=os.getenv("CHAT_MODEL_NAME", "qwen3-max"),
    model_provider="openai",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url=os.getenv("DASHSCOPE_BASE_URL"),
)


@tool
def document_retriever(query: str) -> str:
    """Retrieve relevant paper passages for a user query."""
    try:
        results = llama_index_retriever.retrieve(query)
    except Exception as exc:
        return f"检索失败：{exc}"

    if not results:
        return "未检索到相关内容"

    passages = []
    for index, node in enumerate(results, start=1):
        passages.append(f"【相关内容{index}】\n{node.text}")
    return "\n\n".join(passages)


agent = create_agent(
    model=llm,
    system_prompt=(
        "你是一个专业的论文问答机器人。回答前必须先使用 document_retriever "
        "检索相关论文内容，然后基于检索结果回答。"
        "如果检索结果为空，直接说明未找到相关信息。"
    ),
    tools=[document_retriever],
)


def main() -> None:
    print("论文 RAG 智能体已启动，输入 exit 或 quit 退出。")
    while True:
        query = input("\n你：").strip()
        if query.lower() in {"exit", "quit"}:
            print("已退出。")
            break
        if not query:
            continue

        for step in agent.stream(
            {"messages": [HumanMessage(content=query)]},
            stream_mode="values",
        ):
            step["messages"][-1].pretty_print()


if __name__ == "__main__":
    main()
