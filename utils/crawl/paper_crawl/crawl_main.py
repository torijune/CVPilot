import json
import importlib
import os

from utils.crawl.paper_crawl.crawlers.acl_crawler import acl_crawler
from utils.crawl.paper_crawl.crawlers.cvpr_crawler import cvpr_crawler
from utils.crawl.paper_crawl.crawlers.eccv_crawler import eccv_crawler
from utils.crawl.paper_crawl.crawlers.emnlp_crawler import emnlp_crawler
from utils.crawl.paper_crawl.crawlers.iccv_crawler import iccv_crawler
from utils.crawl.paper_crawl.crawlers.iclr_crawler import iclr_crawler
from utils.crawl.paper_crawl.crawlers.iccv_crawler import iccv_crawler
from utils.crawl.paper_crawl.crawlers.icml_crawler import icml_crawler
from utils.crawl.paper_crawl.crawlers.naacl_crawler import naacl_crawler
from utils.crawl.paper_crawl.crawlers.neurips_crawler import neurips_crawler

def main():
    base_dir = os.path.dirname(__file__)
    with open(os.path.join(base_dir, "conference_list.json"), "r", encoding="utf-8") as f:
        conf_data = json.load(f)

    all_results = []

    for field in conf_data["fields"]:
        field_name = field["field"]
        for conf in field["conferences"]:
            conf_name = conf["name"]
            conf_url = conf["site"]
            module_name = get_crawler_module(conf_name)
            if not module_name:
                print(f"[SKIP] {conf_name} (크롤러 미구현)")
                continue
            try:
                crawler = importlib.import_module(f"crawlers.{module_name}")
                print(f"[INFO] {field_name} - {conf_name} 크롤링 시작")
                papers = crawler.crawl_all_papers(conf_url)
                for paper in papers:
                    paper["field"] = field_name
                    paper["conference"] = conf_name
                all_results.extend(papers)
                print(f"[DONE] {conf_name}: {len(papers)}개 논문 크롤링")
            except Exception as e:
                print(f"[ERROR] {conf_name} 크롤링 실패: {e}")

    # 결과 저장 (예: 전체 논문을 하나의 JSON으로)
    with open(os.path.join(base_dir, "all_papers.json"), "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"총 {len(all_results)}개 논문 크롤링 완료!")

if __name__ == "__main__":
    main()