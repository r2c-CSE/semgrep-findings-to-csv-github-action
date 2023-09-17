import requests
import sys
import json
import re
import os
import pandas as pd

try:
    SEMGREP_API_WEB_TOKEN = os.environ["SEMGREP_API_WEB_TOKEN"]
except KeyError:
    SEMGREP_API_WEB_TOKEN = "Token not available!"

FILTER_IMPORTANT_FINDINGS = False

def get_deployments():
    headers = {"Accept": "application/json", "Authorization": "Bearer " + SEMGREP_API_WEB_TOKEN}

    r = requests.get('https://semgrep.dev/api/v1/deployments',headers=headers)
    if r.status_code != 200:
        sys.exit(f'Get failed: {r.text}')
    data = json.loads(r.text)
    slug_name = data['deployments'][0].get('slug')
    print("Accessing org: " + slug_name)
    return slug_name

def get_projects(slug_name):
    
    headers = {"Accept": "application/json", "Authorization": "Bearer " + SEMGREP_API_WEB_TOKEN}

    r = requests.get('https://semgrep.dev/api/v1/deployments/' + slug_name + '/projects?page=0',headers=headers)
    if r.status_code != 200:
        sys.exit(f'Get failed: {r.text}')
    data = json.loads(r.text)
    for project in data['projects']:
        project_name = project['name']
        print("Getting findings for: " + project_name)
        get_findings_per_repo(slug_name, project_name)

def get_findings_per_repo(slug_name, repo):
      
    headers = {"Accept": "application/json", "Authorization": "Bearer " + SEMGREP_API_WEB_TOKEN}

    r = requests.get('https://semgrep.dev/api/v1/deployments/' + slug_name + '/findings?repos='+repo,headers=headers)
    if r.status_code != 200:
        sys.exit(f'Get failed: {r.text}')
    data = json.loads(r.text)
    file_path = re.sub(r"[^\w\s]", "", repo) + ".json"
    # file_path = "findings.json"
    if FILTER_IMPORTANT_FINDINGS == True:
        data = [obj for obj in data['findings'] if obj["severity"] == "high" and obj["confidence"] == "high" or obj["confidence"] == "medium"]
    else:
        data = [obj for obj in data['findings'] ]

    with open(file_path, "w") as file:
         json.dump(data, file)


def combine_json_files(folder_path, output_file):
    combined_data = []
    
    # Loop through each file in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            print("Opening " + filename)
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

def json_to_df(json_file):
    # Read the JSON file into a DataFrame
    df = pd.read_json(json_file)

    df = df.rename(columns={'rule_name' : 'Finding Title' , 'rule_message'  : 'Finding Description & Remediation', 'relevant_since' : 'First Seen'})


    # filter out only specific columns
    df = df.loc[:, [ 'Finding Title', 'Finding Description & Remediation', 'state', 'First Seen', 'severity', 'confidence',  'triage_state', 'triaged_at', 'triage_comment', 'state_updated_at', 'repository',  'location' ]] 
    # df = df.loc[:, [ 'state', 'repository', 'first_seen_scan_id', 'triage_state', 'severity', 'confidence', 'relevant_since', 'rule_name', 'rule_message', 'location',	'triaged_at', 'triage_comment', 'state_updated_at']] 
    # 'state', 'repository', 'first_seen_scan_id', 'triage_state', 'severity', 'confidence', 'relevant_since', 'rule_name', 'rule_message', 'location',	'triaged_at', 'triage_comment', 'state_updated_at'
    # update column to datetime format
    # df['first_seen_scan_id'] = pd.to_datetime(df['first_seen_scan_id'], format='%H-%M--%d-%b-%Y')

    return df

def json_to_csv_pandas(json_file, csv_file):

    df = json_to_df(json_file)

    df = df.rename(columns={'rule_name' : 'Finding Title' , 'rule_message'  : 'Finding Description & Remediation', 'relevant_since' : 'First Seen'})

    # Write the DataFrame to CSV
    df.to_csv(csv_file, index=False)

def json_to_xlsx_pandas(json_file, xlsx_file):

    df = json_to_df(json_file)

    # Write the DataFrame to CSV
    # df.to_excel(xlsx_file, index=False)

    writer = pd.ExcelWriter(xlsx_file, engine='xlsxwriter') 
    df.to_excel(writer, sheet_name='Findings', index=False)

    for column in df:
        column_width = max(df[column].astype(str).map(len).max(), len(column))
        col_idx = df.columns.get_loc(column)
        writer.sheets['Findings'].set_column(col_idx, col_idx, column_width)

    col_idx = df.columns.get_loc('Finding Title')
    writer.sheets['Findings'].set_column(col_idx, col_idx, 50)
    
    col_idx = df.columns.get_loc('Finding Description & Remediation')
    writer.sheets['Findings'].set_column(col_idx, col_idx, 150)
    
    col_idx = df.columns.get_loc('repository')
    writer.sheets['Findings'].set_column(col_idx, col_idx, 100)
    
    col_idx = df.columns.get_loc('location')
    writer.sheets['Findings'].set_column(col_idx, col_idx, 100)

    workbook = writer.book
    worksheet = writer.sheets['Findings']

    # Add some cell formats.
    datatime_format = workbook.add_format({'datetime_format': 'mmm d yyyy hh:mm'})

    
    # Set the column width and format.
    worksheet.set_column(4, 4, 30, datatime_format)
    
    writer.close()

if __name__ == "__main__":
    slug_name = get_deployments()
    get_projects(slug_name)
    print ("starting process to combine JSON files")
    combine_json_files('.', 'combined.json')
    print ("completed combine process")
    print ("starting process to convert combined JSON file to csv & xlsx")
    json_to_csv_pandas('combined.json', 'output.csv')
    json_to_xlsx_pandas('combined.json', 'output.xlsx')
    print ("completed conversion process")
