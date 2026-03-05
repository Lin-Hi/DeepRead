# State Tracker 设计文档

**版本**: 1.0
**日期**: 2026-03-04
**状态**: 已确认

---

## 概述

State Tracker 负责管理 DeepRead 的处理状态，实现增量更新和断点续传功能。

---

## state.json 结构设计

### 完整 Schema

```json
{
  "version": "1.0",
  "last_updated": "2026-03-04T14:30:00Z",
  "files": {
    "FULLTEXT01.pdf": {
      "hash": "sha256:abc123...def456",
      "processed_at": "2026-03-04T14:30:00Z",
      "title": "Analyzing common structures in Enterprise Architecture modeling notations",
      "folder_name": "2022-Hussein-AnalyzingCommonStructuresEnterprise",
      "outputs": [
        "01-Literature/2022-Hussein-AnalyzingCommonStructuresEnterprise/2022-Hussein-AnalyzingCommonStructuresEnterprise.md",
        "01-Literature/2022-Hussein-AnalyzingCommonStructuresEnterprise/Summary.md",
        "01-Literature/2022-Hussein-AnalyzingCommonStructuresEnterprise/2022-Hussein-AnalyzingCommonStructuresEnterprise.canvas"
      ],
      "status": "completed",
      "error": null,
      "retry_count": 0
    }
  },
  "unnamed_counter": 3,
  "statistics": {
    "total_processed": 10,
    "successful": 8,
    "failed": 2,
    "last_batch_id": "batch_20260304_143000"
  }
}
```

### 字段说明

#### 根级别字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `version` | string | state.json 格式版本号 |
| `last_updated` | ISO8601 | 最后更新时间戳 |
| `files` | object | 文件记录字典，key 为原始 PDF 文件名 |
| `unnamed_counter` | integer | UNNAMED 编号计数器（全局递增） |
| `statistics` | object | 处理统计信息 |

#### 文件记录字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `hash` | string | 是 | SHA256 文件哈希 |
| `processed_at` | ISO8601 | 是 | 处理完成时间 |
| `title` | string | 否 | 提取的论文标题 |
| `folder_name` | string | 是 | 生成的文件夹名称 |
| `outputs` | array | 是 | 输出文件路径列表 |
| `status` | enum | 是 | 处理状态：pending/processing/completed/failed/skipped |
| `error` | string/null | 否 | 错误信息（失败时） |
| `retry_count` | integer | 否 | 重试次数 |

---

## 增量更新逻辑

### 处理流程

```
扫描 input-pdfs/
    │
    ▼
计算每个文件的 SHA256 hash
    │
    ▼
对比 state.json:
    ├─ hash 匹配 → 跳过 (除非 --force)
    ├─ hash 不匹配 → 重新处理
    └─ 无记录 → 新文件，处理
    │
    ▼
处理完成后更新 state.json (原子写入)
```

### 核心算法

```python
def should_process(pdf_path: Path, state: dict) -> bool:
    """判断是否需要处理文件"""
    file_hash = calculate_sha256(pdf_path)
    filename = pdf_path.name

    # 检查 state 中是否存在
    if filename not in state["files"]:
        return True

    record = state["files"][filename]

    # 检查 hash 是否变化
    if record.get("hash") != file_hash:
        return True

    # 检查输出文件是否存在
    for output_path in record.get("outputs", []):
        if not Path(output_path).exists():
            return True

    return False
```

---

## 原子写入机制

为了防止程序崩溃导致 state.json 损坏，使用原子写入模式：

```python
import tempfile
import shutil
from pathlib import Path
import json

def save_state_atomic(state_path: Path, data: dict):
    """原子写入 state.json，避免崩溃导致文件损坏"""
    # 写入临时文件
    temp_path = state_path.with_suffix('.tmp')
    with open(temp_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # 原子移动到目标位置
    shutil.move(str(temp_path), str(state_path))
```

---

## UNNAMED 编号管理

### 规则

1. **全局递增**: `unnamed_counter` 只增不减
2. **不回收编号**: 删除文件后编号不重用，避免冲突
3. **格式**: `UNNAMED_[year]_[num]` 或 `UNNAMED_[num]`

### 分配算法

```python
def get_unnamed_folder(state: dict, year: str = None) -> str:
    """获取新的 UNNAMED 文件夹名"""
    counter = state["unnamed_counter"] + 1
    state["unnamed_counter"] = counter

    if year:
        return f"UNNAMED_{year}_{counter:03d}"
    else:
        return f"UNNAMED_{counter:03d}"
```

---

## 错误处理与恢复

### 状态转换图

```
[pending] ──开始处理──► [processing] ──成功──► [completed]
                              │
                              └──失败──► [failed] ──重试──► [processing]
                              │
                              └──跳过──► [skipped]
```

### 损坏恢复

```python
def load_state_with_recovery(state_path: Path) -> dict:
    """加载 state.json，支持损坏恢复"""
    try:
        with open(state_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        # 备份损坏的文件
        if state_path.exists():
            backup_path = state_path.with_suffix('.json.bak')
            shutil.copy(str(state_path), str(backup_path))
            logger.warning(f"state.json 损坏，已备份到 {backup_path}")

        # 返回空状态
        return {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "files": {},
            "unnamed_counter": 0,
            "statistics": {"total_processed": 0, "successful": 0, "failed": 0}
        }
```

---

## 性能优化

### 建议

1. **延迟写入**: 批量处理时，每 N 个文件写入一次 state.json
2. **内存缓存**: 将 state 保存在内存中，减少磁盘 I/O
3. **压缩选项**: 大量文件时可考虑压缩存储（未来版本）

---

## API 接口设计

### StateTracker 类

```python
class StateTracker:
    def __init__(self, state_path: Path):
        self.state_path = state_path
        self._data = self._load()

    def _load(self) -> dict:
        """加载状态文件"""
        pass

    def save(self):
        """原子保存状态"""
        pass

    def get_file_record(self, filename: str) -> Optional[dict]:
        """获取文件记录"""
        pass

    def update_file_record(self, filename: str, record: dict):
        """更新文件记录"""
        pass

    def should_process(self, pdf_path: Path, force: bool = False) -> bool:
        """判断是否需要处理"""
        pass

    def get_next_unnamed_counter(self) -> int:
        """获取下一个 UNNAMED 编号"""
        pass

    def get_statistics(self) -> dict:
        """获取处理统计"""
        pass
```

---

## 验证清单

- [x] JSON Schema 定义清晰
- [x] 原子写入机制设计完成
- [x] 增量更新逻辑确认
- [x] UNNAMED 编号策略确定
- [x] 错误恢复机制设计完成
- [ ] 单元测试覆盖 (Phase 4 执行)
- [ ] 性能基准测试 (Phase 4 执行)
