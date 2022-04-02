import requests
import json
import os
from datetime import datetime

with open( 'params.json', 'r') as the_file:
    json_params = json.load(the_file)

url = json_params['jira_url'] + '/rest/api/2/issue/'
jira_login = json_params['jira_login']
jira_pass = json_params['jira_pass']
task_file = json_params['release_task_file']

release_name = input("Input Release name:")

with open(task_file) as the_file:
    task_list = the_file.readlines()

#create web session
session = requests.Session()
session.auth = (jira_login, jira_pass)
session.headers = {'Content-type': 'application/json'}

for task in task_list:
    task = task.replace('\\n', '')
    task = task.strip()
    print(task)
    #creating Json body for request to Jira
    comment_body = {}
    comment_body['body'] = release_name
    json_txt = json.dumps(comment_body)

    response = session.post(url + task + '/comment', json_txt, verify=False)
    if response.status_code != 201:
        print(response.content)

    fild_ch_body = {} 
    rls = {}
    #rls1 = {}    
    rls['customfield_15213'] = release_name
    fild_ch_body['fields'] = rls

    #rls1['customfield_15214'] = release_name
    #fild_ch_body['fields'] = rls

    json_txt = json.dumps(fild_ch_body)

    response = session.put(url + task, json_txt, verify=False)
    if response.status_code != 204:
        print(response.content)
session.close()