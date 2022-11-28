import datetime
import re
from typing import List, Pattern, Tuple

from utils.wrap_logger import LogFactory, LoggerFileType


class TabelContentMatchResult(object):
    def __init__(self, total_page: int, current_page: int, sizeof_items: int,
                 epidemic_data_list: List[Tuple[str]] = None):
        self.total_page = total_page
        self.current_page = current_page
        self.sizeof_items = sizeof_items
        self.epidemic_data_list = epidemic_data_list


class NewAddParagraphParseResult(object):
    def __init__(self, total_new_add_size: int, outside_new_add_all_size: int, outside_new_add_detail_pairs: List,
                 outside_normal_2_positive_size: int, outside_normal_2_positive_detail_pairs: List,
                 local_new_add_all_size, local_new_add_detail_pairs: List,
                 local_normal_2_positive_size: int, local_normal_2_positive_detail_pairs: List,
                 dead_new_add_size: int, dead_outside_new_add: int, dead_local_new_add: int,
                 maybe_new_add_size: int, maybe_outside_new_add: int, maybe_local_new_add: int) -> None:

        self.total_new_add_size = total_new_add_size
        self.outside_new_add_all_size = outside_new_add_all_size
        self.outside_new_add_detail_pairs = outside_new_add_detail_pairs
        self.outside_normal_2_positive_size = outside_normal_2_positive_size
        self.outside_normal_2_positive_pairs = outside_normal_2_positive_detail_pairs
        self.local_new_add_all_size = local_new_add_all_size
        self.local_new_add_detail_pairs = local_new_add_detail_pairs
        self.local_normal_2_positive_size = local_normal_2_positive_size
        self.local_normal_2_positive_detail_pairs = local_normal_2_positive_detail_pairs
        self.dead_new_add_size = dead_new_add_size
        self.dead_outside_new_add = dead_outside_new_add
        self.dead_local_new_add = dead_local_new_add
        self.maybe_new_add_size = maybe_new_add_size
        self.maybe_outside_size = maybe_outside_new_add
        self.maybe_local_size = maybe_local_new_add


class OutsideAggParseResult(object):
    def __init__(self, current_outside_positive_instance=0,
                 # outside_severe_illness_instance = 0,
                 outside_maybe_positive_instance=0,
                 outside_accumulated_positive_instance=0,
                 outside_accumulated_cure_instance=0,
                 outside_dead_instance=0) -> None:
        self.currrent_outside_positive_instance = current_outside_positive_instance
        self.outside_maybe_positive_instance = outside_maybe_positive_instance
        self.outside_accumulated_cure_instance = outside_accumulated_cure_instance
        self.outside_accumulated_positive_instance = outside_accumulated_positive_instance
        self.outside_dead_instance = outside_dead_instance


class LocalAggParseResult(object):
    def __init__(self,  current_local_positive_size=0,
                 current_local_sereve_illness_size=0,
                 local_accumulated_cure_size=0,
                 local_accumulated_dead_size=0,
                 local_accumulated_positive_size=0,
                 local_maybe_positive_size=0,
                 local_accumulated_closely_size=0,
                 local_in_observation=0) -> None:
        self.current_local_sereve_illness_size = current_local_sereve_illness_size
        self.current_local_positive_size = current_local_positive_size
        self.local_accumulated_cure_size = local_accumulated_cure_size
        self.local_accumulated_dead_size = local_accumulated_dead_size
        self.local_accumulated_positive_size = local_accumulated_positive_size
        self.local_maybe_positive_size = local_maybe_positive_size
        self.local_accumulated_closely_size = local_accumulated_closely_size
        self.local_in_observation = local_in_observation


class CureParagraphParseResult(object):
    def __init__(self, cure_total_add_size: int, outside_cure_add_size: int, local_cure_add_size: int,
                 local_cure_detail_pairs: List, severe_illness_instance: int, sizeof_close_observation: int) -> None:
        self.cure_total_add_size = cure_total_add_size
        self.outside_cure_add_size = outside_cure_add_size
        self.local_cure_add_size = local_cure_add_size
        self.local_cure_detail_pairs = local_cure_detail_pairs
        self.severe_illness_instance = severe_illness_instance
        self.sizeof_close_observation = sizeof_close_observation


class AsymptomaticParseResult(object):
    def __init__(self, asymptomatic_add_total_size=0,
                 asymptomatic_local_add_size=0,
                 asymptomatic_outside_add_size=0,
                 asymptomatic_local_detail_pairs=[]) -> None:
        self.asymptomatic_add_total_size = asymptomatic_add_total_size
        self.asymptomatic_local_add_size = asymptomatic_local_add_size
        self.asymptomatic_outside_add_size = asymptomatic_outside_add_size
        self.asymptomatic_local_detail_pairs = asymptomatic_local_detail_pairs


