import asyncio
import datetime
import os
import random
import time
import traceback
from typing import List, Tuple

import pandas as pd
from utils import utility

from .template_parse import (AsymptomaticParseResult, CureParagraphParseResult,
                             GATParseResult, LocalAggParseResult,
                             MedicalObservationParseResult,
                             NewAddParagraphParseResult, OutsideAggParseResult,
                             TabelContentMatchResult, UrlTempalteParser)

try:
    # get the ref of list param!
    from pyppeteer.launcher import DEFAULT_ARGS
    wanted_remove_params = ('--enable-automation',)
    if isinstance(DEFAULT_ARGS, list):
        for wanted_remove_param in wanted_remove_params:
            try:
                DEFAULT_ARGS.remove(wanted_remove_param)
                print("Successfully removed the droped param -> {}".format(wanted_remove_param))
            except ValueError as ex:
                print("param -> {} not found in our list!traceback -> {}".format(
                    wanted_remove_param,
                    str(ex)
                ))
except ImportError:
    print("some errors occured while import the pyppeteer!")
    traceback.print_exc()
    exit(-1)

from pyppeteer import launch
from utils.wrap_logger import LogFactory, LoggerFileType


class WjwEpidemicFetcher(object):
    def __init__(self, logger: LogFactory = None, epidemic_tabel_url_formatter: str = None,
                 date_format: str = None, save_dir: str = None, wjw_epedemic_root_url: str = None,
                 url_template_parser: UrlTempalteParser = None, **kwargs) -> None:
        """
        Args:
            epidemic_tabel_url:str,the root url of wjw data
            date_format:str,a format for date string!
            save_dir:the root directory you want to save your data,if not exist! we will create it!
        """
        if logger is None:
            print("you did not specify logger,we will create a default logger!")
            logger = LogFactory(
                log_dir="logs",
                log_prefix="wjs_epidemic_fetcher",
                scope_name="wjs_epidemic",
                use_webhook=False,
                file_handler_type=LoggerFileType.RotateCategory
            )
        self.logger = logger
        utility.check_and_create_dir_if_not_exsit(save_dir)
        self.save_dir = save_dir
        self.date_format = date_format
        if not epidemic_tabel_url_formatter.startswith("http"):
            error_string = "the epidmic_url should starts with http,but get -> {},maybe it is not right!".format(
                epidemic_tabel_url_formatter)
            self.logger.info(error_string)
            raise ValueError(error_string)
        self.epidemic_tabel_url_formatter = epidemic_tabel_url_formatter
        self.url_template_parser = url_template_parser
        self.wjw_epidemic_root_url = wjw_epedemic_root_url

        self.max_retry_times: int = kwargs.get("max_retry_times", 12)

        # 每一页的有多少条wjw数据? 这个可以进行硬编码,也可以实际去获取
        self.epidemic_data_size_of_each_page = 24

        # set the random interval 模拟人的行为,随机在某一段区间内沉睡程序
        self.random_sleep_lower = 0.5
        self.random_sleep_upper = 3.5

    async def _url_context_fetch_core(self, url: str = None) -> str:
        """
        the core function to get the url!
        """
        browser = await launch(
            {
                "headless": False,
                "dumpio": True,
                "autoClose": True
            }
        )

        # open the url
        page = await browser.newPage()
        await page.goto(url)
        await asyncio.wait(
            [page.waitForNavigation()]
        )
        content = await page.content()
        await browser.close()
        return content

    def _url_context_fetch(self, url: str) -> str:
        return asyncio.get_event_loop().run_until_complete(self._url_context_fetch_core(url=url))

    def _check_data_for_wjs_epidemic_tabel(self, content: str) -> bool:
        key_string = "疫情通报"
        return (key_string in content)

    def get_wjs_epidemic_tabel_data(self, page_indices: int = None) -> str:
        """
        Args:
            page_indices:int,the indices of current url!
        """
        s1, flag = utility.check_positive_int_value(page_indices)
        if not flag:
            self.logger.info("bad param page_indices,reason -> {}".format(s1))
            raise RuntimeError(s1)

        if page_indices == 1:
            self.logger.info("fetch the latest data,and we will no any formatter for the url!")
            wjw_tabel_url = self.epidemic_tabel_url_formatter.replace("{}", "")
        else:
            wjw_tabel_url = self.epidemic_tabel_url_formatter.format(page_indices)
        max_retry_times = self.max_retry_times
        content = ""
        while max_retry_times > 0:
            self.logger.info("try to get the wjw tabel data for {} time!".format(self.max_retry_times - max_retry_times + 1))
            try:
                content = self._url_context_fetch(url=wjw_tabel_url)
                if self._check_data_for_wjs_epidemic_tabel(content):
                    break
                else:
                    max_retry_times -= 1
            except Exception as ex:
                self.logger.info("faile by reason -> {} at {} times".format(
                    str(ex),
                    self.max_retry_times - max_retry_times + 1
                ))
                max_retry_times -= 1
        return content

    def _is_new_add_positive_paragraph(self, content) -> bool:
        return "31个省（自治区、直辖市）和新疆生产建设兵团报告新增确诊病例" in content

    # 这些函数一定是 noexcept 的,因为我们有 default value!
    def transfer_new_add_positive_data_2_data_frame(self, result: NewAddParagraphParseResult) -> List[Tuple[str, pd.DataFrame]]:
        data_frame_list = []
        new_agg_data_kv_list = [
            {"key": "新增确诊病例", "value": result.total_new_add_size},
            {"key": "境外输入病例", "value": result.outside_new_add_all_size},
            {"key": "境外由无症状感染者转为确诊病例", "value": result.outside_normal_2_positive_size},
            {"key": "新增本土病例", "value": result.local_new_add_all_size},
            {"key": "本土无由症状感染者转为确诊病例", "value": result.local_normal_2_positive_size},
            {"key": "新增死亡病例", "value": result.dead_new_add_size},
            {"key": "新增本土死亡病例", "value": result.dead_local_new_add},
            {"key": "新增境外死亡病例", "value": result.dead_outside_new_add},
            {"key": "新增增疑似病例", "value": result.maybe_new_add_size},
            {"key": "新增本土疑似病例", "value": result.maybe_local_size},
            {"key": "新增境外疑似病例", "value": result.maybe_outside_size}
        ]
        data_frame_list.append(
            ("新增病例汇总数据", pd.DataFrame(new_agg_data_kv_list))
        )

        new_outside_detail_kv_list = []
        for province, value in result.outside_new_add_detail_pairs:
            new_outside_detail_kv_list.append(
                {
                    "province": province,
                    "value": value
                }
            )
        data_frame_list.append(
            ("境外输入明细(按省份)", pd.DataFrame(new_outside_detail_kv_list))
        )

        new_outside_normal_2_positive_kv_list = []
        for province, value in result.outside_normal_2_positive_pairs:
            new_outside_normal_2_positive_kv_list.append(
                {
                    "province": province,
                    "value": value
                }
            )
        data_frame_list.append(
            ("境外由无症状感染者转为确诊病例明细(按省份)", pd.DataFrame(new_outside_normal_2_positive_kv_list))
        )
        new_local_detail_kv_list = []
        for province, value in result.local_new_add_detail_pairs:
            new_local_detail_kv_list.append(
                {
                    "province": province,
                    "value": value
                }
            )
        data_frame_list.append(
            ("本土病例明细(按省份)", pd.DataFrame(new_local_detail_kv_list))
        )

        new_local_normal_2_positive_kv_list = []
        for province, value in result.outside_normal_2_positive_pairs:
            new_local_normal_2_positive_kv_list.append(
                {
                    "province": province,
                    "value": value
                }
            )
        data_frame_list.append(
            ("本土由无症状感染者转为确诊病例明细(按省份)", pd.DataFrame(new_local_normal_2_positive_kv_list))
        )
        return data_frame_list

    def _is_new_add_cure_paragraph(self, content) -> bool:
        return "当日新增治愈出院病例" in content

    def transfer_new_add_cure_data_2_data_frame(self, result: CureParagraphParseResult) -> List[Tuple[str, pd.DataFrame]]:
        data_frame_list = []
        cure_new_add_data_kv_list = [
            {"key": "当日新增治愈出院病例", "value": result.cure_total_add_size},
            {"key": "境外输入病例", "value": result.outside_cure_add_size},
            {"key": "本土病例", "value": result.local_cure_add_size},
            {"key": "解除医学观察的密切接触者", "value": result.sizeof_close_observation},
            {"key": "重症病例变化", "value": result.severe_illness_instance}
        ]
        data_frame_list.append(
            ("新增治愈汇总数据", pd.DataFrame(cure_new_add_data_kv_list))
        )

        local_cure_detal_kv_list = []
        for province, value in result.local_cure_detail_pairs:
            local_cure_detal_kv_list.append(
                {
                    "province": province,
                    "value": value
                }
            )
        data_frame_list.append(
            ("本土新增治愈明细(按省份)", pd.DataFrame(local_cure_detal_kv_list))
        )
        return data_frame_list

    def _is_outside_agg_paragraph(self, content) -> bool:
        return "境外输入现有确诊病例" in content

    def transfer_outside_agg_2_data_frame(self, result: OutsideAggParseResult) -> List[Tuple[pd.date_range]]:
        data_frame_list = []
        outside_agg_kv_list = [
            {"key": "境外输入现有确诊病例", "value": result.currrent_outside_positive_instance},
            {"key": "疑似病例", "value": result.outside_maybe_positive_instance},
            {"key": "累计确诊病例", "value": result.outside_accumulated_positive_instance},
            {"key": "计治愈出院病例", "value": result.outside_accumulated_cure_instance},
            {"key": "死亡病例", "value": result.outside_dead_instance}
        ]
        data_frame_list.append(
            ("境外输入病例汇总", pd.DataFrame(outside_agg_kv_list))
        )
        return data_frame_list

    def _is_local_agg_paragrah(self, content) -> bool:
        return "据31个省（自治区、直辖市）和新疆生产建设兵团报告，现有确诊病例" in content

    def transfer_local_agg_2_data_frame(self, result: LocalAggParseResult) -> List[Tuple[pd.DataFrame]]:
        data_frame_list = []
        local_agg_kv_list = [
            {"key": "现有确诊病例", "value": result.current_local_positive_size},
            {"key": "重症病例", "value": result.current_local_sereve_illness_size},
            {"key": "累计治愈出院病例", "value": result.local_accumulated_cure_size},
            {"key": "累计死亡病例", "value": result.local_accumulated_dead_size},
            {"key": "累计报告确诊病例", "value": result.local_accumulated_positive_size},
            {"key": "现有疑似病例", "value": result.local_maybe_positive_size},
            {"key": "累计追踪到密切接触者", "value": result.local_accumulated_closely_size},
            {"key": "尚在医学观察的密切接触者", "value": result.local_in_observation}
        ]
        data_frame_list.append(
            ("本土病例汇总", pd.DataFrame(local_agg_kv_list))
        )
        return data_frame_list

    def _is_asymptomatic_paragraph(self, content) -> bool:
        return "31个省（自治区、直辖市）和新疆生产建设兵团报告新增无症状感染者" in content

    def transfer_asymptomatic_2_data_frame(self, result: AsymptomaticParseResult) -> List[Tuple[pd.DataFrame]]:
        data_frame_list = []
        asymtopatic_agg_kv_list = [
            {"key": "新增无症状感染者", "value": result.asymptomatic_add_total_size},
            {"key": "境外输入", "value": result.asymptomatic_outside_add_size},
            {"key": "本土病例", "value": result.asymptomatic_local_add_size}
        ]
        data_frame_list.append(
            ("新增无症状感染汇总", pd.DataFrame(asymtopatic_agg_kv_list))
        )

        asymtopatic_local_detail_kv_list = []
        for province, value in result.asymptomatic_local_detail_pairs:
            asymtopatic_local_detail_kv_list.append(
                {
                    "province": province,
                    "value": value
                }
            )
        data_frame_list.append(
            ("本土新增无症状感染明细(按省份)", pd.DataFrame(asymtopatic_local_detail_kv_list))
        )
        return data_frame_list

    def _is_medical_observation_paragraph(self, content) -> bool:
        return "当日解除医学观察的无症状感染者" in content

    def transfer_medical_observation_2_data_frame(self, result: MedicalObservationParseResult) -> List[Tuple[pd.DataFrame]]:
        data_frame_list = []
        medical_observation_agg_kv_list = [
            {"key": "当日解除医学观察的无症状感染者", "value": result.close_observation_total_size},
            {"key": "境外输入", "value": result.close_outside_observaton_size},
            {"key": "本土病例", "value": result.close_local_observation_size},
            {"key": "当日转为确诊病例", "value": result.transfer_2_postive_size},
            {"key": "当日转为确诊病例(本土)", "value": result.transfer_2_postive_size - result.outside_transfer_2_postive_size},
            {"key": "当日转为确诊病例(境外输入)", "value": result.outside_transfer_2_postive_size},
            {"key": "尚在医学观察的无症状感染者", "value": result.in_medical_observation_size},
            {"key": "尚在医学观察的无症状感染者", "value": result.in_medical_observation_size - result.outside_in_medical_observation_size},
            {"key": "尚在医学观察的无症状感染者(境外输入)", "value": result.outside_in_medical_observation_size}
        ]
        data_frame_list.append(
            ("医学观察汇总", pd.DataFrame(medical_observation_agg_kv_list))
        )

        close_observation_local_detail_kv_list = []
        for province, value in result.close_local_detail_pairs:
            close_observation_local_detail_kv_list.append(
                {
                    "province": province,
                    "value": value
                }
            )
        data_frame_list.append(
            ("本土解除医学观察明细(按省份)", pd.DataFrame(close_observation_local_detail_kv_list))
        )
        return data_frame_list

    def _is_gat_paragrpah(self, content) -> bool:
        return "累计收到港澳台地区通报确诊病例" in content

    def transfer_gat_2_data_frame(self, result: GATParseResult) -> List[Tuple[str, pd.DataFrame]]:
        data_frame_list = []
        gat_agg_kv_list = [
            {"key": "港澳台地区通报确诊病例", "value": result.gat_accumulated_total_size},
            {"key": "香港特别行政区", "value": result.hongkong_accumulate_total_size},
            {"key": "香港特别行政区出院", "value": result.hongkong_out_hospital_size},
            {"key": "香港特别行政区死亡", "value": result.hongkong_dead_size},
            {"key": "澳门特别行政区", "value": result.aomen_accumulate_total_size},
            {"key": "澳门特别行政区出院", "value": result.aomen_out_hospital_size},
            {"key": "澳门特别行政区死亡", "value": result.aomen_dead_size},
            {"key": "台湾地区", "value": result.taiwan_accumulated_total_size},
            {"key": "台湾地区出院", "value": result.taiwan_out_hospital_size},
            {"key": "台湾地区死亡", "value": result.taiwan_dead_size}
        ]
        data_frame_list.append(
            ("港澳台汇总", pd.DataFrame(gat_agg_kv_list))
        )
        return data_frame_list

    def _create_ramdom_float_number(self) -> float:
        random_value = random.random() * (self.random_sleep_upper - self.random_sleep_lower)
        return random_value

    def fetch_with_specify_day_range(self, left_datetime: datetime.datetime = None,
                                     right_datetime: datetime.datetime = None,
                                     sleep_randomly: bool = True) -> None:
        if(right_datetime < left_datetime):
            raise ValueError("right datetime can not be less than left datetime!")
        left_page_indices = self._compute_page_indices_with_today(left_datetime)
        right_page_indices = self._compute_page_indices_with_today(right_datetime)
        for page_indices in range(left_page_indices, right_page_indices + 1):
            page_content = self.get_wjs_epidemic_tabel_data(page_indices=page_indices)
            parsed_page_data: TabelContentMatchResult = self.url_template_parser.parse_tabel_url_content(
                content=page_content
            )
            epidemic_data_list = parsed_page_data.epidemic_data_list
            for sub_url, title, date_string in epidemic_data_list:
                date = self._deserialize_date_string(date_string=date_string)
                date = date - datetime.timedelta(days=1)
                date_string = date.strftime(self.date_format)
                if left_datetime <= date <= right_datetime:
                    self.logger.info("analyse the data for -> {}".format(date_string))
                    epidemic_data_url = self._safe_concat_urls(
                        self.wjw_epidemic_root_url,
                        sub_url
                    )
                    data_frame_list,content_data_list = self.fetch_data_frame_data_list_by_specify_url(
                        epidemic_data_url=epidemic_data_url
                    )
                    source_save_dir = os.path.join(self.save_dir, date_string)
                    utility.check_and_create_dir_if_not_exsit(source_save_dir)
                    excel_file_path = os.path.join(source_save_dir, "{}.xlsx".format(title))
                    text_file_path = os.path.join(source_save_dir, "{}.txt".format(date.strftime(self.date_format)))
                    self._write_data_frame_list_to_file(
                        data_frame_list=data_frame_list,
                        save_path=excel_file_path
                    )
                    self.logger.info("write excel data -> {}".format(excel_file_path))
                    with open(text_file_path, "w", encoding="utf-8") as f:
                        for content in content_data_list:
                            f.write(content)
                            f.write("\n")
                    self.logger.info("write text data -> {}".format(text_file_path))
                else:
                    self.logger.info("date -> {} out of range,we specify {} ~ {}!we will ignore this".format(
                        date_string,
                        left_datetime.strftime(self.date_format),
                        right_datetime.strftime(self.date_format)
                    ))
                    continue
                if sleep_randomly:
                    sleep_time = self._create_ramdom_float_number()
                    self.logger.info("sleeping for time -> {} for next op!".format(sleep_time))
                    time.sleep(sleep_time)

    def fetch_data_frame_data_list_by_specify_url(self, epidemic_data_url: str) -> Tuple[List[Tuple[str, pd.DataFrame]], List[str]]:
        """
        Args:
            epidemic_data_url:str,the url of epidemic data for a specify day!
        Returns:
            total_data_frame_list:List,the list of sub data frame
            epidemic_content_list:list,the list of epidemic paragraph data!
        """
        epidemic_content = self._url_context_fetch(url=epidemic_data_url)
        total_data_frame_list = []
        epidemic_content_list = []
        # just for test!
        # with open("test.html", "r", encoding="utf-8") as f:
        #     epidemic_content = f.read()
        if epidemic_content != "":
            epidemic_content_list = self.url_template_parser.parse_epidemic_url_content(
                content=epidemic_content
            )
            n = len(epidemic_content_list)

            writer = open("data.txt", "w", encoding="utf-8")
            for i in range(n):
                content = epidemic_content_list[i]
                writer.write(content)
                writer.write("\n")
                data_frame_list = []
                if self._is_new_add_positive_paragraph(content):
                    result = self.url_template_parser.format_new_add_epidemic_instance(content=content)
                    data_frame_list = self.transfer_new_add_positive_data_2_data_frame(result=result)

                elif self._is_new_add_cure_paragraph(content):
                    result = self.url_template_parser.format_new_add_cure_instance(content=content)
                    data_frame_list = self.transfer_new_add_cure_data_2_data_frame(result=result)

                elif self._is_outside_agg_paragraph(content):
                    result = self.url_template_parser.format_outside_agg(content=content)
                    data_frame_list = self.transfer_outside_agg_2_data_frame(result)

                elif self._is_local_agg_paragrah(content):
                    result = self.url_template_parser.format_local_agg(content=content)
                    data_frame_list = self.transfer_local_agg_2_data_frame(result)

                elif self._is_asymptomatic_paragraph(content):
                    result = self.url_template_parser.format_asymptomatic(content=content)
                    data_frame_list = self.transfer_asymptomatic_2_data_frame(result)

                elif self._is_medical_observation_paragraph(content):
                    result = self.url_template_parser.format_medical_obsevation(content=content)
                    data_frame_list = self.transfer_medical_observation_2_data_frame(result)

                elif self._is_gat_paragrpah(content):
                    result = self.url_template_parser.format_gat(content=content)
                    data_frame_list = self.transfer_gat_2_data_frame(result)
                else:
                    self.logger.info("unknown paragraph -> {}".format(content))
                    data_frame_list = []
                total_data_frame_list.extend(data_frame_list)
        else:
            self.logger.info("the content is empty!")
        # self._write_data_frame_list_to_file(total_data_frame_list)
        return total_data_frame_list, epidemic_content_list

    def fetch_with_specify_day(self, date: datetime.datetime):
        """
        get the data at specify day!
        """
        page_indices = self._compute_page_indices_with_today(date)
        # compute the batch_size!
        page_content = self.get_wjs_epidemic_tabel_data(page_indices=page_indices)
        parsed_page_data: TabelContentMatchResult = self.url_template_parser.parse_tabel_url_content(
            content=page_content
        )
        time.sleep(0.2)
        if isinstance(date,str):
            specify_date_string = date
            date = datetime.datetime.strptime(date,self.date_format)
        else:
            specify_date_string = date.strftime(self.date_format)
        epidemic_data_list = parsed_page_data.epidemic_data_list
        for sub_url, title, date_string in epidemic_data_list:
            sub_date = datetime.datetime.strptime(date_string,self.date_format)
            if (sub_date - date).days == 1:
                self.logger.info("analyse the data for -> {}".format(date_string))
                epidemic_data_url = self._safe_concat_urls(self.wjw_epidemic_root_url, sub_url)
                print(epidemic_data_url)
                data_frame_list, content_data_list = self.fetch_data_frame_data_list_by_specify_url(
                    epidemic_data_url=epidemic_data_url
                )
                source_save_dir = os.path.join(self.save_dir,specify_date_string)
                utility.check_and_create_dir_if_not_exsit(source_save_dir)
                excel_file_path = os.path.join(source_save_dir, "{}.xlsx".format(title))
                text_file_path = os.path.join(source_save_dir, "{}.txt".format(title))
                self._write_data_frame_list_to_file(
                    data_frame_list=data_frame_list,
                    save_path=excel_file_path
                )
                self.logger.info("write excel data -> {}".format(excel_file_path))
                with open(text_file_path, "w", encoding="utf-8") as f:
                    for content in content_data_list:
                        f.write(content)
                        f.write("\n")
                self.logger.info("write text data -> {}".format(text_file_path))
                break
            else:
                self.logger.info("the url for -> {} is not expected,we specify at -> {}".format(
                    specify_date_string,
                    date_string
                ))

    def _deserialize_date_string(self, date_string: str):
        return datetime.datetime.strptime(date_string, self.date_format)

    def _safe_concat_urls(self, lhs_url: str, rhs_url: str) -> str:
        if lhs_url.endswith("/"):
            lhs_url = lhs_url.strip("/")
        if rhs_url.startswith("/"):
            rhs_url = rhs_url.strip("/")
        return "{}/{}".format(lhs_url, rhs_url)

    def _compute_page_indices_with_today(self, date: datetime.datetime = None) -> int:
        """
        compute the page offset!
        """
        if isinstance(date,str):
            date = datetime.datetime.strptime(date,self.date_format)
        today = datetime.datetime.today()
        yesterday = today - datetime.timedelta(days=1)
        day_offset = (yesterday - date).days
        if day_offset < 0:
            error_info = "can not specify the future,today is {},but you give day -> {}".format(
                today.strftime(self.date_format),
                date.strftime(self.date_format)
            )
            self.logger.info(error_info)
            raise ValueError(error_info)
        page_indices = ((day_offset + 1) // self.epidemic_data_size_of_each_page) + 1
        return page_indices

    def _write_data_frame_list_to_file(self, data_frame_list: List[Tuple[str, pd.DataFrame]], save_path: str = None) -> None:
        for sheet_name,data_frame in data_frame_list:
            self.logger.info("{} -> {} ".format(sheet_name,data_frame))
        if save_path is None:
            save_path = "lazydog.xlsx"
        writer = pd.ExcelWriter(save_path)
        for sheet_name, data_frame in data_frame_list:
            data_frame.to_excel(writer, sheet_name=sheet_name, index=False)
        writer.save()


if __name__ == "__main__":
    wjs_fetcher = WjwEpidemicFetcher(
        epidemic_tabel_url="http://www.baidu.com",
        save_dir="wjw_epidemic_data"
    )
    url = "http://www.nhc.gov.cn/xcs/yqtb/202211/b741658e3325404ea22e74ab73e01637.shtml"
    content = wjs_fetcher._url_context_fetch(url)
    print(content)
