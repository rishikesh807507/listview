"""
Master data collection dispatcher for Listview — Indian Stocks & IPO Intelligence Platform.
Runs all scheduled collectors in sequence.
Compatible with Windows Task Scheduler, Linux Cron, and GitHub Actions.
Usage:
  python collector.py
  python collector.py --task stocks
  python collector.py --task gmp
"""
import sys
import argparse
from collectors.stock_collector import collect_stocks
from collectors.historical_collector import collect_historical
from collectors.gmp_collector import collect_gmp
from collectors.ipo_collector import collect_ipos
from collectors.financial_collector import collect_financials
from collectors.news_collector import collect_news

def run_all():
    print("==================================================")
    print("Listview Data Collection Cycle Started")
    print("==================================================")
    print("\n[1/6] Running Stock Price Collector...")
    collect_stocks()
    print("\n[2/6] Running Historical Price Snapshot Collector...")
    collect_historical()
    print("\n[3/6] Running IPO GMP Open-Dataset Collector...")
    collect_gmp()
    print("\n[4/6] Running IPO Timeline & Status Collector...")
    collect_ipos()
    print("\n[5/6] Running Financials & Valuation Ratios Collector...")
    collect_financials()
    print("\n[6/6] Running Free Market News & Sentiment Collector...")
    collect_news()
    print("\n==================================================")
    print("[SUCCESS] Data collection cycle completed successfully.")
    print("==================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run zero-cost data collectors")
    parser.add_argument("--task", type=str, choices=["all", "stocks", "historical", "gmp", "ipos", "financials", "news"], default="all")
    args = parser.parse_args()

    if args.task == "all":
        run_all()
    elif args.task == "stocks":
        collect_stocks()
    elif args.task == "historical":
        collect_historical()
    elif args.task == "gmp":
        collect_gmp()
    elif args.task == "ipos":
        collect_ipos()
    elif args.task == "financials":
        collect_financials()
    elif args.task == "news":
        collect_news()
