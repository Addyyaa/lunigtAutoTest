# Lunight App 自动化测试项目

本项目用于基于 Appium + Pytest + Allure 的移动应用自动化测试框架搭建与示例。

## 功能特性

- 基于 Page Object 的用例结构，SRP/DRY/KISS 原则
- Pytest 夹具统一管理驱动、截图、日志与 Allure 附件
- 覆盖率统计与阈值（默认 80%）
- 代码质量工具：Black/Isort/Ruff/Pylint 与 Pre-commit
- 多环境/多平台（Android/iOS）能力配置示例

## 环境要求

- Python 3.9+
- Appium Server（建议 Appium 2.x）
- Android/iOS SDK & 模拟器或真机（按需）

## 快速开始

```bash
# 1) 创建并激活虚拟环境（Windows PowerShell）
python -m venv .venv
.venv\\Scripts\\Activate.ps1

# 2) 安装依赖
pip install -U pip
pip install -r requirements.txt

# 3) 启动 Appium Server（示例）
# appium --allow-cors

# 4) 运行单元测试（不依赖真机），查看覆盖率
pytest -m "not e2e"

# 5) 运行 e2e 示例（需要设备与对应 capabilities）
pytest -m e2e --alluredir=allure-results

# 6) 生成并查看 Allure 报告
allure serve allure-results
```

## 目录结构

```
.
├── src/
│   ├── core/
│   │   ├── config.py
│   │   ├── driver_factory.py
│   │   └── logger.py
│   ├── page_objects/
│   │   ├── base_page.py
│   │   └── sample_page.py
│   └── utils/
│       └── path.py
├── resources/
│   └── capabilities/
│       ├── android.json
│       └── ios.json
├── tests/
│   ├── unit/
│   │   ├── test_config.py
│   │   └── test_logger.py
│   └── e2e/
│       └── test_sample_app.py
├── .gitignore
├── .pylintrc
├── .pre-commit-config.yaml
├── pyproject.toml
├── pytest.ini
├── requirements.txt
├── the.md
└── README.md
```

## 代码规范与质量

- 统一使用 Black/Isort/Ruff/Pylint；提交前通过 Pre-commit 自动检查
- Pytest + pytest-cov 统计覆盖率，默认阈值 80%
- 遵循 SOLID 原则，模块单一职责，避免全局变量

## Allure 使用

- 失败时自动附加截图/page source/log 到 Allure
- 报告输出目录：`allure-results/`，可用 `allure serve` 本地预览

## 常见问题

- 设备/会话创建失败：检查 Appium 地址、capabilities、设备可用性
- 覆盖率未达标：先运行 `pytest -m "not e2e"`，完善单元测试

## 许可证

MIT（按需调整）

---

## 文件与目录说明（逐一说明）

- `src/`: 测试框架源码目录，遵循单一职责与模块化拆分。
  - `src/__init__.py`: 将 `src` 作为可导入包的标识。
  - `src/core/`: 核心能力模块（配置、驱动、日志）。
    - `config.py`: 配置加载器。优先级为 环境变量 > `.env` > 默认值/资源文件；解析 `resources/capabilities/*.json`，并根据 `DEVICE_PROFILE` 选择 profile，提供 `get_config()` 获取 `AppiumConfig` 与 `load_capabilities()`。
    - `driver_factory.py`: Appium Driver 工厂。基于服务器地址与 capabilities 构建 `webdriver.Remote`，统一生命周期管理（`create()`/`quit()`）。
    - `logger.py`: 日志模块。配置控制台与滚动文件输出（`logs/tests.log`），统一格式与等级。
  - `src/page_objects/`: Page Object 模块，承载页面与组件的交互封装。
    - `base_page.py`: 基础 Page 封装，提供 `find/click/type/wait_visible` 等常用方法与显式等待。
    - `sample_page.py`: 示例页面对象，演示元素定位与操作（如 `tap_ok()`）。
  - `src/utils/`: 通用工具模块。
    - `path.py`: 路径工具，集中管理项目根目录与资源目录定位。

- `resources/`: 测试所需的静态资源与配置。
  - `resources/capabilities/`: Appium 能力配置（JSON）。
    - `android.json`: Android 设备/模拟器的 capabilities，包含 `default` 与 `ci` 两个 profile 示例。
    - `ios.json`: iOS 设备/模拟器的 capabilities，包含 `default` 与 `ci` 两个 profile 示例。

- `tests/`: 测试用例与 Pytest 配置辅助。
  - `tests/__init__.py`: 使 `tests` 成为包（部分工具解析更稳定）。
  - `tests/conftest.py`: 全局夹具与钩子。
    - `config` 夹具：提供已解析的配置对象。
    - `appium_driver` 夹具：基于工厂创建与销毁 Appium 会话。
    - 失败钩子：用例失败时自动附加截图与 `page_source` 到 Allure。
  - `tests/unit/`: 单元测试目录。
    - `test_config.py`: 校验配置解析与 capabilities 文件存在性。
    - `test_logger.py`: 校验日志模块幂等化（重复获取同名 logger 不新增 handler）。
  - `tests/e2e/`: 端到端测试目录。
    - `test_sample_app.py`: 占位示例（带 `@pytest.mark.e2e` 与 `skip`），演示 Page 使用方式。

- 根目录配置与文档：
  - `.gitignore`: Git 忽略规则，包含 Python/IDE/报告/缓存目录等。
  - `requirements.txt`: 运行与质量工具依赖清单（Appium、pytest、allure、pylint、black、isort、ruff、mypy、pre-commit 等）。
  - `pytest.ini`: Pytest 配置（标记、日志、覆盖率阈值、Allure 输出目录等）。
  - `pyproject.toml`: 统一工具配置（Black/Isort/Ruff/Mypy/Pylint），对齐行宽与规则集。
  - `.pylintrc`: Pylint 基础配置，与 `pyproject.toml` 配合约束检查项。
  - `.pre-commit-config.yaml`: 预提交钩子（Ruff/Black/Isort/Pylint）统一风格与静态检查。
  - `the.md`: 工程说明与约定（架构/质量/测试规范/变更记录/Bug 复盘模板）。
  - `README.md`: 使用指南与总体说明（安装、运行、目录、说明）。
  - `.env`（可选，未提交）：环境变量文件。常用键：
    - `PLATFORM_NAME`：`Android` 或 `iOS`
    - `APPIUM_SERVER_URL`：如 `http://127.0.0.1:4723`
    - `DEVICE_PROFILE`：`default`/`ci`，选择 capabilities 中的 profile

- 运行时/生成目录（自动产生或建议保留）：
  - `logs/`: 日志输出目录（滚动日志 `tests.log`）。
  - `allure-results/`: Allure 原始结果（由 pytest 运行生成）。
  - `allure-report/`: Allure 可视化报告（由 `allure generate/serve` 生成）。
  - `reports/`: 可选的自定义报表目录（若有二次封装）。

### 说明与扩展建议

- 当页面/组件增多时，在 `src/page_objects/` 下继续以单文件单页面的方式扩展，保持 SRP 与可维护性。
- 跨页面的公共交互或装饰行为，优先放入 `BasePage` 或新增工具模块（遵循 DRY）。
- 对于不同设备/环境，新增 capabilities profile（如 `staging`、`prod`），通过 `DEVICE_PROFILE` 切换。
- 若需要并发或多设备执行，可在 `pytest` 命令中结合 `-n`（pytest-xdist）与参数化 capabilities（后续可扩展）。
