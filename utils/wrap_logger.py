import datetime
import logging
import os
import sys
from enum import Enum, unique
from logging import FileHandler
from logging.handlers import TimedRotatingFileHandler
from typing import Sequence

import requests


@unique
class LoggerFileType(Enum):
    ProcessSafeCategory = 0
    RotateCategory = 1
    NormalCategory = 2


class ProcessSafeFileHandler(FileHandler):
    APPEND_MOD = "a"

    def __init__(self, filename: str, mode: str = "a",
                 encoding: str = "utf-8", delay: bool = False,
                 suffix="%Y-%m-%d") -> None:
        """
        Args:
            fileanme:str->the log file path
            mode:file open mod,has a,w..,default is append content to this file
            --- if we use append mod,this will be process safe,important
            encoding:the file encod style
            dealy:bool->default is false
            suffix:str->default,we will save the file use the date time as the suffix,split our log by different day
        """
        if mode != ProcessSafeFileHandler.APPEND_MOD:
            print("Waring:you use open file mode {},which maybe not \
                process safe,we suggest you use a mode".format(mode))
        now = datetime.datetime.now()
        suffix_time = now.strftime(suffix)
        time_filename = "{}.{}".format(filename, suffix_time)
        FileHandler.__init__(self, time_filename, mode=mode,
                             encoding=encoding, delay=delay)
        self.filename = os.fspath(filename)
        self.mode = mode
        self.encoding = encoding
        self.suffix = suffix
        self.suffix_time = suffix_time

    def emit(self, record):
        try:
            if self._check_base_filename():
                self._make_base_filename()
            FileHandler.emit(self, record)
        except(KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)

    def _check_base_filename(self) -> bool:
        _check_status: bool = False
        current_time = datetime.datetime.now().strftime(self.suffix)
        time_filename = "{}.{}".format(self.filename, self.suffix_time)
        if (current_time != self.suffix_time) or (not os.path.exists(time_filename)):
            _check_status = True
        else:
            _check_status = False
        return _check_status

    def _make_base_filename(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        current_time = datetime.datetime.now().strftime(self.suffix)
        self.suffix_time = current_time
        # update the baseFilename
        self.baseFilename = "{}.{}".format(self.filename, self.suffix_time)
        if not self.delay:
            self.stream = open(
                self.baseFilename,
                self.mode,
                encoding=self.encoding
            )


class LogFactory(object):
    # static variable
    headers = {"Content-Type": "text/plain"}
    UPLOAD_BASE_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key={}&type={}"

    def __init__(self,
                 log_dir: str = "sb", log_level: int = logging.INFO,
                 log_prefix: str = "xx.log", log_format: str = None,
                 scope_name: str = "xx", use_webhook: bool = True,
                 webhook_url: str = "", mentioned_list: Sequence = None,
                 use_stream: bool = True, file_handler_type: int = LoggerFileType.RotateCategory,
                 timeout: int = 50, **kwargs) -> None:
        """
        Args:
            log_dir:the directory to save log,default is logs which is on current directory!
            log_leve:int,can be warn,info,error,fatal....
            webhook_url:a url which push info
            use_stream:bool,whether show info to other stream
            file_handler_type:str,if rolling,set rolling log by day/normal:a generic a+ mode file
            scope_name:the scope name,to prevent that different loggers write the same content
            mentioned_list:the person list which you want to push info,default not @ anyone
            timeout:the timeout for net request
            kwargs:some optional params,like log file save number
        """
        self.log_dir = log_dir
        self.log_level = log_level
        self.use_stream = use_stream
        self.file_handler_type = file_handler_type
        self.timeout = timeout
        # optional
        self.use_webhook = use_webhook
        if use_webhook:
            self.webhook_url = webhook_url
            key_index = webhook_url.find("key")
            if key_index == -1:
                Warning("the webhook url: {},maybe an invalid webhook_url \
                     missing key...if you use this,you can not push file!".format(webhook_url))
                self.url_key = ""
            else:
                self.url_key = webhook_url[key_index:]
            self.mentioned_list = mentioned_list
        self.prefix = log_prefix
        self.format = log_format
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        if not isinstance(self.log_level, int):
            try:
                self.log_level = int(self.log_level)
            except ValueError:
                raise RuntimeError(
                    "log level should be int or can be converted to int ,but your input is {}".format(self.log_level))
                # if you not specify,use default 5
        self.max_logfile_number = kwargs.get("logfile_number", 5)
        self._set_logger(
            prefix=self.prefix,
            log_format=self.format,
            scope_name=scope_name
        )
        self.dynamic_bind_logger_method()

    def dynamic_bind_logger_method(self) -> None:
        attrs = ("debug", "warning", "info", "critical", "fatal", "error")
        for attr in attrs:
            func = getattr(self.logger, attr)
            setattr(self, attr, func)

    def get_logger(self):
        if not hasattr(self, "logger"):
            raise AttributeError(
                "object don't have logger attr,please checn your initialize status!")
        return self.logger

    def _set_logger(self, prefix: str, scope_name: str, log_format: str = None):
        """
        Args:
            prefix:the prefix of log file
        """
        # the basict log file path
        log_fp = os.path.join(self.log_dir, prefix)
        if self.file_handler_type == LoggerFileType.RotateCategory:
            file_handler = TimedRotatingFileHandler(
                filename=log_fp,
                when="midnight",
                interval=1,
                backupCount=self.max_logfile_number,  # hard code
                encoding="utf-8"
            )
            print("using rotaing type!")
        # normal log file
        elif self.file_handler_type == LoggerFileType.NormalCategory:
            file_handler = FileHandler(
                filename=log_fp,
                mode="a",
                encoding="utf-8"
            )
            print("use normal type!")
        elif self.file_handler_type == LoggerFileType.ProcessSafeCategory:
            file_handler = ProcessSafeFileHandler(
                filename=log_fp,
                suffix="%Y-%m-%d"
            )
        else:
            valid_catogeries = (
                LoggerFileType.ProcessSafeCategory,
                LoggerFileType.NormalCategory,
                LoggerFileType.RotateCategory
            )
            raise ValueError("here we only have logger types -> {},but you give {} which not in our initialize list!".format(
                valid_catogeries,
                self.file_handler_type
            ))
        # default log format
        if log_format is None:
            log_format = "%(name)s %(asctime)s  [%(levelname)s] {%(filename)s:%(lineno)d} %(message)s"
        formatter = logging.Formatter(log_format)
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(formatter)
        _logger = logging.getLogger(scope_name)
        _logger.setLevel(self.log_level)
        _logger.addHandler(file_handler)
        # add to stream
        if self.use_stream:
            stream_handler = logging.StreamHandler(stream=sys.stdout)
            stream_handler.setLevel(self.log_level)
            stream_handler.setFormatter(formatter)
            _logger.addHandler(stream_handler)
        self.logger = _logger

    def push_text(self, text):
        """
        Args:
            text:str,text content to push
            mentioned_list:list,members you want to @
        Returns:
            dict,http post returns
        """
        if not self.use_webhook:
            self.logger.warning("you set not use webhook....!")
            return
        data = {
            "msgtype": "text",
            "text": {
                "content": text,
                "mentioned_list": self.mentioned_list,
            }
        }
        try:
            res = requests.post(
                self.webhook_url, headers=LogFactory.headers, json=data, timeout=self.timeout)
            res_json = res.json()
        except Exception as e:
            res_json = {"error": str(e)}
        return res_json

    def push_markdown(self, markdown: str):
        """
        Args:
            markdown:str,the markdown format text
        Returns:
            dict,http post returns
        """
        if not self.use_webhook:
            self.logger.warning("you set not use webhook....!")
            return
        if not markdown.endswith("<@all>"):
            markdown += "<@all>"
        data = {
            "msgtype": "markdown",
            "markdown": {
                "content": markdown
            }
        }
        try:
            res = requests.post(
                self.webhook_url, headers=self.headers, json=data, timeout=self.timeout)
            res_json = res.json()
        except Exception as e:
            res_json = {"error": str(e)}
        return res_json

    def debug(self, msg: str) -> None:
        raise NotImplementedError("not write!")

    def info(self, msg: str) -> None:
        raise NotImplementedError("not write!")

    def warning(self, msg: str) -> None:
        raise NotImplementedError("not write!")

    def fatal(self, msg: str) -> None:
        raise NotImplementedError("not write!")

    def critical(self, msg: str) -> None:
        raise NotImplementedError("not write!")

    def error(self, msg: str, traceback: bool = True) -> None:
        raise NotImplementedError("not write!")

    def push_image(self, img_base64, img_md5):
        """
        Args:
            img_base64:img convert to base64
            img_md5:check the img
        Returns:
            dict,http post returns
        """
        if not self.use_webhook:
            self.logger.warning("you set not use webhook....!")
            return
        data = {
            "msg_type": "image",
            "image": {
                "base64": img_base64,
                "md5": img_md5
            }
        }
        try:
            res = requests.post(
                self.webhook_url, headers=self.headers, json=data, timeout=self.timeout)
            res_json = res.json()
        except Exception as e:
            res_json = {"error": str(e)}
        return res_json

    def push_file(self, fp: str):
        """
        Args:
            fp:the file path you want to push
        Returns:
            dict,http post returns
        """
        if not self.use_webhook:
            self.logger.warning("you set not use webhook....!")
            return
        post_url = LogFactory.UPLOAD_BASE_URL.format(
            self.url_key,
            "file"  # 固定传入 file
        )
        file_size = os.path.getsize(fp)
        file_data = {
            "filename": fp,
            "filelength": file_size
        }
        file_res = requests.post(
            post_url,
            json=file_data
        )
        file_json = file_res.json()
        if "media_id" in file_json:
            media_id = file_json["media_id"]
            push_data = {
                "msgtype": "file",
                "file": {
                    "meida_id": media_id
                }
            }
            res = requests.post(
                self.webhook_url, headers=self.headers, json=push_data, timeout=self.timeout)
            res_json = res.json()
            return res_json
        else:
            return file_json

    def __str__(self):
        p_tr = hex(id(self))
        return "<object with log and push info at {}>".format(p_tr)

    def __len__(self):
        return len(self.logger.handlers)


if __name__ == "__main__":
    logger = LogFactory(
        log_dir="logs",
        log_level=logging.INFO,
        scope_name="sunflower",
        webhook_url="https://www.baidu.com"
    )
    logger.dynamic_bind_logger_method()
    logger.info("this is bind method!")
    logger.error("fuck this world!")
