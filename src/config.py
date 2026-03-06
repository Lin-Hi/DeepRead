"""
/**
 * [IN]: pydantic-settings, python-dotenv, pathlib
 * [OUT]: Settings 类 - 项目全局配置管理
 * [POS]: 被所有模块消费，在 main.py 中初始化
 * [PROTOCOL]: 修改配置项 -> 同步更新 .env.example 文档
 */
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    """
    DeepRead 项目配置类

    配置优先级（从高到低）：
    1. 环境变量
    2. .env 文件
    3. 默认值
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # 忽略未定义的环境变量
    )

    # ========== API 配置 ==========
    api_base_url: str = ""  # 必填，从 .env 读取 (API_BASE_URL)
    api_key: str = ""       # 必填，从 .env 读取 (API_KEY)
    model: str = ""         # 必填，从 .env 读取 (MODEL)

    # ========== 路径配置 ==========
    input_dir: str = "input-pdfs"
    output_dir: str = "01-Literature"
    knowledge_map_dir: str = "00-KnowledgeMap"
    state_dir: str = ".deepread"
    log_dir: str = "logs"
    reports_dir: str = "reports"

    # ========== 处理配置 ==========
    max_retries: int = 3
    batch_size: int = 10
    timeout_seconds: int = 300

    # ========== 日志配置 ==========
    log_level: str = "INFO"

    # ========== Canvas 配置 ==========
    canvas_node_width: int = 300
    canvas_node_height: int = 200
    canvas_node_spacing_x: int = 350  # 水平间距
    canvas_node_spacing_y: int = 250  # 垂直间距

    # ========== 文件名配置 ==========
    max_filename_length: int = 100
    max_title_slug_words: int = 5

    @property
    def root_dir(self) -> Path:
        """项目根目录"""
        return Path(__file__).parent.parent

    @property
    def input_path(self) -> Path:
        """PDF 输入目录"""
        return self.root_dir / self.input_dir

    @property
    def output_path(self) -> Path:
        """文献输出目录"""
        return self.root_dir / self.output_dir

    @property
    def knowledge_map_path(self) -> Path:
        """总图谱目录"""
        return self.root_dir / self.knowledge_map_dir

    @property
    def state_path(self) -> Path:
        """状态文件目录"""
        return self.root_dir / self.state_dir

    @property
    def state_file(self) -> Path:
        """state.json 完整路径"""
        return self.state_path / "state.json"

    @property
    def log_path(self) -> Path:
        """日志目录"""
        return self.root_dir / self.log_dir

    @property
    def reports_path(self) -> Path:
        """报告目录"""
        return self.root_dir / self.reports_dir

    def check_config(self) -> tuple[bool, list[str]]:
        """
        验证配置有效性

        Returns:
            (是否有效, 错误信息列表)
        """
        errors = []

        # 检查 API Key
        if not self.api_key:
            errors.append("API_KEY is required. Please set it in .env file.")
        elif not self.api_key.startswith(("sk-", "Bearer ")):
            errors.append("API_KEY format seems invalid. Should start with 'sk-'.")

        # 检查必要目录是否存在（不存在会自动创建）
        for path_name, path in [
            ("input_path", self.input_path),
            ("output_path", self.output_path),
            ("knowledge_map_path", self.knowledge_map_path),
            ("state_path", self.state_path),
            ("log_path", self.log_path),
        ]:
            try:
                path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create directory {path_name}: {e}")

        return len(errors) == 0, errors


# 全局配置实例
settings = Settings()
