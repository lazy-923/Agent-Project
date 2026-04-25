# IRAC 法律顾问智能体

这是一个基于 IRAC（Issue、Rule、Application、Conclusion）法律分析框架的 Agent 学习项目。当前目录包含两个阶段：

- `legacy_criminal_case/`：早期初版法律顾问智能体，作为“刑事案件判断”部分的完整参考实现。
- `app/`：新版 IRAC 项目骨架，计划拆分为聊天入口、法律条文检索、民事案件判断、刑事案件判断等子图，目前仍处于开发中。

本次整理只做项目归档和文档包装，不继续补完新版终版功能。

## 项目结构

```text
.
├── main.py                         # 新版命令行入口，仍在开发中
├── app/
│   ├── graph.py                    # 新版主图
│   ├── state.py                    # 新版状态定义
│   ├── agents/                     # 通用 Agent
│   ├── subgraphs/
│   │   ├── criminal_case/          # 新版刑事案件判断子图，未完成
│   │   ├── civil_case/             # 新版民事案件判断子图，未完成
│   │   └── legal_clause/           # 法律条文检索子图，未完成
│   └── utils/
├── legacy_criminal_case/           # 初版，作为刑事案件判断参考实现
├── scripts/                        # 向量库构建脚本
├── data/                           # 示例资料
├── vector_store/                   # 本地向量库目录
└── requirements.txt
```

## 当前可展示版本

当前最适合展示的是 `legacy_criminal_case/`，它按 IRAC 流程串联四个阶段：

```text
案件事实
  -> Issue：识别法律议题
  -> Rule：整理相关法律规则
  -> Application：将规则适用于案件事实
  -> Conclusion：形成判断结论
```

运行和说明见：

[legacy_criminal_case/README.md](legacy_criminal_case/README.md)

## 新版规划

新版 `app/` 的目标是把法律顾问拆成更清晰的模块：

- 通用聊天 Agent
- 法律条文检索
- 刑事案件判断
- 民事案件判断
- 主图路由与状态管理

这些功能还在建设中，因此 GitHub 展示时建议把 `legacy_criminal_case/` 标注为当前完整模块，把新版 `app/` 标注为后续重构方向。

## 环境变量

顶层 `.env` 不应提交到 GitHub。运行前请参考对应目录下的 `.env.example` 填写模型服务配置。

## 免责声明

本项目仅用于 Agent 和法律推理流程学习，不构成法律意见，也不能替代律师、司法机关或专业法律服务。
