# Schedule a Python script with GitHub Actions to pull Semgrep Findings for full ORG and save as CSV & XLSX format

This example shows how to run a Python script as cron job with GitHub Actions to pull Semgrep Findings for full ORG and save as CSV & XLSX. It calls an API once every hour (could be any schedule you want), downloads the findings as JSON, combines all the findings across all projects (repos) into a single JSON file, converts it into a CSV & XLSX file and stores the findings as an Artifact.

**IMPORTANT** Secret environment variables must be set. 
* Set secrets in Settings/Secrets/Actions -> 'New repository secret'.
* Use the  secret name `SEMGREP_API_WEB_TOKEN` to store your Semgrep Web API token
* You can generate the `SEMGREP_API_WEB_TOKEN` from [https://semgrep.dev](https://semgrep.dev/orgs/~/settings/tokens). Make sure that the generated token has the `Token Scope` as  `WEB API`.

## What does the script do?
* The script does the following:
  * Get your current deployment
  * Get your projects
  * Dump a JSON file for each projects
  * Combines the per project JSON files into a single JSON files for the full Organization
  * Filter the JSON for specific columns that are of interest and rename column names
  * Converts the combined JSON file into a CSV & XLSX file
  * Saves the CSV & XLSX file as an Artifact in GitHUb actions. The Artifact name is "Findings-Current Time -- Current Date"

## Other Settings
* Inspect and configure cron job in GitHub Action .github/workflows/actions.yml
* It can install and use third party packages from requirements.txt

