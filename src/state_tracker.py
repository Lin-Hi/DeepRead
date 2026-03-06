"""
/**
 * [IN]: config.settings, hashlib, json, shutil, pathlib
 * [OUT]: StateTracker 类 - 管理 .deepread/state.json 的读写和增量更新逻辑
 * [POS]: 被 main.py 调用，在 PDF 处理前后更新状态
 * [PROTOCOL]: 修改状态结构 -> 同步更新文档和版本号
 */
"""
import json
import hashlib
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import Any, Optional
from dataclasses import dataclass, field, asdict

from src.config import settings


@dataclass
class FileState:
    """单个文件的处理状态"""
    hash: str
    processed_at: str
    title: str
    folder_name: str
    outputs: list[str] = field(default_factory=list)
    status: str = "completed"  # completed, failed, processing
    error_message: Optional[str] = None


class StateTracker:
    """
    状态追踪器

    管理 .deepread/state.json 文件，支持：
    - 文件 hash 计算和比对
    - 增量更新检测
    - UNNAMED 编号管理
    - 原子写入（防止崩溃损坏）
    """

    def __init__(self, state_dir: Path = settings.state_path) -> None:
        self.state_file = state_dir / "state.json"
        self._state: dict = {}
        self._load()

    def _load(self) -> None:
        """加载 state.json 文件"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    self._state = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Failed to load state file: {e}")
                print("Creating new state file...")
                self._state = self._create_default_state()
        else:
            self._state = self._create_default_state()

    def _create_default_state(self) -> dict:
        """创建默认状态结构"""
        return {
            "version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "files": {},
            "unnamed_counter": 0
        }

    def _save_atomic(self) -> None:
        """原子写入 state.json"""
        self._state["last_updated"] = datetime.now().isoformat()

        # 创建临时文件
        temp_file = self.state_file.with_suffix('.tmp')
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self._state, f, indent=2, ensure_ascii=False)

            # 原子移动
            shutil.move(str(temp_file), str(self.state_file))
        except Exception as e:
            if temp_file.exists():
                temp_file.unlink()
            raise IOError(f"Failed to save state: {e}")

    @staticmethod
    def compute_hash(file_path: Path) -> str:
        """
        计算文件的 SHA256 hash

        Args:
            file_path: PDF 文件路径

        Returns:
            sha256:hash_string 格式的 hash 值
        """
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return f"sha256:{sha256.hexdigest()}"

    def get_next_unnamed_number(self) -> int:
        """获取下一个 UNNAMED 编号并递增计数器"""
        current = int(str(self._state.get("unnamed_counter", 0)))
        self._state["unnamed_counter"] = current + 1
        self._save_atomic()
        return current + 1

    def is_processed(self, pdf_path: Path) -> bool:
        """
        检查文件是否已处理且未变更

        Args:
            pdf_path: PDF 文件路径

        Returns:
            True 如果文件已处理且 hash 匹配
        """
        filename = pdf_path.name

        if filename not in self._state["files"]:
            return False

        file_state = self._state["files"][filename]

        # 检查输出文件是否存在
        outputs = file_state.get("outputs", [])
        missing_outputs = [f for f in outputs if not Path(f).exists()]

        if missing_outputs:
            print(f"  Output files missing: {missing_outputs}")
            return False

        # 检查 hash 是否匹配
        current_hash = self.compute_hash(pdf_path)
        if file_state.get("hash") != current_hash:
            print(f"  File changed (hash mismatch)")
            return False

        return True

    def get_file_state(self, pdf_path: Path) -> Optional[FileState]:
        """获取文件的处理状态"""
        filename = pdf_path.name
        if filename not in self._state["files"]:
            return None

        data = self._state["files"][filename]
        return FileState(**data)

    def update_file_state(
        self,
        pdf_path: Path,
        title: str,
        folder_name: str,
        outputs: list[str],
        status: str = "completed",
        error_message: Optional[str] = None
    ) -> None:
        """
        更新文件处理状态

        Args:
            pdf_path: PDF 文件路径
            title: 论文标题
            folder_name: 生成的文件夹名
            outputs: 输出文件路径列表
            status: 处理状态
            error_message: 错误信息（如果有）
        """
        filename = pdf_path.name
        file_hash = self.compute_hash(pdf_path)

        self._state["files"][filename] = {
            "hash": file_hash,
            "processed_at": int(datetime.now().timestamp()),
            "title": title,
            "folder_name": folder_name,
            "outputs": outputs,
            "status": status,
            "error_message": error_message
        }

        self._save_atomic()

    def remove_file_state(self, pdf_path: Path) -> None:
        """删除文件状态记录"""
        filename = pdf_path.name
        if filename in self._state["files"]:
            del self._state["files"][filename]
            self._save_atomic()

    def get_all_processed_files(self) -> list[str]:
        """获取所有已处理的文件名列表"""
        return [
            name for name, data in self._state["files"].items()
            if data.get("status") == "completed"
        ]

    def reset(self) -> None:
        """重置所有状态（谨慎使用）"""
        self._state = self._create_default_state()
        self._save_atomic()

    def get_statistics(self) -> dict:
        """获取处理统计信息"""
        files = self._state["files"]
        total = len(files)
        completed = sum(1 for f in files.values() if f.get("status") == "completed")
        failed = sum(1 for f in files.values() if f.get("status") == "failed")

        return {
            "total_files": total,
            "completed": completed,
            "failed": failed,
            "unnamed_counter": self._state.get("unnamed_counter", 0)
        }
