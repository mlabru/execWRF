from configparser import ConfigParser

def process_arw(
    fo_cfg_parser: ConfigParser,
    fo_forecast_date: ConfigParser,
    fs_token: str
) -> None: ...

def process_wps(fo_cfg_parser: ConfigParser, fo_forecast_date: ConfigParser) -> None: ...

def process_wrf(fo_cfg_parser: ConfigParser, fo_forecast_date: ConfigParser) -> None: ...

def process_all(
    fo_cfg_parser: ConfigParser,
    fo_forecast_date: ConfigParser,
    fs_token: str
) -> None: ...
