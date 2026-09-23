# Zhengyang Wang · 王正旸

![Multimodal AI and spatial reasoning](assets/research-header.svg)

Computer Science undergraduate at **BNBU**, working on **multimodal AI, spatial reasoning, and research software**. My projects connect data validation, computer vision, and spatiotemporal modelling. I contribute reproducible fixes and bug reports to AI and agent tooling.

BNBU 计算机本科生，研究与项目涵盖 **多模态 AI、空间推理与科研软件**，结合数据校验、计算机视觉和时空建模经验，为 AI 与 Agent 工具提供可复现的问题报告和修复。

[Website · 个人网站](https://wzhengyang.com) · [Research & projects · 研究与项目](https://wzhengyang.com/projects/)

[Research · 研究](#research) · [Contributions · 贡献](#contributions) · [Case studies · 案例](#case-studies) · [Projects · 项目](#projects)

<a name="research"></a>

## Selected research & systems · 研究与系统

| Project · 项目 | My work · 我的工作 |
| --- | --- |
| **MACH / MetaVision-DB** · 多模态推理 | Co-developed a VLM agent framework for visual metaphor reasoning and communication games; led dataset construction with concept–image alignment, schema validation, and manual review. |
| **MapAgent** · 室内定位与空间推理 | Developed a Qwen3-based localisation agent combining BLE, motion, and map evidence, with independent verification and deterministic fallback. |
| **MetroHeight** · RGB-D 测量 | Developed an iOS app and FastAPI backend, integrating SAM 3 segmentation, gravity-aligned reconstruction, and local RANSAC floor fitting for cargo-height measurement. |
| **ST-Net** · 心脏影像时序分割 | Developed a cine MRI segmentation model with temporal attention and cyclic regularisation of area and centroid trajectories under ED/ES-only supervision. |
| **Environmental modelling** · 环境时空建模 | Developed river-discharge forecasting with hydrological time series and river-network graphs; separately analysed soil-water and satellite vegetation signals for post-fire recovery. |

These projects inform my open-source work on multimodal input handling, data reliability, and agent validation. / 开源选题围绕这些项目中的多模态输入、数据可靠性与 Agent 验证问题展开。

<a name="contributions"></a>

## Open-source contribution · 开源贡献

| Project · 项目 | Contribution · 贡献 | Status · 状态 |
| --- | --- | --- |
| [Hugging Face Datasets](https://github.com/huggingface/datasets) | Fix cross-process locking for long filenames, with regression tests · 修复长文件名的跨进程锁失效并添加回归测试 | [PR #8654](https://github.com/huggingface/datasets/pull/8654) — submitted / 待审 |
| [Hugging Face Datasets](https://github.com/huggingface/datasets) | Fix EXIF orientation when serializing in-memory PIL images, preserving TIFF compatibility · 修复内存图像序列化后的旋转与镜像错误，保持 TIFF 兼容 | [PR #8656](https://github.com/huggingface/datasets/pull/8656) — submitted / 待审 |
| [LlamaIndex](https://github.com/run-llama/llama_index) | Fix Base64 conversion of in-memory image streams for multimodal input · 修复多模态输入中内存图像流的 Base64 转换 | [PR #23159](https://github.com/run-llama/llama_index/pull/23159) — submitted / 待审 |
| [Hugging Face Hub](https://github.com/huggingface/huggingface_hub) | Report and reproduce missing tools in paginated MCP discovery · 报告并复现 MCP 分页工具遗漏 | [Issue #4956](https://github.com/huggingface/huggingface_hub/issues/4956) — resolved by [PR #4960](https://github.com/huggingface/huggingface_hub/pull/4960), authored by Kayvan-Zahiri / 他人修复已合并 |

<a name="case-studies"></a>

Technical case studies · 技术案例：

- [In-memory images and model input encoding · 内存图像与模型输入编码](notes/llamaindex-image-streams.md)
- [Cross-process cache locking · 跨进程缓存锁](notes/datasets-locking.md)
- [MCP tool discovery and pagination · MCP 工具发现与分页](notes/mcp-tool-discovery.md)
- [Tool failures and agent recovery · 工具失败与 Agent 回退](notes/agent-tool-results.md) — review addressed by the PR author; PR unmerged / 审查意见已由 PR 作者修正，尚未合并

### [KuiklyLoadingKit](https://github.com/Yang1107-wzy/KuiklyLoadingKit) — Kotlin Multiplatform

I developed a loading component for [Tencent KuiklyUI's official ecosystem task #1480](https://github.com/Tencent-TDS/KuiklyUI/issues/1480). It provides full-screen and local overlays, loading-state control, timeout cancellation, a declarative DSL, and Android/iOS examples. The component is delivered in its own repository, with [API documentation](https://github.com/Yang1107-wzy/KuiklyLoadingKit/blob/main/docs/API.md) and [validation records](https://github.com/Yang1107-wzy/KuiklyLoadingKit/blob/main/docs/VALIDATION.md).

**External acknowledgment:** a KuiklyUI project collaborator [confirmed task completion on 5 August 2026](https://github.com/Tencent-TDS/KuiklyUI/issues/1480#issuecomment-5192793318).

为腾讯 KuiklyUI 官方生态任务开发跨平台加载组件，提供全屏/局部加载、状态控制、超时取消、声明式 DSL 及 Android/iOS 示例。成果以独立组件仓库交付，已获项目协作者在官方 Issue 中确认完成。

<a name="projects"></a>

## Computer vision · 计算机视觉

### [Archery target and score-region detection](https://github.com/Yang1107-wzy/archery-yolo11s-detection)

A joint project with Jiacheng Yao, using YOLO11s for archery target and score-region detection. The repository includes training logs, checkpoints, evaluation reports, and a Streamlit demo. [Results](https://github.com/Yang1107-wzy/archery-yolo11s-detection/blob/main/RESULTS.md) distinguish validation-based model selection from held-out test evaluation; the [dataset card](https://github.com/Yang1107-wzy/archery-yolo11s-detection/blob/main/DATASET_CARD.md) and [reproduction guide](https://github.com/Yang1107-wzy/archery-yolo11s-detection/blob/main/REPRODUCIBILITY.md) document the evaluation scope.

与 Jiacheng Yao 合作的 YOLO11s 箭靶与分数区域检测项目，公开训练记录、模型、评测报告和演示。验证集模型选择与测试集评估分别记录；预测框中心不等同于真实箭矢落点。

## Selected course projects · 课程项目

These are group projects. The linked repositories describe the methods, available artifacts, and my documented role.

以下均为课程小组项目；各仓库提供方法说明、已有材料和我的具体参与范围。

| Project · 项目 | Focus · 内容 | My role · 我的角色 |
| --- | --- | --- |
| [Blood glucose forecasting · 血糖预测](https://github.com/Yang1107-wzy/neural-networks-glucose-forecasting) | Sequence models for one-hour-ahead prediction · 序列模型与一小时预测 | Team leader; Transformer presentation · 组长、Transformer 展示部分 |
| [Next-day flow mapping · 次日流量分布预测](https://github.com/Yang1107-wzy/machine-learning-grid-flood-forecasting) | Multi-source environmental inputs and a 2D catchment grid · 多源环境输入与二维流域网格 | Group member and report coauthor · 小组成员、报告共同作者 |
| [Bézier CNC path control · Bézier 数控路径](https://github.com/Yang1107-wzy/numerical-computation-cnc-path-control) | Arc-length integration and constant-feed-rate simulation · 弧长积分与恒进给速度仿真 | Group member; adaptive Simpson presentation · 小组成员、自适应 Simpson 展示 |

More course work: [factor regression](https://github.com/Yang1107-wzy/probability-statistics-factor-regression) (Problem 3 analysis / 第 3 题分析) · [Mentor Caring System SRS](https://github.com/Yang1107-wzy/software-engineering-mentor-caring-srs) (one of six specification preparers / 六位需求规格说明编写成员之一).

Course results and reproduction limits are documented in each repository. / 课程结果及复现条件见各仓库说明。

## Engineering practice · 工程实践

[BNBU course assistant](https://github.com/Yang1107-wzy/yang-bnbu-course-assistant) is a source-available Tampermonkey learning project exploring DOM inspection, browser state, and cross-tab coordination. Its license and repository rules restrict it to non-commercial learning and controlled testing.

BNBU 课程助手是源码可见的 Tampermonkey 学习项目，探索 DOM 检查、浏览器状态和跨标签协调；按仓库许可与使用规则，仅用于非商业学习和受控测试。
