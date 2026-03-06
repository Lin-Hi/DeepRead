# 20260306 - PDF 处理工作流智能化改进 Plan

## 背景与问题

当前 `_convert_with_marker()` 以完全黑盒的方式调用 `marker_single`：用 `subprocess.run` 阻塞等待，用户看不到任何进度，也无法确认 GPU 是否被使用。

此外，Marker 已内置 pdftext + Surya OCR 的自动路由，但我们未将预扫描结果（`has_text_layer`）传递给它，可能在纯文字 PDF 上触发了不必要的完整 OCR 流程。

---

## 改进目标

### A. 预扫描智能路由（Token 经济学）
- 利用已有的 `has_text_layer` 字段，在调用 Marker 时传入 `--page_range` 或跳过 Surya 全量扫描的标志
- 通过 Marker 参数或环境变量，让纯文字 PDF 跳过 OCR 模型加载

### B. 实时步骤进度 + 计时器
- 将 `subprocess.run` → `subprocess.Popen` 流式读取 stdout/stderr
- 在 `main.py` / `pdf_processor.py` 各关键步骤前后打印带时间戳和耗时的状态行
- 格式示例：`[1/4] 预扫描 PDF...  ✓ 完成 (0.3s)`

### C. 设备信息提示
- 在 Marker 调用前打印当前使用 CPU/GPU 的提示
- 格式：`[PDF→MD] 使用设备: CUDA (NVIDIA RTX 4070 Laptop GPU)`

---

## 设计决策与约束

### 关于 Marker 的"预扫描路由"边界

> [!IMPORTANT]
> Marker 本身已内部实现 pdftext → Surya OCR 自动路由，无需我们重新实现。
> 我们的优化点是：
> 1. 当 `has_text_layer=True` 时传入 `--disable_ocr` 参数（如 Marker 支持），跳过 Surya 模型加载
> 2. 当 `has_text_layer=False` 时不做任何限制，让 Marker 全力运行 OCR
> 
> **不要**在 Python 层自行实现 pdftext/Surya 调用，避免产生与 Marker 的冲突和重复维护负担。

### 关于实时输出

Marker subprocess 的进度信息通过 stderr 输出（tqdm 进度条）。改用 `Popen` + `iter(proc.stderr.readline, '')` 实时读取并格式化输出。

---

## 修改范围

### `src/pdf_processor.py`

#### `_convert_with_marker()`
- [ ] 在调用前打印设备信息（CUDA / CPU）
- [ ] 检查 `has_text_layer` → 对纯文字 PDF 追加 `--disable_ocr` 参数（需先验证 Marker 是否支持此参数）
- [ ] 将 `subprocess.run` 改为 `subprocess.Popen` 流式输出
- [ ] 解析 stderr 并以格式化方式重新打印关键行（过滤噪音）

#### `process()`
- [ ] 在各子步骤前后记录时间并打印耗时

### `src/main.py`

#### `process_single_pdf()`
- [ ] 增加整体步骤进度展示（步骤 N/M 的外层框架）
- [ ] 各步骤完成时打印 `✓ 完成 (Xs)`

---

## 验证计划

1. 对 `3510611.pdf`（有文字层）运行，确认控制台实时输出步骤进度 + GPU 提示
2. 对 `input-pdfs/edge-cases/` 中的扫描版 PDF（无文字层）运行，确认走 OCR 路径
3. 全量 pytest 通过（核心逻辑测试不受影响）

---

## 待确认技术细节（需执行前验证）

- [ ] 确认 `marker_single --help` 中是否存在 `--disable_ocr` 或等效参数
- [ ] 确认 Marker stderr 输出的具体格式，以便精确过滤

## Checklist

- [ ] 验证 Marker 是否支持 `--disable_ocr`
- [ ] 修改 `_convert_with_marker()`：设备提示 + Popen 流式输出
- [ ] 修改 `process()`：步骤计时器
- [ ] 修改 `main.py`：外层步骤进度框架
- [ ] 全量测试通过
- [ ] 分形文档回环（L3 文件头 + src/CLAUDE.md）
