"""应用配置(配置服务): 环境变量 + .env, 预留配置中心接入点。

优先级: 环境变量 > .env > 代码默认。纯 12-factor —— 各环境差异用**环境变量**表达,
不为每个环境建配置文件。K8s ConfigMap / Nacos / Eureka 等把配置挂成 env 注入即可。

配置中心接入(seam):
- reload_settings() 是**热更钩子** —— 未来接配置中心的变更 watcher 时, 由其在配置变更
  回调里调用它从环境重新加载; 需要热生效的副作用(如重配日志级别)由调用方拿到新配置后触发
  (见 app/core/logging.configure_logging)。
- 母版只留这个 seam, 不预置任何配置中心客户端 / watcher(YAGNI)。

嵌套键用双下划线覆盖, 例: APP_LOGGING__LEVEL=DEBUG、APP_LOGGING__SQL_ECHO=false。
"""

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class LoggingSettings(BaseModel):
    """日志格式 / 滚动 / 留存的配置(嵌套于 Settings.logging)。"""

    level: str = "INFO"
    dir: str = "logs"
    json_file: str = "app.jsonl"
    rotation_when: str = "H"  # 滚动单位: H=小时
    rotation_interval_hours: int = 8  # 每 8 小时滚动一份
    backup_count: int = 30  # 保留份数: 3 份/天 * 10 天 = 30(即 10 天)
    sql_echo: bool = True  # 是否打印每条 SQL(生产建议 false)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_nested_delimiter="__",  # 嵌套键: APP_LOGGING__LEVEL
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # 异步 SQLite, WAL 模式在 db/session.py 的连接钩子里开启
    database_url: str = "sqlite+aiosqlite:///./dev.db"
    api_prefix: str = "/api"
    # CORS 放行来源: 默认 ["*"] 放行所有跨域; 生产收窄用 APP_CORS_ORIGINS='["https://你的域名"]'
    cors_origins: list[str] = ["*"]
    logging: LoggingSettings = LoggingSettings()


settings = Settings()


def reload_settings() -> Settings:
    """从环境重新加载配置, **原地更新单例**(热更 seam, 见模块 docstring)。

    原地更新使既有 `from app.core.config import settings` 的引用也能读到新值; 有副作用的
    组件(日志等)需要调用方拿到返回值后自行重新应用。
    """
    fresh = Settings()
    settings.__dict__.update(fresh.__dict__)
    return settings
