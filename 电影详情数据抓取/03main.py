import os.path
import re

import requests
import csv
from lxml import html
from typing_extensions import runtime

# 目标
MAIN_URL = "https://www.themoviedb.org"  # 主页网站
URL_GOAL = "https://www.themoviedb.org/movie/top-rated"  # 获取电影 第一页数据
TMDB_TOP_URL_2 = "https://www.themoviedb.org/discover/movie/items"  # 获取电影 第二页之后数据
DATA_PAGE = "air_date.gte=&air_date.lte=&certification=&certification_country=CN&debug=&first_air_date.gte=&first_air_date.lte=&include_adult=false&include_softcore=false&latest_ceremony.gte=&latest_ceremony.lte=&page=%s&primary_release_date.gte=&primary_release_date.lte=&region=&release_date.gte=&release_date.lte=2026-12-26&show_me=everything&sort_by=vote_average.desc&vote_average.gte=0&vote_average.lte=10&vote_count.gte=300&watch_region=CN&with_genres=&with_keywords=&with_networks=&with_origin_country=&with_original_language=&with_watch_monetization_types=&with_watch_providers=&with_release_type=&with_runtime.gte=0&with_runtime.lte=400"


def requests_get_mainpage(URL_GOAL, address="csv_datas/movie_list.csv"):
    """
    将电影列表保存在address文件中
    :param url:主页网站地址
    :return: None
    """

    # 访问网站获取响应
    print(f"访问网站, 获取TMDB电影榜单数据 ...")

    html_main = requests.get(URL_GOAL, timeout=60)

    # 解析数据
    doc_html_main = html.fromstring(html_main.text)
    movie_list = doc_html_main.xpath("//a[@data-media-type='movie' and @class='flex w-full']/@href")
    movienames_list = doc_html_main.xpath("//a[@data-media-type='movie' and @class='flex w-full']/div/img/@alt")
    # 保存电影列表
    if os.path.exists('csv_datas'):
        pass
    else:
        os.mkdir('csv_datas')
    with open(address, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, ["电影名称", "电影链接"])
        writer.writeheader()
        for i in range(len(movienames_list)):
            writer.writerow({"电影名称": movienames_list[i], "电影链接": MAIN_URL + movie_list[i]})
    print("保存电影列表成功")


def requests_post_page(TMDB_TOP_URL_2, pagemax=2, data_page=DATA_PAGE, address="csv_datas/movie_list.csv"):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    for page in range(2, pagemax + 1):

        data_page_ = data_page % str(page)
        print(f"访问第{page}页数据...")
        page_html = requests.post(TMDB_TOP_URL_2, data=data_page_)
        doc_page = html.fromstring(page_html.text)
        movie_list = doc_page.xpath("//a[@data-media-type='movie' and @class='flex w-full']/@href")
        movienames_list = doc_page.xpath("//a[@data-media-type='movie' and @class='flex w-full']/div/img/@alt")
        # 保存电影列表
        if os.path.exists('csv_datas'):
            pass
        else:
            os.mkdir('csv_datas')
        with open(address, "a+", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, ["电影名称", "电影链接"])
            for i in range(len(movienames_list)):
                writer.writerow({"电影名称": movienames_list[i], "电影链接": MAIN_URL + movie_list[i]})
        print("保存电影列表成功")


