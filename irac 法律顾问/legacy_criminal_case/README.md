# 初版法律顾问：刑事案件判断

这个目录归档了早期的 `irac法律顾问` 项目。它是一个基于 IRAC 方法的法律判断 Agent，目前作为新版 IRAC 项目中“刑事案件判断”部分的参考实现。

## 流程

```text
案件事实
  -> IssueAgent：识别核心法律议题
  -> RuleAgent：检索和整理相关法律规则
  -> ApplicationAgent：将规则适用于案件事实
  -> ConclusionAgent：生成裁判理由和最终判断
```

## 文件说明

```text
.
├── counselor-agent.py   # LangGraph 图定义和四阶段 Agent
├── prompts.py           # 提示词、结构化分析要求和示例案情
├── langgraph.json       # LangGraph dev server 配置
├── requirements.txt     # Python 依赖
├── .env.example         # 环境变量模板
├── schedule.md          # 原始开发计划记录
└── 法律顾问.ipynb        # Notebook 学习记录
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

4. 使用 LangGraph dev server 运行。

```bash
langgraph dev
```

`langgraph.json` 中注册的图 ID 是 `law_judgement`。

## 展示重点

这个初版更适合展示 IRAC 刑事案件判断链路：议题识别、规则提取、事实适用、结论生成。新版 `app/` 会继续拆分模块，但当前目录保留为一个相对完整的阶段成果。

## 免责声明

本项目仅用于学习和技术演示，不构成法律意见。
