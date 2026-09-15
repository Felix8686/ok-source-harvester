# ok-source-harvester

自动发现、验证、去重、评分并输出公开分享的 OK影视 / TVBox 配置源。

## 当前状态

Phase 0：工程骨架与架构边界。当前版本**不会进行大规模网络采集，也不提交真实影视源数据**。

## 设计目标

- 自动发现公开分享的候选配置地址。
- 对同一 URL 去重，同时保留多个发现来源。
- 保留完整验证历史，而不是只保留最后状态。
- 通过可扩展 Collector / Validator 接口逐步加入 GitHub、网页、Telegram 等来源和深度验证能力。
- 第一版使用 SQLite，存储层通过 Repository 边界隔离，未来可迁移 PostgreSQL。

## 开发

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"
ruff check .
mypy src
pytest
```

配置项见 `.env.example`。所有敏感信息只通过环境变量读取。

架构和路线图见 `docs/ARCHITECTURE.md` 与 `docs/ROADMAP.md`。
