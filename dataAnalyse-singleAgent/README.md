# 单 Agent 数据分析助手

这是一个基于 LangChain Agent 的数据分析学习项目。Agent 集成了 MySQL 查询、数据表提取、Python 代码执行、Matplotlib/Seaborn 可视化和 Tavily 搜索能力，适合演示“让大模型调用工具完成数据分析任务”的基础工作流。

## 功能

- 使用自然语言生成并执行 MySQL 查询
- 将 SQL 查询结果提取为 pandas DataFrame
- 执行轻量级 Python 数据处理代码
- 生成并保存 Matplotlib/Seaborn 图表
- 在非数据分析问题中调用 Tavily 搜索

## 项目结构

```text
.
├── agent.py          # Agent、工具函数和命令行入口
├── requirements.txt  # Python 依赖
└── .env.example      # 环境变量模板
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

3. 复制环境变量模板并填写密钥、数据库连接信息。

```bash
copy .env.example .env
```

4. 启动命令行 Agent。

```bash
python agent.py
```

## 环境变量

| 变量名 | 说明 |
| --- | --- |
| `DEEPSEEK_API_KEY` | DeepSeek 模型 API Key |
| `TAVILY_API_KEY` | Tavily 搜索 API Key |
| `HOST` | MySQL 主机地址 |
| `USER` | MySQL 用户名 |
| `MYSQL_PW` | MySQL 密码 |
| `DB_NAME` | MySQL 数据库名 |
| `PORT` | MySQL 端口，默认 `3306` |
| `FIGURE_PUBLIC_DIR` | 图表保存根目录，生成图片会写入其下的 `images/` |

## 示例问题

```text
查询客户表中前 10 条记录
把 churn 表读取为 df_churn
统计 df_churn 中不同套餐类型的客户数量
画出不同合同类型下流失率的柱状图
```

## 说明

这个项目是学习型 demo，默认允许 Agent 执行 Python 代码和 SQL 查询。请只在可信环境和测试数据库中运行，不要直接连接生产数据库。