class MedicalObservationParseResult(object):
    def __init__(self, close_observation_total_size=0,
                 close_outside_observaton_size=0,
                 close_local_observation_size=0,
                 close_local_detail_pairs=[],
                 transfer_2_postive_size=0,
                 outside_transfer_2_postive_size=0,
                 in_medical_observation_size=0,
                 outside_in_medical_observation_size=0) -> None:
        self.close_observation_total_size = close_observation_total_size
        self.close_outside_observaton_size = close_outside_observaton_size
        self.close_local_observation_size = close_local_observation_size
        self.close_local_detail_pairs = close_local_detail_pairs
        self.transfer_2_postive_size = transfer_2_postive_size
        self.outside_transfer_2_postive_size = outside_transfer_2_postive_size
        self.in_medical_observation_size = in_medical_observation_size
        self.outside_in_medical_observation_size = outside_in_medical_observation_size


class GATParseResult(object):
    def __init__(self, gat_accumulated_total_size=0,
                 hongkong_accumulate_total_size=0,
                 hongkong_out_hospital_size=0,
                 hongkong_dead_size=0,
                 aomen_accumulate_total_size=0,
                 aomen_out_hospital_size=0,
                 aomen_dead_size=0,
                 taiwan_accumulated_total_size=0,
                 taiwan_out_hospital_size=0,
                 taiwan_dead_size=0) -> None:
        self.gat_accumulated_total_size = gat_accumulated_total_size
        self.hongkong_accumulate_total_size = hongkong_accumulate_total_size
        self.hongkong_out_hospital_size = hongkong_out_hospital_size
        self.hongkong_dead_size = hongkong_dead_size
        self.aomen_accumulate_total_size = aomen_accumulate_total_size
        self.aomen_out_hospital_size = aomen_out_hospital_size
        self.aomen_dead_size = aomen_dead_size
        self.taiwan_accumulated_total_size = taiwan_accumulated_total_size
        self.taiwan_out_hospital_size = taiwan_out_hospital_size
        self.taiwan_dead_size = taiwan_dead_size


