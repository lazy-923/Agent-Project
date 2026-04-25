# Mini Deep Research

这是一个迷你版 Deep Research 学习项目，用 LangGraph 串联“规划搜索 -> 执行网页搜索 -> 汇总生成研究报告”的多节点工作流。项目目标是演示如何把复杂研究任务拆成可观察、可扩展的 Agent Graph。

## 工作流

```text
用户问题
  -> planner_node：生成 3-4 个搜索关键词和理由
  -> search_node：调用 Tavily 搜索并提炼摘要
  -> writer_node：整合搜索摘要，输出 Markdown 研究报告
```

## 项目结构

```text
.
├── deepresearch.py              # 推荐入口，暴露 LangGraph graph
├── mini-deepresearch-2.0.py      # 原始学习脚本
├── mini-deepresearch-1.0.ipynb   # Notebook 学习记录
├── mini-deepresearch-2.0.ipynb   # Notebook 学习记录
├── langgraph.json               # LangGraph dev server 配置
├── requirements.txt             # Python 依赖
├── .env.example                 # 环境变量模板
└── agent-chat-ui/               # 可选 Next.js 聊天前端
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

3. 复制环境变量模板并填写模型服务和 Tavily Key。

```bash
copy .env.example .env
```

4. 命令行运行一次研究任务。

```bash
python deepresearch.py
```

5. 或使用 LangGraph dev server。

```bash
langgraph dev
```

`langgraph.json` 中注册的图 ID 是 `deepresearch`。

## 环境变量

| 变量名 | 说明 |
| --- | --- |
| `BASE_URL` | OpenAI 兼容模型服务地址，例如 DashScope 兼容模式地址 |
| `API_KEY` | 模型服务 API Key |
| `MODEL_NAME` | 模型名称，默认 `qwen3-max` |
| `TAVILY_API_KEY` | Tavily 搜索 API Key |

## 示例问题

```text
2025 年国内外多智能体框架的发展趋势是什么？
LangGraph 相比传统 ReAct Agent 的优势和限制是什么？
企业引入 RAG 系统时最常见的失败原因有哪些？
```

## 前端

`agent-chat-ui/` 是可选的 LangGraph 聊天前端。后端通过 `langgraph dev` 启动后，可以在前端中配置：

```text
Deployment URL: http://localhost:2024
Assistant/Graph ID: deepresearch
```

## 说明

这个项目依赖实时网页搜索和大模型调用，运行时需要可用的网络、模型 API Key 和 Tavily API Key。Notebook 文件作为学习过程保留，推荐展示和运行时使用 `deepresearch.py`。
