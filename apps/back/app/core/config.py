"""应用配置: 环境变量 + .env, 前缀 APP_。"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_", extra="ignore")

    # 异步 SQLite, WAL 模式在 db/session.py 的连接钩子里开启
    database_url: str = "sqlite+aiosqlite:///./dev.db"
    api_prefix: str = "/api"
    log_level: str = "INFO"
    # 默认打印每条 SQL(便于开发排查); 生产可设 APP_SQL_ECHO=false 关闭
    sql_echo: bool = True
    # CORS 放行来源: 默认 ["*"] 放行所有跨域(便于起步);
    # 生产收窄用 APP_CORS_ORIGINS='["https://你的域名"]'(JSON 数组)
    cors_origins: list[str] = ["*"]


settings = Settings()
