"""Centralized utility for loading domain-specific configuration files."""
import importlib
from typing import Any, TypeVar

T = TypeVar('T')


class ConfigReader:
    _cache = {}

    @classmethod
    def load_domain_config(cls, domain_name: str) -> Any:
        if domain_name in cls._cache:
            return cls._cache[domain_name]

        try:
            module_path = f'src.domains.{domain_name}.config'
            config_module = importlib.import_module(module_path)

            if hasattr(config_module, 'Config'):
                config_class = getattr(config_module, 'Config')
                config_instance = config_class()
                cls._cache[domain_name] = config_instance
                return config_instance
            else:
                raise AttributeError(f"Config class not found in {module_path}")

        except ImportError as e:
            raise ImportError(f"Could not load config for domain '{domain_name}': {str(e)}")

    @classmethod
    def get(cls, domain_name: str, key: str, default: Any = None) -> Any:
        config = cls.load_domain_config(domain_name)
        return getattr(config, key, default)

    @classmethod
    def clear_cache(cls) -> None:
        cls._cache.clear()
