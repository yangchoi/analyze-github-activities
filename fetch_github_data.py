import os
import pandas as pd
import requests
from dotenv import load_dotenv


load_dotenv()

token = os.getenv('GITHUB_TOKEN')
headers = {'Authorization': f'Bearer {token}'}

repo_owner = os.getenv('REPO_OWNER')
repo_name = os.getenv('REPO_NAME')
user_name = os.getenv('USER_NAME')

page = 1
per_page = 100
pr_data = []

while True:
    PR_LIST_API_URL = f'https://api.github.com/search/issues?q=is:pr+repo:{repo_owner}/{repo_name}+author:{user_name}&per_page={per_page}&page={page}'
    pr_list_response = requests.get(PR_LIST_API_URL, headers=headers)

    if pr_list_response.status_code == 400:
        print('Wrong API URL')

    if pr_list_response.status_code == 200:
        for item in pr_list_response.json()['items']:
            if item['pull_request']['merged_at'] is None:
                continue
            pr_info = {
                'PR number': item['number'],
                'PR title': item['title'],
                'PR author': item['user']['login'],
                'PR description': item['body'],
                'PR URL': item['html_url'],
                'PR created at': item['created_at'],
                'PR merged at': item['pull_request']['merged_at'],
                'PR diff': []
            }

            pull_number = item['number']
            PR_DIFF_API_URL = f'https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pull_number}/files'
            pr_diff_response = requests.get(PR_DIFF_API_URL, headers=headers)

            for diff_item in pr_diff_response.json():
                pr_info['PR diff'].append({
                    'filename': diff_item['filename'],
                    'status': diff_item['status'],
                    'changes': diff_item['changes'],
                    'patch': diff_item.get('patch', 'No patch')
                })
            pr_data.append(pr_info)
        page += 1
    else:
        break
        print('failed to get pull requests')

df = pd.DataFrame(pr_data)

excel_file = 'pr_data.csv'
df.to_csv(excel_file, index=False)
print('Excel file created successfully')

