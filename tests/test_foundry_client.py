from weather_digest.foundry_client import _build_deployment_endpoint


def test_build_deployment_endpoint_adds_azure_openai_deployment_path() -> None:
    endpoint = _build_deployment_endpoint(
        "https://{your-foundry}.openai.azure.com/",
        "gpt-5.4",
    )

    assert (
        endpoint
        == "https://{your-foundry}.openai.azure.com/openai/deployments/gpt-5.4"
    )


def test_build_deployment_endpoint_keeps_existing_deployment_path() -> None:
    endpoint = _build_deployment_endpoint(
        "https://example.openai.azure.com/openai/deployments/existing",
        "gpt-5.4",
    )

    assert endpoint == "https://example.openai.azure.com/openai/deployments/existing"
