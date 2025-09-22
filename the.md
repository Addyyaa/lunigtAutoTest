# 项目修改说明（the.md）

在对项目进行任何修改前，请阅读本文件，确保遵循以下约定与规则：

## 设计与工程约束

- 架构：Appium + Pytest + Allure，采用 Page Object 模式；业务逻辑与测试逻辑解耦。
- 原则：SRP/DRY/KISS、组合优于继承、SOLID、渐进式披露（按需加载模块）。
- 质量：启用 Black/Isort/Ruff/Pylint，测试覆盖率≥80%（`pytest.ini` 已设阈值）。
- 目录：模块化与组件化，避免巨型文件；单文件超 3000 行前先做模块拆分设计。
- 异常：精确捕获，记录日志，提供可读的报错与排错线索。
- 配置：避免硬编码，统一走 `resources/capabilities/*.json` 与环境变量覆盖。

## 测试规范

- 单元测试：放在 `tests/unit/`，优先覆盖 `src/core` 与通用工具。
- E2E 测试：放在 `tests/e2e/`，均加 `@pytest.mark.e2e` 标记；在 CI 中可选择性执行。
- 报告：Allure 结果输出至 `allure-results/`，CI 中归档并生成报告页面。

## Bug 复盘模板（请复制使用）

- Bug 现象：
- 触发路径：
- 根因分析：
- 修复方案：
- 回归验证：

## 变更记录

- 使用中文撰写提交说明；为公共 API/类/方法补充 docstring。
