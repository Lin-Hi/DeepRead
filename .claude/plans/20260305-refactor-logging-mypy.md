# 20260305: 日志增强与类型审查重构计划 (Refactor Logging & Mypy)

## 目标
为项目搭建独立的日志流转存储中心（改进提案 B），并构建覆盖全局项目的严格 Mypy 类型保障屏障（改进提案 C）。由此提高系统的运行可观测性，以及长期避免出现 Python 的运行时“类型暗坑”。

## Checklist

### 改进提案 B：增强 Logging 日志落盘封装
- [ ] **1. 创建独立日志基础设施**
  - 在 `src/` 下创建独立的 `logger.py` 单例或功能模块。
  - 使用标准的 `logging` 模块配合 `logging.handlers.TimedRotatingFileHandler`（按天产生切割滚动日志）。
  - 设置**终端控制台**（StreamHandler）为 `INFO` 级别，输出简洁格式。
  - 设置**实体文件**（FileHandler）为 `DEBUG` 级别，输出极其详尽的时间刺与线程格式。
  - 规定日志文件自动存放及归档于项目根目录 `logs/deepread_YYYY-MM-DD.log`。

- [ ] **2. 项目配置联动**
  - 于 `src/config.py` 中补充相关路径定义 `log_dir: Path`，并在启动时保证依赖路径有效创建。

- [ ] **3. 替换全项目代码打印流**
  - 全局移除目前存在于 `main.py` 开头的原始 `logging.basicConfig(...)`。
  - 搜索并替换散落在 `state_tracker.py`、`pdf_processor.py` 等各个核心模块中的原始 `logger` 或 `print`，要求统一从 `src.logger` 引用。

### 改进提案 C：执行严格的 Mypy 静态类型审查
- [ ] **1. 配置 Mypy 全局策略红线**
  - 在根目录定义配置文件 `mypy.ini`。
  - 开启一系列严格约束，如 `disallow_untyped_defs = True`（全部函数必须带标注）以及第三方未知依赖使用 `ignore_missing_imports = True` 避开误报。

- [ ] **2. 修补代码库历史“裸奔”函数**
  - 跑通 `mypy src/`，排查终端控制台出现的红色异常。
  - 针对每一个错误，为对应函数的 `args` 及 `return` 加上强类型的 `typing` 注释。
  - 对于从 `JSON`、`LLM Regex` 或者动态解析字典读取来的 `dict` 或 `Any` 变量作安全的强制转型与验证处理，避免推导崩溃危险。

- [ ] **3. 文档登记**
  - 将 `mypy` 这个库加入 `requirements.txt`。

## 验收条件 (Verification)
1. 运行工具流以后，`logs/` 下能平稳写入详尽带时间的 debug 错误日志。
2. 终端执行 `mypy src/ --config-file mypy.ini` 必须反馈纯净的 `Success: no issues found in xx source files`。
