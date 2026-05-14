from .errors import AppConfigError
from .models import AppConfig, Flag
from dataclasses import asdict


def build_app_config(argv: list[str]) -> AppConfig:
    config = asdict(AppConfig())
    if len(argv) > 1:
        val: str | bool
        for arg in argv[1:]:
            if "=" in arg:
                key, val = arg.split("=", maxsplit=1)
            else:
                key, val = arg, True
            try:
                parsed_key = Flag(key).parse_flag()
                if parsed_key not in config:
                    raise AppConfigError("AppConfig does not contain "
                                         f"key '{parsed_key}'")
                config[parsed_key] = val
            except ValueError:
                raise AppConfigError(f"Unknown flag: {key}\n"
                                     f"Available flags: {Flag.show_flags()}")
    return AppConfig(**config)
