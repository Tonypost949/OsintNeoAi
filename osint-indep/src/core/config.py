"""
Configuration management for OSINT Independent Platform.
Supports YAML config files with environment variable overrides.
"""
import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional, List
from dataclasses import dataclass, field
import logging


@dataclass
class DatabaseConfig:
    type: str = "sqlite"
    host: str = "localhost"
    port: int = 5432
    database: str = "osint"
    username: str = ""
    password: str = ""
    path: str = "data/osint.db"
    pool_size: int = 10
    max_overflow: int = 20
    echo: bool = False
    
    @property
    def url(self) -> str:
        if self.type == "sqlite":
            return f"sqlite:///{self.path}"
        elif self.type == "postgresql":
            return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        elif self.type == "mysql":
            return f"mysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        return f"sqlite:///{self.path}"


@dataclass
class APIConfig:
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    timeout: int = 30
    cors_origins: List[str] = field(default_factory=lambda: ["*"])
    rate_limit: int = 100
    rate_limit_window: int = 60
    auth_enabled: bool = True
    jwt_secret: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expiration: int = 3600
    api_key_header: str = "X-API-Key"


@dataclass
class CollectorConfig:
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    user_agent: str = "OSINT-Independent/1.0"
    proxy: str = ""
    verify_ssl: bool = True
    max_concurrent: int = 10
    rate_limit: int = 60
    rate_limit_window: int = 60


@dataclass
class EnricherConfig:
    timeout: int = 30
    max_retries: int = 3
    cache_ttl: int = 3600
    api_keys: Dict[str, str] = field(default_factory=dict)


@dataclass
class LoggingConfig:
    level: str = "INFO"
    format: str = "json"
    file: str = "logs/osint.log"
    max_size: int = 10485760
    backup_count: int = 5
    console: bool = True


@dataclass
class StorageConfig:
    type: str = "sqlite"
    path: str = "data"
    bucket: str = ""
    region: str = "us-east-1"


@dataclass
class WebConfig:
    host: str = "0.0.0.0"
    port: int = 8080
    debug: bool = False
    secret_key: str = ""
    session_timeout: int = 3600


class Config:
    """Main configuration class with YAML file and env var support."""
    
    def __init__(self, config_path: Optional[str] = None):
        self._config: Dict[str, Any] = {}
        self._load_config(config_path)
        self._apply_env_overrides()
        
        # Initialize typed config objects
        self.database = DatabaseConfig(**self._config.get('database', {}))
        self.api = APIConfig(**self._config.get('api', {}))
        self.collectors = CollectorConfig(**self._config.get('collectors', {}))
        self.enrichers = EnricherConfig(**self._config.get('enrichers', {}))
        self.logging = LoggingConfig(**self._config.get('logging', {}))
        self.storage = StorageConfig(**self._config.get('storage', {}))
        self.web = WebConfig(**self._config.get('web', {}))
    
    def _load_config(self, config_path: Optional[str] = None) -> None:
        """Load configuration from YAML file."""
        paths = []
        
        if config_path:
            paths.append(Path(config_path))
        
        # Default search paths
        paths.extend([
            Path("config/default.yaml"),
            Path("config/development.yaml"),
            Path("config/production.yaml"),
            Path("/etc/osint/config.yaml"),
            Path.home() / ".config" / "osint" / "config.yaml",
        ])
        
        for path in paths:
            if path.exists():
                with open(path, 'r') as f:
                    self._config = yaml.safe_load(f) or {}
                break
        else:
            self._config = {}
    
    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides."""
        env_mappings = {
            'OSINT_DB_TYPE': ('database', 'type'),
            'OSINT_DB_HOST': ('database', 'host'),
            'OSINT_DB_PORT': ('database', 'port'),
            'OSINT_DB_NAME': ('database', 'database'),
            'OSINT_DB_USER': ('database', 'username'),
            'OSINT_DB_PASS': ('database', 'password'),
            'OSINT_DB_PATH': ('database', 'path'),
            'OSINT_API_HOST': ('api', 'host'),
            'OSINT_API_PORT': ('api', 'port'),
            'OSINT_API_WORKERS': ('api', 'workers'),
            'OSINT_JWT_SECRET': ('api', 'jwt_secret'),
            'OSINT_COLLECTOR_TIMEOUT': ('collectors', 'timeout'),
            'OSINT_COLLECTOR_PROXY': ('collectors', 'proxy'),
            'OSINT_LOG_LEVEL': ('logging', 'level'),
            'OSINT_LOG_FILE': ('logging', 'file'),
            'OSINT_WEB_HOST': ('web', 'host'),
            'OSINT_WEB_PORT': ('web', 'port'),
            'OSINT_WEB_SECRET': ('web', 'secret_key'),
        }
        
        for env_var, (section, key) in env_mappings.items():
            value = os.environ.get(env_var)
            if value is not None:
                if section not in self._config:
                    self._config[section] = {}
                # Type conversion
                if key in ('port', 'workers', 'timeout', 'max_retries', 'max_concurrent', 
                          'rate_limit', 'rate_limit_window', 'pool_size', 'max_overflow',
                          'cache_ttl', 'max_size', 'backup_count', 'session_timeout',
                          'jwt_expiration'):
                    value = int(value)
                elif key in ('echo', 'verify_ssl', 'auth_enabled', 'debug', 'cors_origins'):
                    value = value.lower() in ('true', '1', 'yes', 'on')
                self._config[section][key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation key."""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            if value is None:
                return default
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value by dot-notation key."""
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Return configuration as dictionary."""
        return self._config.copy()
    
    def save(self, path: str) -> None:
        """Save configuration to YAML file."""
        with open(path, 'w') as f:
            yaml.dump(self._config, f, default_flow_style=False)


# Global config instance
_config: Optional[Config] = None


def get_config(config_path: Optional[str] = None) -> Config:
    """Get global configuration instance."""
    global _config
    if _config is None:
        _config = Config(config_path)
    return _config


def reset_config() -> None:
    """Reset global configuration."""
    global _config
    _config = None