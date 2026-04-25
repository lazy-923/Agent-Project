# Agent-Project

这个仓库用于整理我在学习 Agent 开发过程中的多个练习项目。每个子项目都尽量保留学习痕迹，同时补充可运行的 Python 入口、依赖文件、环境变量模板和 README，方便后续在 GitHub 上展示。

## 项目索引

| 项目 | 说明 | 推荐入口 |
| --- | --- | --- |
| `dataAnalyse-singleAgent` | 单 Agent 数据分析助手，集成 SQL、Python、绘图和搜索工具 | `agent.py` |
| `dataAnalyse-基于langgraph的多代理` | 基于 LangGraph 的多 Agent 数据分析示例，包含 Supervisor 调度 | `multi_agent_supervisor.py` |
| `mini-deepresearch` | 迷你 Deep Research 工作流，包含规划搜索、网页搜索和报告生成 | `deepresearch.py` |
| `南大软院论文rag智能体` | 面向论文 PDF 的 RAG 问答智能体 | `rag_agent.py` |
| `irac 法律顾问` | 基于 IRAC 框架的法律顾问智能体，新版仍在开发，初版刑事案件判断已归档 | `legacy_criminal_case/counselor-agent.py` |

## 使用说明

每个项目目录下都有独立的 `README.md`、`requirements.txt` 和 `.env.example`。运行前通常需要：

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

然后根据各项目 README 填写模型服务、搜索服务或数据库相关环境变量。

## 注意

- Notebook 文件主要作为学习过程记录，推荐展示和运行时使用整理后的 `.py` 文件。
- 法律相关项目仅用于 Agent 技术学习和流程演示，不构成法律意见。
