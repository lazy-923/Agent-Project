# 基于 LangGraph 的多代理数据分析

这是一个多 Agent 数据分析学习项目，演示如何用 LangGraph 组织多个角色协作完成数据查询、Python 分析和普通对话任务。原始 Notebook 保留为学习过程记录，推荐运行入口是 `multi_agent_supervisor.py`。

## 项目亮点

- Supervisor 节点根据用户问题选择下一个工作 Agent
- `sqler` Agent 负责销售数据库的增删改查和数据查询
- `coder` Agent 负责调用 Python REPL 完成计算或分析
- `chat` Agent 负责普通自然语言回答
- 默认使用本地 SQLite 示例数据库，clone 后更容易启动

## 项目结构

```text
.
├── multi_agent_supervisor.py     # 推荐入口，暴露 LangGraph graph
├── agent_supervisor.ipynb        # Supervisor 多代理实验记录
├── agent_network.ipynb           # Network 多代理实验记录
├── agent_graphrag_neo4j.ipynb    # GraphRAG + Neo4j 实验记录
├── company.txt                   # GraphRAG 示例文本
├── langgraph.json                # LangGraph dev server 配置
├── requirements.txt              # Python 依赖
└── .env.example                  # 环境变量模板
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

3. 复制环境变量模板并填写模型服务信息。

```bash
copy .env.example .env
```

4. 命令行运行。

```bash
python multi_agent_supervisor.py
```

5. 或使用 LangGraph dev server。

```bash
langgraph dev
```

`langgraph.json` 中注册的图 ID 是 `multi_agent_data_analyst`。

## 环境变量

| 变量名 | 说明 |
| --- | --- |
| `BASE_URL` | OpenAI 兼容模型服务地址 |
| `API_KEY` | 模型服务 API Key |
| `MODEL_NAME` | Supervisor、SQL、Chat 使用的模型，默认 `qwen3-max` |
| `CODER_MODEL_NAME` | Python 分析 Agent 使用的模型，默认 `qwen-coder-turbo` |
| `DATABASE_URL` | SQLAlchemy 数据库连接，默认 `sqlite:///sales_demo.db` |

## 示例问题

```text
查询销售额最高的前 5 条记录，并解释这些记录有什么特点
新增一条销售记录：product_id=1, employee_id=2, customer_id=3, sale_date=2026-01-01, quantity=4, amount=999.9, discount=0.05
帮我用 Python 计算 1 到 100 的平方和
你好，请介绍一下这个多代理系统的角色分工
```

## 说明

项目启动时会自动创建一个本地 `sales_demo.db` 示例数据库并填充模拟销售数据。如果你设置了 `DATABASE_URL`，则会连接到指定数据库。请不要把真实 `.env` 上传到 GitHub。
