# app/utils/retriever.py
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

def get_retriever(persist_directory: str = "./vector_store/chroma"):
    """
    鍒涘缓骞惰繑鍥炰竴涓悜閲忔暟鎹簱鐨勬绱㈠櫒銆?

    Args:
        persist_directory: 鍚戦噺鏁版嵁搴撶殑鎸佷箙鍖栫洰褰曘€?

    Returns:
        涓€涓厤缃ソ鐨勬绱㈠櫒瀵硅薄銆?
    """
    print("---UTIL: Loading Vector Store---")
    # 鍦ㄨ繖閲屽姞杞藉悜閲忔暟鎹簱鍜屽祵鍏ユā鍨?
    # vectorstore = Chroma(
    #     persist_directory=persist_directory,
    #     embedding_function=OpenAIEmbeddings()
    # )
    # retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    # return retriever

    # 杩欐槸涓€涓崰浣嶇瀹炵幇
    class PlaceholderRetriever:
        def invoke(self, query):
            print(f"---UTIL: Retrieving documents for query: {query}---")
            return ["浠庡悜閲忔暟鎹簱妫€绱㈠埌鐨勬硶鏉?", "浠庡悜閲忔暟鎹簱妫€绱㈠埌鐨勬硶鏉?"]

    return PlaceholderRetriever()
