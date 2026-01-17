__all__ = ['core', 'strategies', 'indicators', 'utils', 'api', 'config', 'data']

def __getattr__(name):
    if name in __all__:
        import importlib
        module = importlib.import_module(f'.{name}', __name__)
        globals()[name] = module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
