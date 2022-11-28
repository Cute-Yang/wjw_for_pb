from src.template_parse import UrlTempalteParser
from src.wjw_url_parse import WjwEpidemicFetcher

if __name__ == "__main__":
    template_parser = UrlTempalteParser(
        date_format="%Y-%m-%d"
    )
    wjw_fetcher = WjwEpidemicFetcher(
        epidemic_tabel_url_formatter="http://www.baidu.com",
        save_dir="wjw_epidemic_data",
        url_template_parser=template_parser
    )
    wjw_fetcher.fetch_data_frame_data_list_by_specify_url("lazydog")
    # url = "http://www.nhc.gov.cn/xcs/yqtb/202211/b741658e3325404ea22e74ab73e01637.shtml"
    # url = "http://www.nhc.gov.cn/xcs/yqtb/list_gzbd.shtml"
    # content = wjs_fetcher._url_context_fetch(url)
    # with open("test.html", "w", encoding="utf-8") as f:
    #     f.write(content)
    # with open("test.html", "r", encoding="utf-8") as f:
    #     content = f.read()

    # # s = template_parse.parse_epidemic_url_content(content=content)
    # # for i in s:
    # #     print(i)
    # #     print()
    # # if s is not None:
    # #     print(s.total_page)
    # #     print(s.current_page)
    # #     print(s.sizeof_items)
    # #     print(s.epidemic_data_list)
    # with open("p1.txt", "r", encoding="utf-8") as f:
    #     content = f.read()

    # s = template_parse.format_new_add_epidemic_instance(content=content)
    # print(s)
    # with open("p2.txt", "r", encoding="utf-8") as f:
    #     content = f.read()
    # print(template_parse.format_new_add_cure_instance(content=content))
