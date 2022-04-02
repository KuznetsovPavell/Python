import requests
import json
import os
import gmail
from datetime import datetime

with open( 'params.json', 'r') as the_file:
    json_params = json.load(the_file)

url = json_params['jira_url'] + '/rest/api/2/issue/'
jira_login = json_params['jira_login']
jira_pass = json_params['jira_pass']

gmail_login = json_params['gmail_login']
gmail_pass = json_params['gmail_pass']

task_file = json_params['task_file']

release_number = input("Input Release number:")
destination_branch = input("Input destination branch name:")
time_limit = input("Input time lomit:")
dest_release = 'тестрелізу'
if 'rc_' in destination_branch:
    dest_release = 'релізу'
elif 'bugfix' in destination_branch or 'master' in destination_branch:
    dest_release = 'багфіксу'


with open(task_file) as the_file:
    task_list = the_file.readlines()

#create web session
session = requests.Session()
session.auth = (jira_login, jira_pass)
session.headers = {'Content-type': 'application/json'}

#connect to gmail
gmail_conn = gmail.GMail(gmail_login + '@unity-bars.com',gmail_pass)

for task in task_list:
    task = task.replace('\\n', '')
    task = task.strip()
    print(task)
    #creating Json body for request to Jira
    message_text = 'Заявку ' + task + ' включено до ' + dest_release + ' ' + release_number + '. Прохання створити Merge Request в гілку ' + destination_branch + ' до ' + time_limit + '!!'
    req_body = {}
    visibility = {}
    visibility['type'] = 'group'
    visibility['value'] = 'BARS_UG - БАРС'
    req_body['body'] = message_text
    req_body['visibility'] = visibility
    json_txt = json.dumps(req_body)

    #geting assignee emailAddress
    response = session.get(url + task, verify=False)
    if response.status_code == 200:
        json_data = json.loads(response.text)
        assignee_email = json_data['fields']['assignee']['emailAddress']
        #sending email
        msg = gmail.Message('Створіть MergeRequest!!',to=assignee_email,text=message_text)
        gmail_conn.send(msg)
    else:
        print(response.content)
    response = session.post(url + task + '/comment', json_txt, verify=False)
    if response.status_code != 201:
        print(response.content)
session.close()
gmail_conn.close()