class UrlTempalteParser(object):
    def __init__(self, logger: LogFactory = None, date_format: str = None) -> None:
        if logger is None:
            print("you did not specify logger,we will create a default logger!")
            logger = LogFactory(
                log_dir="logs",
                log_prefix="wjw_template_parser.log",
                scope_name="wjw_template_parser",
                use_webhook=False,
                file_handler_type=LoggerFileType.RotateCategory
            )
        self.logger = logger
        self.date_format = date_format
        self.limit_size = 7

        self.daily_data_fetch_pattern_generic = re.compile(
            r"<li>  <a href=\"(.*?)\" target=\"_blank\" title=\"(.*?)\">.*?</a><span class=\".*?\">(.*?)</span></li>"
        )
        self.logger.info(self.daily_data_fetch_pattern_generic)

        self.daily_data_fetch_pattern_split_line = re.compile(
            r"<li class=\"line\">  <a href=\"(.*?)\" target=\"_blank\" title=\"(.*?)\">.*?</a><span class=\".*?\">(.*?)</span></li>"
        )
        self.logger.info(self.daily_data_fetch_pattern_split_line)

        self.page_divide_pattern = re.compile(
            r"<script type=\"text/javascript\" src=\"/xcs/xhtml/js/page\.js\"></script><script>window\.onload=function\(\) \{createPageHTML\('page_div',(\d+), (\d),'list_gzbd','shtml',(\d+)\);\}</script>"
        )
        self.logger.info(self.page_divide_pattern)

        # self.epidemic_data_pattern_generic = re.compile(
        #     r"<p style=.*?><span style=.*?>(.*?)</span><span style=.*?><o:p></o:p></span></p>"
        # )
        # self.logger.info(self.epidemic_data_pattern_generic)

        self.epidemic_data_pattern = re.compile(
            r"<p style=.*?><span style=.*?>(.*?)</span></p>"
        )
        self.logger.info(self.epidemic_data_pattern)

        # self.epidemic_data_pattern_third = r"<p style=.*?><span style=.*?><font face=.*?>(.*?)</span><span style=.*?><o:p></o:p></span></p>"
        # self.logger.info(self.epidemic_data_pattern_third)

        self.epidemic_data_strip_pattern_v1 = re.compile(r"<font face=.*?>|</font>")
        self.epidemic_data_strip_pattern_v2 = re.compile(r"</span><span style=.*?><o:p></o:p>")

        self.new_add_total_fetch_pattern = re.compile(
            r"\d{1,2}月\d{1,2}日0—24时，31个省（自治区、直辖市）和新疆生产建设兵团报告新增确诊病例(\d+)例。"
        )

        self.outside_new_add_template_pattern = re.compile(
            r"其中境外输入病例(\d+)例（(.*?)），含(\d+)例由无症状感染者转为确诊病例（(.*?)）；"
        )

        self.local_new_add_template_pattern = re.compile(
            r"本土病例(\d+)例（(.*?)），含(\d+)例由无症状感染者转为确诊病例（(.*?)）。"
        )

        self.dead_new_add_fetch_pattern_v1 = re.compile(
            r"新增死亡病例(\d+)例，其中境外输入病例(\d+)例（.*?），本土病例(\d+)例（.*?）。"
        )
        self.dead_new_add_fetch_pattern_v2 = re.compile(
            r"新增死亡病例(\d+)例，为境外输入病例.*?"
        )
        self.dead_new_add_fetch_pattern_v3 = re.compile(
            r"新增死亡病例(\d+)例，为本土病例.*?"
        )

        self.maybe_new_add_fetch_pattern_v1 = re.compile(
            r"新增疑似病例(\d+)例，其中境外输入病例(\d+)例（.*?），本土病例(\d+)例（.*?）。"
        )
        self.maybe_new_add_fetch_pattern_v2 = re.compile(
            r"新增疑似病例(\d+)例，为境外输入病例.*?。"
        )
        self.maybe_new_add_fetch_pattern_v3 = re.compile(
            r"新增疑似病例(\d+)例，为本土病例.*?。"
        )

        self.place_and_size_split_pattern = re.compile(
            r"(.*?)(\d+)例"
        )

        self.cure_new_add_fetch_pattern = re.compile(
            r"当日新增治愈出院病例(\d+)例，其中境外输入病例(\d+)例，本土病例(\d+)例（(.*?)），解除医学观察的密切接触者(\d+)人，重症病例较前一日(.*?)(\d+)例"
        )

        self.outside_agg_pattern_v1 = re.compile(
            r"境外输入现有确诊病例(\d+)例（.*?），无现有疑似病例。累计确诊病例(\d+)例，累计治愈出院病例(\d+)例，无死亡病例。"
        )
        self.outside_agg_pattern_v2 = re.compile(
            r"境外输入现有确诊病例(\d+)例（.*?），现有疑似病例(\d+)例.*?。累计确诊病例(\d+)例，累计治愈出院病例(\d+)例，无死亡病例。"
        )
        self.outside_agg_pattern_v3 = re.compile(
            r"境外输入现有确诊病例(\d+)例（.*?），无现有疑似病例。累计确诊病例(\d+)例，累计治愈出院病例(\d+)例，死亡病例。(\d+)例.*?"
        )
        self.outside_agg_pattern_v4 = re.compile(
            r"境外输入现有确诊病例(\d+)例（.*?），现有疑似病例(\d+)例.*?。累计确诊病例(\d+)例，累计治愈出院病例(\d+)例，死亡病例。(\d+)例.*"
        )

        self.local_agg_pattern_v1 = re.compile(
            r"截至\d{1,2}月\d{1,2}日24时，据31个省（自治区、直辖市）和新疆生产建设兵团报告，现有确诊病例(\d+)例（其中重症病例(\d+)例），累计治愈出院病例(\d+)例，累计死亡病例(\d+)例，累计报告确诊病例(\d+)例，现有疑似病例(\d+)例。累计追踪到密切接触者(\d+)人，尚在医学观察的密切接触者(\d+)人。"
        )
        self.local_agg_pattern_v2 = re.compile(
            r"截至\d{1,2}月\d{1,2}日24时，据31个省（自治区、直辖市）和新疆生产建设兵团报告，现有确诊病例(\d+)例（其中重症病例(\d+)例），累计治愈出院病例(\d+)例，累计死亡病例(\d+)例，累计报告确诊病例(\d+)例，无疑似病例。累计追踪到密切接触者(\d+)人，尚在医学观察的密切接触者(\d+)人。"
        )
        self.local_agg_pattern_v3 = re.compile(
            r"截至\d{1,2}月\d{1,2}日24时，据31个省（自治区、直辖市）和新疆生产建设兵团报告，现有确诊病例(\d+)例（无重症病例），累计治愈出院病例(\d+)例，累计死亡病例(\d+)例，累计报告确诊病例(\d+)例，现有疑似病例(\d+)例。累计追踪到密切接触者(\d+)人，尚在医学观察的密切接触者(\d+)人。"
        )
        self.local_agg_pattern_v4 = re.compile(
            r"截至\d{1,2}月\d{1,2}日24时，据31个省（自治区、直辖市）和新疆生产建设兵团报告，现有确诊病例(\d+)例（无重症病例），累计治愈出院病例(\d+)例，累计死亡病例(\d+)例，累计报告确诊病例(\d+)例，无疑似病例。累计追踪到密切接触者(\d+)人，尚在医学观察的密切接触者(\d+)人。"
        )

        self.asymptomatic_add_pattern_v1 = re.compile(
            r"31个省（自治区、直辖市）和新疆生产建设兵团报告新增无症状感染者(\d+)例，其中境外输入(\d+)例，本土(\d+)例（(.*?)）。"
        )

        self.close_medical_observation_pattern_v1 = re.compile(
            r"当日解除医学观察的无症状感染者(\d+)例，其中境外输入(\d+)例，本土(\d+)例（(.*?)）；当日转为确诊病例(\d+)例（境外输入(\d+)例）；尚在医学观察的无症状感染者(\d+)例（境外输入(\d+)例）。"
        )

        self.gat_positive_pattern_v1 = re.compile(
            r"累计收到港澳台地区通报确诊病例(\d+)例。其中，香港特别行政区(\d+)例（出院(\d+)例，死亡(\d+)例），澳门特别行政区(\d+)例（出院(\d+)例，死亡(\d+)例），台湾地区(\d+)例（出院(\d+)例，死亡(\d+)例）。"
        )

    def _remove_chinese_comma(self, content: str) -> str:
        return content.replace("，", "")

    def parse_tabel_url_content(self, content: str = None):
        page_divide_match_result = re.findall(self.page_divide_pattern, content)
        if len(page_divide_match_result) == 0:
            self.logger.info("failed to match with page divided pattern!")
            return None
        total_page, current_page, sizeof_items = page_divide_match_result[0]

        epidemic_item_list_v1 = re.findall(
            self.daily_data_fetch_pattern_generic,
            content
        )
        if len(epidemic_item_list_v1) == 0:
            self.logger.info("failed to finda epidemic v1 data from current content!")

        epidemic_item_list_v2 = re.findall(
            self.daily_data_fetch_pattern_split_line,
            content
        )
        if len(epidemic_item_list_v2) == 0:
            self.logger.info("failed to finda epidemic v2 data from current content!")

        epidemic_item_list = []
        epidemic_item_list.extend(epidemic_item_list_v1)
        epidemic_item_list.extend(epidemic_item_list_v2)

        return TabelContentMatchResult(
            total_page=total_page,
            current_page=current_page,
            sizeof_items=sizeof_items,
            epidemic_data_list=epidemic_item_list
        )

    def parse_epidemic_url_content(self, content: str = None) -> str:
        # epidemic_data_list_generic = re.findall(
        #     self.epidemic_data_pattern_generic,
        #     content
        # )
        # if len(epidemic_data_list_generic) == 0:
        #     self.logger.info("failed to match from epidemic_data!")

        epidemic_data_list = re.findall(
            self.epidemic_data_pattern,
            content
        )
        if len(epidemic_data_list) == 0:
            self.logger.info("faield to match HK data from content!")

        # epidemic_data_list_third = re.findall(
        #     self.epidemic_data_pattern_third,
        #     content
        # )
        # if len(epidemic_data_list_third) == 0:
        #     self.logger.info("failed to match data with patter -> {}".format(self.epidemic_data_pattern_third))

        # epidemic_data_list = []
        # epidemic_data_list.extend(epidemic_data_list_generic)
        # epidemic_data_list.extend(epidemic_data_list_HK_AM_TW)
        if len(epidemic_data_list) > self.limit_size:
            epidemic_data_list = epidemic_data_list[:self.limit_size]
        epidemic_data_list = [re.sub(self.epidemic_data_strip_pattern_v1, "", x) for x in epidemic_data_list]
        epidemic_data_list = [re.sub(self.epidemic_data_strip_pattern_v2, "", x) for x in epidemic_data_list]
        return epidemic_data_list

    def _deserialize_date_string(self, date_string: str = None):
        return datetime.datetime.strptime(date_string, self.date_format)

    def _int_and_string_pair_transform(self, pairs: List) -> None:
        for indices, pair in enumerate(pairs):
            pairs[indices] = (pair[0], int(pair[1]))

    def _find_add_detail_pair_core(self, content: str, fetch_pattern: Pattern, op_name: str = None) -> Tuple:
        new_add_all = 0
        new_add_detail_pairs = []
        normal_2_positive_size = 0
        new_add_detail_pairs = []
        new_add_instance_data_list = re.findall(
            fetch_pattern,
            content
        )
        if len(new_add_instance_data_list) > 0:
            new_add_all, new_add_detail,\
                normal_2_positive_size, normal_2_positive_detail = new_add_instance_data_list[0]
            new_add_all: int = int(new_add_all)
            new_add_detail: str = self._remove_chinese_comma(new_add_detail)
            new_add_detail_pairs: List = re.findall(self.place_and_size_split_pattern, new_add_detail)
            self._int_and_string_pair_transform(new_add_detail_pairs)
            normal_2_positive_size: int = int(normal_2_positive_size)
            normal_2_positive_detail: str = self._remove_chinese_comma(normal_2_positive_detail)
            normal_2_positive_detail_pairs: List = re.findall(
                self.place_and_size_split_pattern, normal_2_positive_detail)
            self._int_and_string_pair_transform(normal_2_positive_detail_pairs)
            self.logger.info("{} new add all -> {},add pairs -> {},outside normal_2_postive -> {}, outside normal_2_positive -> {}".format(
                op_name,
                new_add_all,
                new_add_detail_pairs,
                normal_2_positive_size,
                normal_2_positive_detail_pairs
            ))
        return new_add_all, new_add_detail_pairs, normal_2_positive_size, normal_2_positive_detail_pairs

    def format_new_add_epidemic_instance(self, content: str) -> NewAddParagraphParseResult:
        total_new_add_instance_data_list = re.findall(
            self.new_add_total_fetch_pattern,
            content
        )
        total_new_add_instance_size = 0
        if len(total_new_add_instance_data_list) > 0:
            total_new_add_instance_size: int = int(total_new_add_instance_data_list[0])
            self.logger.info("find total new add instance -> {}".format(total_new_add_instance_size))

        outside_new_add_all, outside_new_add_detail_pairs,\
            outside_normal_2_positive_size, outside_normal_2_positive_detail_pairs = self._find_add_detail_pair_core(
                content=content,
                fetch_pattern=self.outside_new_add_template_pattern,
                op_name="outside instance"
            )

        local_new_add_all, local_new_add_detail_pairs,\
            local_normal_2_positive_size, local_normal_2_positive_detail_pairs = self._find_add_detail_pair_core(
                content=content,
                fetch_pattern=self.local_new_add_template_pattern,
                op_name="local instance"
            )

        dead_new_add_size, dead_outside_new_add, dead_local_new_add = 0, 0, 0
        dead_new_add_data_list = re.findall(
            self.dead_new_add_fetch_pattern_v1,
            content
        )
        if len(dead_new_add_data_list) > 0:
            dead_new_add_size, dead_outside_new_add, dead_local_new_add = dead_new_add_data_list[0]
            dead_new_add_size = int(dead_new_add_size)
            dead_outside_new_add = int(dead_outside_new_add)
            dead_local_new_add = int(dead_local_new_add)
        else:
            dead_new_add_data_list = re.findall(
                self.dead_new_add_fetch_pattern_v2,
                content
            )
            if len(dead_new_add_data_list) > 0:
                dead_new_add_size = int(dead_new_add_data_list[0])
                dead_outside_new_add = dead_new_add_size
                dead_local_new_add = 0
            else:
                dead_new_add_data_list = re.findall(
                    self.dead_new_add_fetch_pattern_v3,
                    content
                )
                if len(dead_new_add_data_list) > 0:
                    dead_new_add_size = int(dead_new_add_data_list[0])
                    dead_outside_new_add = 0
                    dead_local_new_add = dead_new_add_size

        self.logger.info("dead new add size -> {}".format(dead_new_add_size))

        maybe_new_add_size, maybe_outside_new_add, maybe_local_new_add = 0, 0, 0
        maybe_new_add_data_list = re.findall(
            self.maybe_new_add_fetch_pattern_v1,
            content
        )
        if len(maybe_new_add_data_list) > 0:
            maybe_new_add_size, maybe_outside_new_add, maybe_local_new_add = maybe_new_add_data_list[0]
            maybe_new_add_size = int(maybe_new_add_size)
            maybe_outside_new_add = int(maybe_outside_new_add)
            maybe_local_new_add = int(maybe_local_new_add)
        else:
            maybe_new_add_data_list = re.findall(
                self.maybe_new_add_fetch_pattern_v2,
                content
            )
            if len(maybe_new_add_data_list) > 0:
                maybe_new_add_size = int(maybe_new_add_data_list[0])
                maybe_outside_new_add = maybe_new_add_size
                maybe_local_new_add = 0
            else:
                maybe_new_add_data_list = re.findall(
                    self.maybe_new_add_fetch_pattern_v3,
                    content
                )
                if len(maybe_new_add_data_list) > 0:
                    maybe_new_add_size = int(maybe_new_add_data_list[0])
                    maybe_local_new_add = maybe_new_add_size
                    maybe_outside_new_add = 0
        # self.logger.info("maybe new add size -> {},outside -> {},local -> {}".format(
        #     maybe_new_add_size,
        #     maybe_outside_new_add,
        #     maybe_local_new_add
        # ))

        return NewAddParagraphParseResult(
            total_new_add_size=total_new_add_instance_size,
            outside_new_add_all_size=outside_new_add_all,
            outside_new_add_detail_pairs=outside_new_add_detail_pairs,
            outside_normal_2_positive_size=outside_normal_2_positive_size,
            outside_normal_2_positive_detail_pairs=outside_normal_2_positive_detail_pairs,
            local_new_add_all_size=local_new_add_all,
            local_new_add_detail_pairs=local_new_add_detail_pairs,
            local_normal_2_positive_size=local_normal_2_positive_size,
            local_normal_2_positive_detail_pairs=local_normal_2_positive_detail_pairs,
            dead_new_add_size=dead_new_add_size,
            dead_local_new_add=dead_local_new_add,
            dead_outside_new_add=dead_outside_new_add,
            maybe_new_add_size=maybe_new_add_size,
            maybe_local_new_add=maybe_local_new_add,
            maybe_outside_new_add=maybe_outside_new_add
        )

    def format_new_add_cure_instance(self, content: str):
        cure_total_add_size = 0
        outside_cure_add_size = 0
        local_cure_add_size = 0
        local_cure_detail_pairs = []
        severe_illness_instance = 0
        sizeof_close_observation = 0
        cure_data_list = re.findall(
            self.cure_new_add_fetch_pattern,
            content
        )
        if len(cure_data_list) > 0:
            print(cure_data_list)
            cure_total_add_size, outside_cure_add_size, local_cure_add_size,\
                local_cure_detail, sizeof_close_observation, binary_op_name, severe_illness_instance = cure_data_list[0]

            sizeof_close_observation = int(sizeof_close_observation)
            cure_total_add_size = int(cure_total_add_size)
            outside_cure_add_size = int(outside_cure_add_size)
            local_cure_add_size = int(local_cure_add_size)
            local_cure_detail = self._remove_chinese_comma(local_cure_detail)
            local_cure_detail_pairs = re.findall(self.place_and_size_split_pattern, local_cure_detail)
            print(local_cure_detail_pairs)
            self._int_and_string_pair_transform(local_cure_detail_pairs)
            if binary_op_name == "增加":
                severe_illness_instance = int(severe_illness_instance)
            elif binary_op_name == "减少":
                severe_illness_instance = -int(severe_illness_instance)
            else:
                self.logger.info("unknown binary op name -> {} for severe illness instance!".format(severe_illness_instance))

        self.logger.info("cure total -> {},outside -> {},local -> {},detail pairs -> {},close obsevation -> {},severe illness -> {}".format(
            cure_total_add_size,
            outside_cure_add_size,
            local_cure_add_size,
            local_cure_detail_pairs,
            sizeof_close_observation,
            severe_illness_instance
        ))
        return CureParagraphParseResult(
            cure_total_add_size=cure_total_add_size,
            outside_cure_add_size=outside_cure_add_size,
            local_cure_add_size=local_cure_add_size,
            local_cure_detail_pairs=local_cure_detail_pairs,
            severe_illness_instance=severe_illness_instance,
            sizeof_close_observation=sizeof_close_observation
        )

    def format_outside_agg(self, content: str) -> OutsideAggParseResult:
        current_outside_positive_instance = 0
        # outside_severe_illness_instance = 0
        outside_maybe_positive_instance = 0
        outside_accumulated_positive_instance = 0
        outside_accumulated_cure_instance = 0
        outside_dead_instance = 0

        outside_agg_data_list = re.findall(
            self.outside_agg_pattern_v1,
            content
        )
        if len(outside_agg_data_list) > 0:
            current_outside_positive_instance, outside_accumulated_positive_instance,\
                outside_accumulated_cure_instance = outside_agg_data_list[0]
            current_outside_positive_instance = int(current_outside_positive_instance)
            outside_accumulated_positive_instance = int(outside_accumulated_positive_instance)
            outside_accumulated_cure_instance = int(outside_accumulated_cure_instance)
        else:
            outside_agg_data_list = re.findall(
                self.outside_agg_pattern_v2,
                content
            )
            if len(outside_agg_data_list) > 0:
                current_outside_positive_instance, outside_maybe_positive_instance,\
                    outside_accumulated_positive_instance, outside_accumulated_cure_instance = outside_agg_data_list[0]
                current_outside_positive_instance = int(current_outside_positive_instance)
                outside_accumulated_positive_instance = int(outside_accumulated_positive_instance)
                outside_accumulated_cure_instance = int(outside_accumulated_cure_instance)
                outside_maybe_positive_instance = int(outside_maybe_positive_instance)
            else:
                if len(outside_agg_data_list) > 0:
                    current_outside_positive_instance, outside_accumulated_positive_instance,\
                        outside_accumulated_cure_instance, outside_dead_instance = outside_agg_data_list[0]
                    current_outside_positive_instance = int(current_outside_positive_instance)
                    outside_accumulated_positive_instance = int(outside_accumulated_positive_instance)
                    outside_accumulated_cure_instance = int(outside_accumulated_cure_instance)
                    outside_dead_instance = int(outside_dead_instance)
                else:
                    outside_agg_data_list = re.findall(
                        self.outside_agg_pattern_v4,
                        content
                    )
                    if len(outside_agg_data_list):
                        current_outside_positive_instance, outside_maybe_positive_instance,\
                            outside_accumulated_positive_instance, outside_accumulated_cure_instance, outside_dead_instance = outside_agg_data_list[0]
                        current_outside_positive_instance = int(current_outside_positive_instance)
                        outside_accumulated_positive_instance = int(outside_accumulated_positive_instance)
                        outside_accumulated_cure_instance = int(outside_accumulated_cure_instance)
                        outside_dead_instance = int(outside_dead_instance)
                        outside_maybe_positive_instance = int(outside_maybe_positive_instance)
                    else:
                        self.logger.info("find nothing for outside agg info!")
        return OutsideAggParseResult(
            current_outside_positive_instance=current_outside_positive_instance,
            outside_maybe_positive_instance=outside_maybe_positive_instance,
            outside_accumulated_positive_instance=outside_accumulated_positive_instance,
            outside_accumulated_cure_instance=outside_accumulated_cure_instance,
            outside_dead_instance=outside_dead_instance
        )

    def format_local_agg(self, content: str):
        local_agg_data_list = []
        current_local_positive_size = 0
        current_local_sereve_illness_size = 0
        local_accumulated_cure_size = 0
        local_accumulated_dead_size = 0
        local_accumulated_positive_size = 0
        local_maybe_positive_size = 0
        local_accumulated_closely_size = 0
        local_in_observation = 0

        local_agg_data_list = re.findall(
            self.local_agg_pattern_v1,
            content
        )
        if len(local_agg_data_list) > 0:
            current_local_positive_size, current_local_sereve_illness_size, local_accumulated_cure_size,\
                local_accumulated_dead_size, local_accumulated_positive_size, local_maybe_positive_size,\
                local_accumulated_closely_size, local_in_observation = local_agg_data_list[0]
        else:
            local_agg_data_list = re.findall(
                self.local_agg_pattern_v2,
                content
            )
            if len(local_agg_data_list) > 0:
                current_local_positive_size, current_local_sereve_illness_size, local_accumulated_cure_size,\
                    local_accumulated_dead_size, local_accumulated_positive_size, local_accumulated_closely_size,\
                    local_in_observation = local_agg_data_list[0]
            else:
                local_agg_data_list = re.findall(
                    self.local_agg_pattern_v3,
                    content
                )
                if len(local_agg_data_list) > 0:
                    current_local_positive_size, local_accumulated_cure_size,\
                        local_accumulated_dead_size, local_accumulated_positive_size, local_maybe_positive_size,\
                        local_accumulated_closely_size, local_in_observation = local_agg_data_list[0]
                else:
                    local_agg_data_list = re.findall(
                        self.local_agg_pattern_v3,
                        content
                    )
                    if len(local_agg_data_list) > 0:
                        current_local_positive_size, local_accumulated_cure_size,\
                            local_accumulated_dead_size, local_accumulated_positive_size, local_maybe_positive_size,\
                            local_accumulated_closely_size, local_in_observation = local_agg_data_list[0]
        return LocalAggParseResult(
            current_local_positive_size=int(current_local_positive_size),
            local_accumulated_closely_size=int(local_accumulated_closely_size),
            local_accumulated_dead_size=int(local_accumulated_dead_size),
            local_accumulated_positive_size=int(local_accumulated_positive_size),
            local_maybe_positive_size=int(local_maybe_positive_size),
            local_in_observation=int(local_in_observation),
            current_local_sereve_illness_size=int(current_local_sereve_illness_size),
            local_accumulated_cure_size=int(local_accumulated_cure_size)
        )

    def format_asymptomatic(self, content: str) -> AsymptomaticParseResult:
        asymptomatic_add_total_size = 0
        asymptomatic_local_add_size = 0
        asymptomatic_outside_add_size = 0
        asymptomatic_local_detail_pairs = []

        asymptomatic_data_list = []
        asymptomatic_data_list = re.findall(
            self.asymptomatic_add_pattern_v1,
            content
        )
        if len(asymptomatic_data_list) > 0:
            asymptomatic_add_total_size, asymptomatic_outside_add_size, asymptomatic_local_add_size,\
                asymptomatic_local_detail = asymptomatic_data_list[0]
            asymptomatic_local_detail = self._remove_chinese_comma(asymptomatic_local_detail)
            asymptomatic_local_detail_pairs = re.findall(self.place_and_size_split_pattern, asymptomatic_local_detail)
            self._int_and_string_pair_transform(asymptomatic_local_detail_pairs)
        return AsymptomaticParseResult(
            asymptomatic_add_total_size=int(asymptomatic_add_total_size),
            asymptomatic_local_add_size=int(asymptomatic_local_add_size),
            asymptomatic_outside_add_size=int(asymptomatic_outside_add_size),
            asymptomatic_local_detail_pairs=asymptomatic_local_detail_pairs
        )

    def format_medical_obsevation(self, content) -> MedicalObservationParseResult:
        close_observation_total_size = 0
        close_outside_observaton_size = 0
        close_local_observation_size = 0
        close_local_detail_pairs = []
        transfer_2_postive_size = 0
        outside_transfer_2_postive_size = 0
        in_medical_observation_size = 0
        outside_in_medical_observation_size = 0

        medical_observation_data_list = []
        medical_observation_data_list = re.findall(
            self.close_medical_observation_pattern_v1,
            content
        )
        if len(medical_observation_data_list) > 0:
            close_observation_total_size, close_outside_observaton_size, close_local_observation_size, close_local_detail,\
                transfer_2_postive_size, outside_transfer_2_postive_size, in_medical_observation_size,\
                outside_in_medical_observation_size = medical_observation_data_list[0]

            close_local_detail = self._remove_chinese_comma(close_local_detail)
            close_local_detail_pairs = re.findall(self.place_and_size_split_pattern, close_local_detail)
        return MedicalObservationParseResult(
            close_observation_total_size=int(close_observation_total_size),
            close_outside_observaton_size=int(close_outside_observaton_size),
            close_local_observation_size=int(close_local_observation_size),
            close_local_detail_pairs=close_local_detail_pairs,
            transfer_2_postive_size=int(transfer_2_postive_size),
            outside_transfer_2_postive_size=int(outside_transfer_2_postive_size),
            in_medical_observation_size=int(in_medical_observation_size),
            outside_in_medical_observation_size=int(outside_in_medical_observation_size)
        )

    def format_gat(self, content):
        gat_accumulated_total_size = 0
        hongkong_accumulate_total_size = 0
        hongkong_out_hospital_size = 0
        hongkong_dead_size = 0
        aomen_accumulate_total_size = 0
        aomen_out_hospital_size = 0
        aomen_dead_size = 0
        taiwan_accumulated_total_size = 0
        taiwan_out_hospital_size = 0
        taiwan_dead_size = 0

        gat_data_list = []
        gat_data_list = re.findall(
            self.gat_positive_pattern_v1,
            content
        )
        if len(gat_data_list) > 0:
            gat_accumulated_total_size, hongkong_accumulate_total_size, hongkong_out_hospital_size,\
                hongkong_dead_size, aomen_accumulate_total_size, aomen_out_hospital_size, aomen_dead_size,\
                taiwan_accumulated_total_size, taiwan_out_hospital_size, taiwan_dead_size = gat_data_list[0]
        return GATParseResult(
            gat_accumulated_total_size=int(gat_accumulated_total_size),
            hongkong_accumulate_total_size=int(hongkong_accumulate_total_size),
            hongkong_out_hospital_size=int(hongkong_out_hospital_size),
            hongkong_dead_size=int(hongkong_dead_size),
            aomen_accumulate_total_size=int(aomen_accumulate_total_size),
            aomen_out_hospital_size=int(aomen_out_hospital_size),
            aomen_dead_size=int(aomen_dead_size),
            taiwan_accumulated_total_size=int(taiwan_accumulated_total_size),
            taiwan_out_hospital_size=int(taiwan_out_hospital_size),
            taiwan_dead_size=int(taiwan_dead_size)
        )
