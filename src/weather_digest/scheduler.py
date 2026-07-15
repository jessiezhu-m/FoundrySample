from __future__ import annotations

import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from weather_digest.config import AppConfig
from weather_digest.emailer import AcsEmailSender, build_weather_email
from weather_digest.foundry_client import FoundryWeatherClient

logger = logging.getLogger(__name__)


def send_daily_weather_digest(config: AppConfig) -> None:
    logger.info("Requesting Shanghai weather digest from AI Foundry endpoint.")
    foundry_client = FoundryWeatherClient(
        endpoint=config.foundry_endpoint,
        deployment=config.foundry_deployment,
        api_version=config.foundry_api_version,
    )
    digest = foundry_client.get_shanghai_weather_digest()

    logger.info("Sending weather digest email to %s.", config.email_to)
    email_sender = AcsEmailSender(connection_string=config.acs_connection_string)
    message = build_weather_email(
        sender=config.email_from,
        recipient=config.email_to,
        body=digest,
    )
    email_sender.send(message)
    logger.info("Weather digest email sent.")


def run_scheduler(config: AppConfig) -> None:
    scheduler = BlockingScheduler(timezone=config.schedule_timezone)
    scheduler.add_job(
        send_daily_weather_digest,
        trigger=CronTrigger(
            hour=config.schedule_hour,
            minute=config.schedule_minute,
            timezone=config.schedule_timezone,
        ),
        args=[config],
        id="daily-shanghai-weather-digest",
        replace_existing=True,
    )

    logger.info(
        "Scheduler started. Daily job time: %02d:%02d %s.",
        config.schedule_hour,
        config.schedule_minute,
        config.schedule_timezone,
    )
    scheduler.start()
