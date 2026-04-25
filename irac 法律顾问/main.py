# main.py
import os
from dotenv import load_dotenv
from app.graph import build_graph

# 鍔犺浇 .env 鏂囦欢涓殑鐜鍙橀噺
# 纭繚鍦ㄥ鍏ヤ换浣?langchain_openai 鐩稿叧妯″潡涔嬪墠璋冪敤
load_dotenv()

def main():
    """
    涓诲嚱鏁帮紝鎻愪緵涓€涓懡浠よ浜や簰鐣岄潰銆?
    """
    # 妫€鏌?API 瀵嗛挜鏄惁璁剧疆
    if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your_api_key":
        print("閿欒锛歄PENAI_API_KEY 鏈缃€?)
        print("璇峰湪 .env 鏂囦欢涓缃偍鐨?OpenAI API 瀵嗛挜銆?)
        return

    # 鏋勫缓鍥?
    app = build_graph()

    print("\n娉曞緥椤鹃棶鏅鸿兘浣撳凡鍚姩锛?)
    print("鎮ㄥ彲浠ュ紑濮嬫彁闂簡銆傝緭鍏?'exit' 鎴?'quit' 閫€鍑恒€?)

    while True:
        try:
            user_input = input("\n浣? ")
            if user_input.lower() in ["exit", "quit"]:
                print("鍐嶈锛?)
                break

            # 璋冪敤鍥?
            inputs = {"question": user_input}
            # stream() 鏂规硶鍙互瀹炴椂鏄剧ず姣忎釜鑺傜偣鐨勮緭鍑?
            for output in app.stream(inputs):
                # stream() 杩斿洖涓€涓瓧鍏革紝key鏄妭鐐瑰悕锛寁alue鏄鑺傜偣鐨勮繑鍥炲€?
                for key, value in output.items():
                    print(f"---NODE: {key}---")
                    print(value)

        except KeyboardInterrupt:
            print("\n鍐嶈锛?)
            break
        except Exception as e:
            print(f"\n鍙戠敓閿欒: {e}")

if __name__ == "__main__":
    main()
