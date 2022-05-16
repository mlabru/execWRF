from configparser import ConfigParser

def process_ARW(
    fo_cfg_parser: ConfigParser,
    fo_forecast_date: ConfigParser,
    fs_token: str
) -> None: ...

def process_WPS(fo_cfg_parser: ConfigParser, fo_forecast_date: ConfigParser) -> None: ...

def process_WRF(fo_cfg_parser: ConfigParser, fo_forecast_date: ConfigParser) -> None: ...

def process_all(
    fo_cfg_parser: ConfigParser,
    fo_forecast_date: ConfigParser,
    fs_token: str
) -> None: ...
