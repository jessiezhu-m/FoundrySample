from __future__ import annotations

import logging
from datetime import datetime
from urllib.parse import quote
from zoneinfo import ZoneInfo

from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.identity import DefaultAzureCredential


logger = logging.getLogger(__name__)

AZURE_OPENAI_SCOPE = "https://cognitiveservices.azure.com/.default"


class FoundryWeatherClient:
    def __init__(self, endpoint: str, deployment: str, api_version: str) -> None:
        endpoint = _build_deployment_endpoint(endpoint, deployment)
        client_kwargs = {
            "endpoint": endpoint,
            "credential": DefaultAzureCredential(
                exclude_interactive_browser_credential=False
            ),
        }
        if _is_azure_openai_endpoint(endpoint):
            client_kwargs["credential_scopes"] = [AZURE_OPENAI_SCOPE]
            client_kwargs["api_version"] = api_version

        self._client = ChatCompletionsClient(**client_kwargs)
        self._model = None if _is_azure_openai_endpoint(endpoint) else deployment

    def get_shanghai_weather_digest(self) -> str:
        today = datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d")
        request = {
            "messages": [
                SystemMessage(
                    content=(
                        "You are a helpful daily weather assistant. "
                        "Return concise, practical information in English."
                    )
                ),
                UserMessage(
                    content=(
                        f"Today is {today}. Please query, or use any real-time data available to you, to tell me today’s weather conditions in Shanghai, China, and provide travel/commuting suggestions. Please include: weather overview, temperature range, rain/wind alerts, clothing recommendations, and commuting advice. If the current endpoint does not have real-time weather capability, please clearly state that limitation."
                    )
                ),
            ],
            "temperature": 0.2,
        }
        if self._model:
            request["model"] = self._model

        response = self._client.complete(**request)

        if not response.choices:
            raise RuntimeError("Foundry endpoint returned no choices.")

        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("Foundry endpoint returned an empty response.")

        logger.info("Foundry endpoint response content:\n%s", content)

        return content


def _build_deployment_endpoint(endpoint: str, deployment: str) -> str:
    endpoint = endpoint.rstrip("/")
    if _is_azure_openai_endpoint(endpoint) and "/openai/deployments/" not in endpoint:
        return f"{endpoint}/openai/deployments/{quote(deployment, safe='')}"
    return endpoint


def _is_azure_openai_endpoint(endpoint: str) -> bool:
    return ".openai.azure.com" in endpoint
