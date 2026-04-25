# scripts/build_vector_store.py
import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

# 鍔犺浇 .env 鏂囦欢涓殑鐜鍙橀噺
load_dotenv()

# --- 閰嶇疆 ---
SOURCE_DIRECTORY = "data/legal_texts"
PERSIST_DIRECTORY = "vector_store/chroma"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

def build():
    """
    澶勭悊鏂囨。銆佸垱寤哄祵鍏ュ苟瀛樺偍鍒板悜閲忔暟鎹簱銆?
    """
    print("---SCRIPT: Building Vector Store---")

    # 1. 鍔犺浇鏂囨。
    print(f"Loading documents from {SOURCE_DIRECTORY}...")
    loader = DirectoryLoader(
        SOURCE_DIRECTORY,
        glob="**/*.txt", # 鍙姞杞?.txt 鏂囦欢
        loader_cls=TextLoader,
        show_progress=True,
        use_multithreading=True
    )
    documents = loader.load()

    if not documents:
        print("No documents found. Please add some .txt files to data/legal_texts.")
        # 鍒涘缓涓€涓┖鏂囦欢浣滀负绀轰緥
        sample_path = os.path.join(SOURCE_DIRECTORY, "sample_law.txt")
        if not os.path.exists(sample_path):
            with open(sample_path, "w", encoding="utf-8") as f:
                f.write("涓崕浜烘皯鍏卞拰鍥藉垜娉曡瀹氾紝鐩楃獌缃槸鎸?..")
            print(f"Created a sample file: {sample_path}")
        return

    # 2. 鍒囧垎鏂囨。
    print("Splitting documents...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    texts = text_splitter.split_documents(documents)
    print(f"Split into {len(texts)} chunks.")

    # 3. 鍒涘缓宓屽叆骞舵寔涔呭寲
    print("Creating embeddings and persisting to ChromaDB...")
    embedding_function = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(
        documents=texts,
        embedding=embedding_function,
        persist_directory=PERSIST_DIRECTORY
    )

    print("---Vector Store Built Successfully!---")
    print(f"Data persisted in: {PERSIST_DIRECTORY}")

if __name__ == "__main__":
    build()
