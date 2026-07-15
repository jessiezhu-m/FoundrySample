from __future__ import annotations

import argparse
import logging

from weather_digest.config import load_config
from weather_digest.scheduler import run_scheduler, send_daily_weather_digest


def main() -> None:
    parser = argparse.ArgumentParser(description="Send a daily Shanghai weather digest.")
    parser.add_argument(
        "--run-once",
        action="store_true",
        help="Send one digest immediately instead of starting the daily scheduler.",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    config = load_config()

    if args.run_once:
        send_daily_weather_digest(config)
        return

    run_scheduler(config)


if __name__ == "__main__":
    main()

