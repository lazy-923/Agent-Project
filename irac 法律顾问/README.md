# IRAC 法律顾问智能体

这是一个基于 IRAC（Issue、Rule、Application、Conclusion）法律分析框架的智能体学习项目。当前仓库中包含两个阶段：

- `legacy_criminal_case/`：初版法律顾问智能体，已经沉淀为“刑事案件判断”部分的参考实现。
- `app/`：新版 IRAC 项目骨架，计划拆分为聊天入口、法律条文检索、民事案件判断、刑事案件判断等子图，目前仍处于开发中。

> 说明：新版 `irac` 还没有补完，本次整理只做项目归档和文档包装，不扩展未完成的终版功能。

## 项目结构

```text
.
├── main.py                         # 新版命令行入口，仍在开发中
├── app/
│   ├── graph.py                    # 新版主图
│   ├── agents/                     # 通用 Agent
│   ├── subgraphs/
│   │   ├── criminal_case/          # 新版刑事案件判断子图，未完成
│   │   ├── civil_case/             # 新版民事案件判断子图，未完成
│   │   └── legal_clause/           # 法律条文检索子图，未完成
│   └── utils/
├── legacy_criminal_case/           # 初版，可作为刑事案件判断部分参考
├── scripts/                        # 向量库构建脚本
├── data/                           # 示例资料
├── vector_store/                   # 本地向量库目录
└── requirements.txt
```

## 初版：刑事案件判断

初版位于 `legacy_criminal_case/`，核心文件是：

- `counselor-agent.py`：按 IRAC 流程串联 Issue、Rule、Application、Conclusion 四个节点
- `prompts.py`：刑事案件判断相关提示词和示例案情
- `法律顾问.ipynb`：Notebook 学习记录

运行方式见 [legacy_criminal_case/README.md](legacy_criminal_case/README.md)。

## 新版状态

新版目录 `app/` 目前是未完成版本，目标是把法律顾问拆成更清晰的模块：

- 通用聊天 Agent
- 法律条文检索
- 刑事案件判断
- 民事案件判断
- 主图路由与状态管理

这些功能还在建设中，因此 GitHub 展示时建议把 `legacy_criminal_case/` 作为当前可说明的完整模块，把新版 `app/` 标注为后续重构方向。

## 环境变量

顶层 `.env` 不应提交到 GitHub。可以参考各子目录的 `.env.example` 填写模型服务配置。

## 免责声明

本项目仅用于 Agent 和法律推理流程学习，不构成法律意见，也不能替代律师、司法机关或专业法律服务。
