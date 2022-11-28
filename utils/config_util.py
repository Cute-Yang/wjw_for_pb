import os
from configparser import RawConfigParser
from typing import Any, Callable


class Slipper(RawConfigParser):
    """
    to support upper string,while default parser which transfer all value -> lower!
    """

    def __init__(self, defaults=None):
        RawConfigParser.__init__(self, defaults=None)

    def optionxform(self, optionstr):
        return optionstr


class SimpleConfigParser(object):
    def __init__(self, config_path: str) -> None:
        self.config_path = config_path
        self._parser = Slipper()
        if not os.path.exists(config_path):
            raise FileNotFoundError("fp {} is not exist!".format(config_path))
        self._parser.read(config_path, encoding="utf-8")

    def get_value(self, scope: str, field_name: str, callback: Callable = None) -> Any:
        """
        this is a generic function to get the field value with specified transfer function
        Args:
            scope:str,the section name
            field_name:str,feature name
            callback:transfer the value,should only accept one param!
        """
        raw_value = self._parser.get(scope, field_name)
        if callback is not None:
            try:
                raw_value = callback(raw_value)
            except Exception:
                raise RuntimeError(
                    "we can not specified callback to transfer our value,please check ...")
        return raw_value


if __name__ == "__main__":
    simple_config_parser = SimpleConfigParser("conf/sunflower.ini")
    scope = "sunflower"
    name = simple_config_parser.get_value(scope, "name")
    color = simple_config_parser.get_value(scope, "color")
    length = simple_config_parser.get_value(scope, "length", float)
    print(name, color, length)
