"""配置服务测试: 嵌套日志配置默认值 + 热更 seam。"""

from app.core.config import reload_settings, settings


def test_should_expose_logging_defaults() -> None:
    # 嵌套 LoggingSettings 的默认值(可被 APP_LOGGING__* 环境变量覆盖)
    assert settings.logging.rotation_interval_hours == 8
    assert settings.logging.backup_count == 30
    assert settings.logging.json_file == "app.jsonl"


def test_should_reload_settings_in_place() -> None:
    # 热更 seam: 原地更新同一单例对象(配置中心 watcher 的接入点)
    assert reload_settings() is settings
