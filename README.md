# Schedule a Python script with GitHub Actions to pull Semgrep Findings for full ORG and save as CSV

This example shows how to run a Python script as cron job with GitHub Actions to pull Semgrep Findings for full ORG and save as CSV. It calls an API once every hour (could be any schedule you want), downloads the findings as JSON, combines all the findings across all projects (repos) into a single JSON file, converts it into a CSV file and stores the findings as an Artifact.

* Implements your script in main.py
* Inspect and configure cron job in GitHub Action .github/workflows/actions.yml
* It can install and use third party packages from requirements.txt

**IMPORTANT** Secret environment variables must be set . Set secrets in Settings/Secrets/Actions -> 'New repository secret'. Use the  secret name `SEMGREP_API_WEB_TOKEN` to store your Semgrep Web API token
