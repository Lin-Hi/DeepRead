# Marker 基准测试报告

**测试日期**: 2026-03-04
**测试环境**: Windows 11, Python 3.10.14 (Conda PY_3_10)
**Marker 版本**: 1.10.2
**Surya OCR 版本**: 0.17.1

---

## 测试概述

本次测试使用 marker-pdf 对学术论文 PDF 进行 Markdown 转换，验证其在 CPU 模式下的处理效果和性能。

### 测试文件

| 文件名 | 大小 | 类型 |
|--------|------|------|
| FULLTEXT01.pdf | 1.9 MB | KTH 硕士论文（双栏排版） |
| FULLTEXT01 (1).pdf | 1.0 MB | 学术论文 |

---

## 测试结果

### FULLTEXT01.pdf

#### 基本信息
- **文档标题**: Analyzing common structures in Enterprise Architecture modeling notations
- **作者**: Ahmed Hussein
- **页数**: 约 70+ 页
- **排版**: 双栏学术格式

#### 处理结果

| 指标 | 结果 |
|------|------|
| 处理时间 | ~10-15 秒 |
| 输出格式 | Markdown + 图片 + JSON 元数据 |
| Markdown 大小 | 150 KB |
| 提取图片数量 | 13 张 |

#### 内容质量评估

✅ **成功提取的内容**:
- 文档标题和作者信息
- 完整摘要（英文 + 瑞典语 Sammanfattning）
- 目录结构（转换为 Markdown 表格格式）
- 关键词
- 致谢部分
- 章节标题层级

✅ **表格处理**:
- 目录被正确识别并转换为 Markdown 表格格式
```markdown
| 1 |     | Introduction<br>1                                |
|---|-----|--------------------------------------------------|
|   | 1.1 | Background<br><br>1                              |
```

✅ **图片提取**:
- 共提取 13 张图片
- 命名格式: `_page_[页码]_Figure_[编号].jpeg`
- 示例: `_page_24_Figure_1.jpeg`, `_page_45_Figure_3.jpeg`

⚠️ **需要注意的问题**:
1. **标题重复**: 首页标题出现两次（可能来自封面和内页）
2. **页眉页脚**: 部分页眉如 "iv | Sammanfattning" 被保留
3. **换行符**: `<br>` 标签出现在表格中

#### 元数据文件 (FULLTEXT01_meta.json)

包含以下结构化信息：
- `table_of_contents`: 详细的目录条目，包含页码和边界框坐标
- `page_info`: 每页的详细信息
- `image_metadata`: 图片的位置和尺寸信息

---

## 技术验证结论

### ✅ 通过的测试项

1. **PDF 解析能力**
   - [x] 双栏排版正确处理
   - [x] 多语言内容支持（英文 + 瑞典语）
   - [x] 复杂文档结构识别

2. **内容提取质量**
   - [x] 标题和元数据提取准确
   - [x] 摘要完整保留
   - [x] 目录结构正确转换

3. **图片提取**
   - [x] 自动识别并提取图片
   - [x] 合理的文件命名格式

4. **性能表现**
   - [x] CPU 模式下 70 页论文约 10-15 秒完成
   - [x] 符合 <10 分钟阈值要求

### ⚠️ 需要关注的问题

1. **LaTeX 公式**: 本测试文件未包含数学公式，需额外验证
2. **复杂表格**: 目录表格处理良好，但数据表格需进一步测试
3. **OCR 准确性**: 当前为数字原生 PDF，扫描版 PDF 的 OCR 效果待验证

---

## 建议配置

基于测试结果，推荐以下 Marker 配置参数：

```python
{
    "output_format": "markdown",
    "disable_image_extraction": False,
    "highres_image_dpi": 192,  # 默认值，适合屏幕显示
    "lowres_image_dpi": 96,    # 布局检测用
}
```

---

## 下一步行动

1. **扩展测试集**: 增加包含公式、表格、图表的 PDF 样本
2. **OCR 测试**: 测试扫描版 PDF 的识别准确率
3. **集成开发**: 将 Marker 调用封装到 `pdf_processor.py` 模块

---

## 参考

- [Marker GitHub](https://github.com/VikParuchuri/marker)
- [Surya OCR](https://github.com/VikParuchuri/surya)
