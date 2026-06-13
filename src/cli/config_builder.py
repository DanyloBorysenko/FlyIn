from .errors import AppConfigError
from .models import AppConfig, Flag
from dataclasses import asdict


class ConfigBuilder:
    """Build app object containing flags and main map's path"""
    def build_app_config(self, argv: list[str]) -> AppConfig:
        """
        Build an AppConfig instance from command-line arguments.
        Validate supported flags and convert them into the
        application's configuration object.

        Raises:
            AppConfigError:
                1. An unsupported flag is provided.
                2. '=' is used with a flag that does not accept a value.
                3. A valid flag is not mapped to AppConfig.
        """
        print(argv)
        config = asdict(AppConfig())
        if len(argv) > 1:
            val: str | bool
            for arg in argv[1:]:
                if "=" in arg:
                    if not (arg.startswith(Flag.MAP_PATH.value)
                            or arg.startswith(Flag.PLAYLIST_PATH.value)):
                        raise AppConfigError("Using '=' is allowed only with"
                                             f" '{Flag.MAP_PATH.value}' and"
                                             f" '{Flag.PLAYLIST_PATH.value}'")
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
                                         f"Available flags: "
                                         f"{Flag.show_flags()}")
        return AppConfig(**config)