def movieDetails(param) -> dict:
    """

    :param param:
    :return: movie_info，电影详情
    “电影名称”:{
                "年份":movieyear,
                "上映时间":moviereleasetime,
                "电影类型":moviegenres,
                "电影时长":movieruntime,
                "评分":moviescore_percent,
                "语言":movielanguage,
                "作者":peopledict,
                "简介":movierevew,
                "标签":movietagline,
                }
                """
    movie_info = {}
    with open(param, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            moviename = row['电影名称']
            html_movie = requests.get(row["电影链接"])
            print(f"访问{moviename}:{row["电影链接"]}网站, 获取电影详情数据 ...")
            doc_html_movie = html.fromstring(html_movie.text)
            # 解析数据
            # moviename = doc_html_movie.xpath("//section/div/h2/a/text()")
            movieyear = doc_html_movie.xpath("//section/div/h2/span/text()")
            moviereleasetime = doc_html_movie.xpath("//section/div/div/span[@class='release']/text()")
            moviegenres = doc_html_movie.xpath("//section/div/div/span[@class='genres']/a/text()")
            movieruntime = doc_html_movie.xpath("//section/div/div/span[@class='runtime']/text()")
            moviescore_percent = doc_html_movie.xpath("//div[@class='user_score_chart']/@data-percent")
            movielanguage = doc_html_movie.xpath(
                "//section[@class = 'facts left_column']/p[strong/bdi[contains(text(), '默认语言')]]/text()")
            movie_peoplelist = doc_html_movie.xpath("//ol[@class = 'people no_image']/li")
            movierevew = doc_html_movie.xpath(
                "//section[@class = 'header poster']//div//div[@class = 'overview']/p/text()")
            movietagline = doc_html_movie.xpath("//section[@class = 'header poster']/div/h3[@class = 'tagline']/text()")

            # 获取制作组
            peopledict = {}
            for movie_people in movie_peoplelist:
                movie_people_name = movie_people.xpath(".//p/a/text()")
                movie_people_role = movie_people.xpath(".//p/text()")
                peopledict.update({movie_people_name[0] if movie_people_name else "": movie_people_role[
                    0] if movie_people_role else ""})
            # 保存获取到的数据
            movie_info.update(
                {moviename.strip() if moviename else "": {"年份": movieyear[0].strip() if movieyear else "",
                                                          "上映时间": moviereleasetime[
                                                              0].strip() if moviereleasetime else "",
                                                          "电影类型": "、".join(
                                                              moviegenres).strip() if moviegenres else "",
                                                          "电影时长": movieruntime[0].strip() if movieruntime else "",
                                                          "评分": moviescore_percent[
                                                              0].strip() if moviescore_percent else "",
                                                          "语言": movielanguage[0].strip() if movielanguage else "",
                                                          "制作组": peopledict if peopledict else "",
                                                          "简介": movierevew[0].strip() if movierevew else "",
                                                          "宣传语": movietagline[0].strip() if movietagline else ""

                                                          }})
    print("保存电影详情成功")
    return movie_info


def sava_movie_info(param, movie_info):
    """
    保存电影详情
    :param param:文件保存路径
    :param movie_info:保存信息
    :return:None
    """
    with open(param, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, ["电影名称", "年份", "上映时间", "电影类型", "电影时长", "评分", "语言", "制作组",
                                       "简介", "宣传语"])
        movienames = movie_info.items()
        writer.writeheader()
        for movie_name, movie_detail in movie_info.items():
            print(f"保存电影详情:{movie_name}...")
            writer.writerow({
                "电影名称": movie_name,
                "年份": movie_detail.get("年份", ""),
                "上映时间": movie_detail.get("上映时间", ""),
                "电影类型": movie_detail.get("电影类型", ""),
                "电影时长": movie_detail.get("电影时长", ""),
                "评分": movie_detail.get("评分", ""),
                "语言": movie_detail.get("语言", ""),
                "制作组": str(movie_detail.get("制作组", "")),
                "简介": movie_detail.get("简介", ""),
                "宣传语": movie_detail.get("宣传语", "")
            })
            print(f"保存{movie_name}电影详情成功")


def datas_cleaning(param):
    """
    数据清洗
    :param param:文件保存路径
    :return:None
    """
    tag = True
    with open(param, "r", encoding="utf-8") as file :
        reader = csv.DictReader(file)
        for row in reader:
            year = re.findall(r"\d{4}",row["年份"])
            releasetime = re.findall(r"\d{4}-\d{2}-\d{2}",row["上映时间"])
            runtime_h = re.findall(r"(\d{1,})h",row["电影时长"])
            runtime_m = re.findall(r"(\d{1,})m",row["电影时长"])
            row["年份"] = year[0] if year else ""
            row["上映时间"] = releasetime[0] if releasetime else ""
            if runtime_h and runtime_m:
                row["电影时长"] = int(runtime_h[0]) * 60 + int(runtime_m[0])
            elif runtime_h:
                row["电影时长"] = int(runtime_h[0]) * 60
            elif runtime_m:
                row["电影时长"] = int(runtime_m[0])
            if tag:
                with open("csv_datas/movie_info.csv", "w", encoding="utf-8", newline="") as filesava :
                    writer = csv.DictWriter(filesava, ["电影名称", "年份", "上映时间", "电影类型", "电影时长", "评分", "语言", "制作组",
                                       "简介", "宣传语"])
                    writer.writeheader()
                    writer.writerow(row)
                tag = False
            else:
                with open("csv_datas/movie_info.csv", "a", encoding="utf-8", newline="") as filesava :
                    writer = csv.DictWriter(filesava, ["电影名称", "年份", "上映时间", "电影类型", "电影时长", "评分", "语言", "制作组",
                                       "简介", "宣传语"])
                    writer.writerow(row)

def main():
    # 获取电影列表,并保存在csv文件中
    requests_get_mainpage(URL_GOAL)
    # 获取分页电影列表
    requests_post_page(TMDB_TOP_URL_2, 5)
    # 获取电影详情
    movie_info = movieDetails("csv_datas/movie_list.csv")
    # 保存电影详情
    sava_movie_info("csv_datas/movie_info_rawdata.csv", movie_info)
    # 数据清洗
    datas_cleaning("csv_datas/movie_info_rawdata.csv")

if __name__ == '__main__':
    main()
