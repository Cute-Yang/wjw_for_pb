import os
import re
from typing import Tuple


def check_and_create_dir_if_not_exsit(path_of_dir: str) -> None:
    if not os.path.exists(path_of_dir):
        print("create dir -> {}".format(path_of_dir))
        os.makedirs(path_of_dir)
    else:
        print("dir -> {} already exist!".format(path_of_dir))


def check_positive_int_value(value: int = None) -> Tuple[str, bool]:
    if not isinstance(value, int):
        error_string = "the value is not int type which has -> {} type".format(type(value))
        return error_string, False
    if value <= 0:
        error_string = "we expect positive value,but get -> {}".format(value)
        return error_string, False
    return None, True

def check_string_with_pattern(pattern:str,string_value:str) -> bool:
    return (re.match(pattern,string_value) is not None)
