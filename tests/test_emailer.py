from weather_digest.emailer import build_weather_email


def test_build_weather_email_sets_expected_headers_and_body() -> None:
    message = build_weather_email(
        sender="weather@example.com",
        recipient="alias@microsoft.com",
        body="Shanghai is sunny today, good for commuting.",
    )

    assert message["From"] == "weather@example.com"
    assert message["To"] == "alias@microsoft.com"
    assert message["Subject"] == "Shanghai Weather and Travel Advice"
    assert message.get_content().strip() == "Shanghai is sunny today, good for commuting."

