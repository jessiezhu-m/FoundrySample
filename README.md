# Shanghai Weather Foundry Demo

This is a small Python demo project for hackathon review.

It intentionally uses a simple implementation:

- A local scheduler runs every day at 06:00 Asia/Shanghai time.
- The job calls an Azure OpenAI deployment through the Foundry inference SDK using your Azure login.
- The AI response is emailed via Azure Communication Services (ACS) Email.

This makes it easy for a later review agent to suggest upgrades, for example:

- Replace the local scheduler with Foundry Agent recurrence.
- Replace SMTP email sending with a Foundry Agent Work IQ / worker tool.
- Add tracing, evals, retry policy, and delivery evidence.

## Project structure

```text
shanghai-weather-foundry-demo/
  src/weather_digest/
    config.py
    foundry_client.py
    emailer.py
    scheduler.py
    main.py
  tests/
    test_emailer.py
  .env.example
  requirements.txt
  pyproject.toml
```

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
Copy-Item .env.example .env
```

Then edit `.env`.

> The project uses a `src/` layout, so `pip install -e .` is required to make
> the `weather_digest` package importable. Without it you will see
> `ModuleNotFoundError: No module named 'weather_digest'`.

## Required environment variables

```text
FOUNDRY_ENDPOINT=
FOUNDRY_DEPLOYMENT=gpt-5.4
FOUNDRY_API_VERSION=2024-06-01

ACS_CONNECTION_STRING=
EMAIL_FROM=
EMAIL_TO=
```

The app uses `DefaultAzureCredential` for the Foundry call, so for local
development run `az login` before starting it. API keys are not required. For
Azure OpenAI endpoints, `FOUNDRY_ENDPOINT` can be the resource base URL, for
example ``; the code adds
`/openai/deployments/<FOUNDRY_DEPLOYMENT>` automatically.

## Email via Azure Communication Services (ACS)

Email is sent through **ACS Email**, which does not depend on an Office 365
mailbox. This avoids the SMTP "basic authentication is disabled" error and the
Microsoft Graph 403/404 errors that occur when your `az login` identity lacks
`Mail.Send` or the sender mailbox is outside your tenant.

One-time provisioning (Azure Portal or CLI):

1. Create an **Azure Communication Services** resource.
2. Create an **Email Communication Services** resource, then add a domain:
   - **Azure Managed Domain** is quickest — it gives you a ready-to-use sender
     like `DoNotReply@<guid>.azurecomm.net` with no DNS setup.
   - Or connect a **custom domain** (requires DNS verification).
3. **Connect** the email domain to the Communication Services resource
   (ACS resource > Email > Domains > Connect domain).
4. In the ACS resource > **Keys**, copy the **connection string** into
   `ACS_CONNECTION_STRING`.
5. Set `EMAIL_FROM` to a verified sender on the provisioned domain, for example
   `DoNotReply@<guid>.azurecomm.net`.

> Note: with an Azure Managed Domain, recipients may be rate-limited and the
> "from" name is fixed. For production use a verified custom domain.

CLI example (managed domain):

```powershell
az communication create --name <acs-name> --resource-group <rg> --location global --data-location UnitedStates
az communication email create --name <email-name> --resource-group <rg> --location global --data-location UnitedStates
az communication email domain create --domain-name AzureManagedDomain --email-service-name <email-name> --resource-group <rg> --domain-management AzureManaged
# Then connect the domain to the ACS resource and copy the connection string from the Keys blade.
```

> Note: `EMAIL_TO` follows the requested address. Please verify whether it is a valid email address.

## Run once

```powershell
python -m weather_digest.main --run-once
```

## Run scheduler

```powershell
python -m weather_digest.main
```

The scheduler runs the job every day at 06:00 in the `Asia/Shanghai` timezone.

## Run tests

```powershell
pytest
```
