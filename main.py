import requests
import sys
import json
import re
import os
import pandas as pd


SEMGREP_APP_TOKEN = "b1dd0059a9e1c8dfa623aabf724b2058e2d442e8625e89e51ce65a6e0b4d3222"
FILTER_IMPORTANT_FINDINGS = True

def get_deployments():
    headers = {"Accept": "application/json", "Authorization": "Bearer " + SEMGREP_APP_TOKEN}

    r = requests.get('https://semgrep.dev/api/v1/deployments',headers=headers)
    if r.status_code != 200:
        sys.exit(f'Get failed: {r.text}')
    data = json.loads(r.text)
    slug_name = data['deployments'][0].get('slug')
    print("Accessing org: " + slug_name)
    return slug_name

def get_projects(slug_name):
    
    headers = {"Accept": "application/json", "Authorization": "Bearer " + SEMGREP_APP_TOKEN}

    r = requests.get('https://semgrep.dev/api/v1/deployments/' + slug_name + '/projects?page=0',headers=headers)
    if r.status_code != 200:
        sys.exit(f'Get failed: {r.text}')
    data = json.loads(r.text)
    for project in data['projects']:
        project_name = project['name']
        print("Getting findings for: " + project_name)
        get_findings_per_repo(slug_name, project_name)


def get_findings_per_repo(slug_name, repo):
      
    headers = {"Accept": "application/json", "Authorization": "Bearer " + SEMGREP_APP_TOKEN}

    r = requests.get('https://semgrep.dev/api/v1/deployments/' + slug_name + '/findings?repos='+repo,headers=headers)
    if r.status_code != 200:
        sys.exit(f'Get failed: {r.text}')
    data = json.loads(r.text)
    file_path = re.sub(r"[^\w\s]", "", repo) + ".json"
    # file_path = "findings.json"
    if FILTER_IMPORTANT_FINDINGS == True:
        data = [obj for obj in data['findings'] if obj["severity"] == "high" and obj["confidence"] == "high" or obj["confidence"] == "medium"]
    with open(file_path, "w") as file:
         json.dump(data, file)


def combine_json_files(folder_path, output_file):
    combined_data = []
    
    # Loop through each file in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            with open(os.path.join(folder_path, filename), 'r') as file:
                data = json.load(file)
                
                # Append data from current file to combined data
                if isinstance(data, list):
                    combined_data.extend(data)
                else:
                    combined_data.append(data)

    # Write combined data to output file
    with open(output_file, 'w') as outfile:
        json.dump(combined_data, outfile, indent=4)

def json_to_csv_pandas(json_file, csv_file):
    # Read the JSON file into a DataFrame
    df = pd.read_json(json_file)
    
    # Write the DataFrame to CSV
    df.to_csv(csv_file, index=False)


if __name__ == "__main__":
    slug_name = get_deployments()
    get_projects(slug_name)
    combine_json_files('/Users/nnayar/projects/python-github-action-template', 'combined.json')
    json_to_csv_pandas('combined.json', 'output.csv')
