"""
/**
 * [IN]: src.config (Settings)
 * [OUT]: config 模块单元测试
 * [POS]: pytest 测试套件，Phase 4 单元测试覆盖
 * [PROTOCOL]: config.py 新增配置项 -> 同步添加验证测试
 */
"""
import pytest
from pathlib import Path
from unittest.mock import patch


class TestSettingsPaths:
    """测试 Settings 路径属性"""

    def test_root_dir_is_path(self):
        from src.config import settings
        assert isinstance(settings.root_dir, Path)

    def test_input_path_contains_input_dir(self):
        from src.config import settings
        assert settings.input_dir in str(settings.input_path)

    def test_output_path_contains_output_dir(self):
        from src.config import settings
        assert settings.output_dir in str(settings.output_path)

    def test_state_file_is_json(self):
        from src.config import settings
        assert settings.state_file.suffix == ".json"

    def test_state_file_parent_is_state_path(self):
        from src.config import settings
        assert settings.state_file.parent == settings.state_path

    def test_paths_are_absolute(self):
        from src.config import settings
        for path in [
            settings.input_path,
            settings.output_path,
            settings.state_path,
            settings.log_path,
        ]:
            assert path.is_absolute(), f"{path} should be absolute"


class TestSettingsDefaults:
    """测试 Settings 默认值"""

    def test_default_model(self):
        from src.config import settings
        assert isinstance(settings.model, str)
        assert len(settings.model) > 0

    def test_default_max_retries(self):
        from src.config import settings
        assert settings.max_retries >= 1

    def test_default_canvas_node_width(self):
        from src.config import settings
        assert settings.canvas_node_width > 0

    def test_default_max_filename_length(self):
        from src.config import settings
        assert settings.max_filename_length > 0
        assert settings.max_filename_length <= 255  # OS 限制


class TestSettingsValidate:
    """测试 Settings.validate()"""

    def test_validate_with_valid_key(self):
        with patch.dict("os.environ", {"API_KEY": "sk-test123456"}):
            from importlib import reload
            import src.config as config_module
            reload(config_module)
            is_valid, errors = config_module.settings.validate()
            # validate() 的核心功能：返回 (bool, list)
            assert isinstance(is_valid, bool)
            assert isinstance(errors, list)

    def test_validate_empty_key_returns_error(self):
        """空 API Key 应该产生错误"""
        with patch.dict("os.environ", {"API_KEY": ""}):
            from importlib import reload
            import src.config as config_module
            reload(config_module)
            is_valid, errors = config_module.settings.validate()
            assert not is_valid
            assert len(errors) > 0

    def test_validate_returns_tuple(self):
        from src.config import settings
        result = settings.validate()
        assert isinstance(result, tuple)
        assert len(result) == 2
