import argparse
import datetime

from src.template_parse import UrlTempalteParser
from src.wjw_url_parse import WjwEpidemicFetcher
from utils import utility
from utils.config_util import SimpleConfigParser
from utils.wrap_logger import LogFactory

# 程序运行的类型 0 表示 只获取昨天最新的数据,1表示爬取指定的某一天的数据
run_for_yesterday = 0
run_for_specify_day = 1
run_for_range_day = 2 # 取区间的等号,即闭区间

arg_parser = argparse.ArgumentParser("wjw script params!")
arg_parser.add_argument("--run_type",type=int,default=0,help="just get the latest data!")
arg_parser.add_argument("--specify_day",type=str,default="",help="which day you want to run!")
arg_parser.add_argument("--left_datetime",type=str,default="",help="left day you want to run!")
arg_parser.add_argument("--right_datetime",type=str,default="",help="right datetime you want to run!")
arg_parser.add_argument("--config_path",type=str,default="conf/epidemic_wjw.ini",help="the conf path...")


if __name__ == "__main__":
    args = arg_parser.parse_args()
    config_path = args.config_path
    run_type = args.run_type
    config_parser = SimpleConfigParser(config_path)
    scope_name = "wjw_epidemic_conf"
    
    wjw_tabel_url_formatter:str = config_parser.get_value(scope=scope_name,field_name="tabel_url")
    date_format:str = config_parser.get_value(scope_name,"date_format")
    root_url:str=config_parser.get_value(scope_name,"root_url")
    log_dir:str=config_parser.get_value(scope_name,"log_dir")
    data_save_dir:str = config_parser.get_value(scope_name,"data_save_dir")
    
    if date_format == "%Y-%m-%d":
        date_pattern = r"^[1-9]\d{3,3}\-\d{2,2}\-\d{2,2}$"
    elif date_format == "%Y-%m-%d %H:%M:%S":
        date_pattern = r"^[1-9]\d{3,3}\-\d{2,2}\-\d{2,2} \d{2,2}:\d{2,2}:\d{2,2}$"
    else:
        raise ValueError("unexpected date format -> {}".format(date_format))
    
    wjw_fetcher_logger = LogFactory(
        log_dir="logs",
        log_prefix="wjw_fetcher.log",
        scope_name="wjw_fetcher",
        use_webhook=False
    )

    content_template_logger = LogFactory(
        log_dir="content_template",
        log_prefix="content_tempalte_parse.log",
        scope_name="content_template_parse",
        use_webhook=False
    )

    content_template_paser = UrlTempalteParser(
        logger=content_template_logger,
        date_format=date_format
    )

    wjw_fetcher = WjwEpidemicFetcher(
        logger=wjw_fetcher_logger,
        epidemic_tabel_url_formatter=wjw_tabel_url_formatter,
        date_format=date_format,
        save_dir=data_save_dir,
        wjw_epedemic_root_url=root_url,
        url_template_parser=content_template_paser,

    )

    if run_type == run_for_yesterday:
        yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
        yesterday_string = yesterday.strftime(yesterday)
        wjw_fetcher.fetch_with_specify_day(yesterday_string)
    elif run_type == run_for_specify_day:
        specify_day = args.specify_day
        if not utility.check_string_with_pattern(date_pattern,specify_day):
            raise ValueError("the specify day -> {} not match the date format -> {}".format(
                specify_day,
                date_format
            ))
        wjw_fetcher.fetch_with_specify_day(specify_day)
    elif run_type == run_for_range_day:
        left_datetime = args.left_datetime
        right_datetime = args.right_datetime
        if (not utility.check_string_with_pattern(date_pattern,left_datetime)) or (not utility.check_string_with_pattern(date_pattern,right_datetime)):
            raise ValueError("the date -> {}/{} not match the date format -> {}".format(
                left_datetime,
                right_datetime,
                date_format
            ))
        wjw_fetcher.fetch_with_specify_day_range(
            left_datetime=datetime.datetime.strptime(left_datetime,date_format),
            right_datetime=datetime.datetime.strptime(right_datetime,date_format),
            sleep_randomly=True
        )
    else:
        raise ValueError("unknonw run type -> {}".format(run_type))

    # main_script.py 是程序的主函数
    # 这里演示 ,比如 想获取 11-27的数据,运行以上函数即可
    #可以看到数据成功写入
    #打开看一哈
    #没有问题
