# 南大软院论文 RAG 智能体

这是一个面向论文问答的 RAG 学习项目。项目使用 LlamaParse 解析 PDF，使用 LlamaIndex 构建向量索引，并通过 LangChain Agent 调用检索工具完成基于论文内容的问答。

## 功能

- 从论文 PDF 中解析结构化文本
- 使用 DashScope Embedding 构建向量索引
- 基于用户问题检索相关论文片段
- 通过 Agent 先检索、再回答，减少脱离论文内容的回答
- 支持复用 `parsed_documents.pkl`，避免每次重新解析 PDF

## 项目结构

```text
.
├── rag_agent.py                                      # 推荐运行入口
├── agent.ipynb                                      # 原始 Notebook 学习记录
├── parsed_documents.pkl                             # 已解析文档缓存
├── datas/
│   └── From Mind to Machine The Rise of Manus AI as a Fully.pdf
├── requirements.txt
└── .env.example
```

## 快速开始

1. 创建并激活虚拟环境。

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. 安装依赖。

```bash
pip install -r requirements.txt
```

3. 复制环境变量模板并填写 API Key。

```bash
copy .env.example .env
```

4. 启动论文问答 Agent。

```bash
python rag_agent.py
```

## 环境变量

| 变量名 | 说明 |
| --- | --- |
| `DASHSCOPE_API_KEY` | DashScope API Key，用于聊天模型和 Embedding |
| `DASHSCOPE_BASE_URL` | OpenAI 兼容接口地址 |
| `CHAT_MODEL_NAME` | 聊天模型名，默认 `qwen3-max` |
| `LLAMA_PARSE_API_KEY` | LlamaParse API Key，仅在没有缓存时解析 PDF 需要 |
| `PDF_PATH` | 论文 PDF 路径 |
| `PARSED_CACHE_PATH` | 解析缓存路径，默认 `parsed_documents.pkl` |
| `EMBED_MODEL_NAME` | Embedding 模型名，默认 `text-embedding-v4` |
| `RETRIEVER_TOP_K` | 每次检索返回片段数，默认 `3` |

## 示例问题

```text
什么是 Manus AI？
论文如何描述 Manus AI 的自主性？
Manus AI 相比传统智能体有什么不同？
这篇论文提到了哪些潜在风险？
```

## 说明

仓库中保留了 `parsed_documents.pkl`，因此通常不需要重新调用 LlamaParse 解析 PDF。若更换论文或删除缓存，则需要配置 `LLAMA_PARSE_API_KEY` 后重新运行。
