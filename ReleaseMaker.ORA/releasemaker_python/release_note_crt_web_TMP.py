import requests
import json
import re 
import os
import sys
from git import Repo

with open( 'params.json', 'r') as the_file:
    json_params = json.load(the_file)

jira_url = json_params['jira_url'] + '/rest/api/2/issue/'
jira_login = json_params['jira_login']
jira_pass = json_params['jira_pass']

# release_no = sys.argv[1] #'8.0.6'
# tagfrom = sys.argv[2] #'TestRelease_8.0.5'
# tagto = sys.argv[3] #'test'
# target_branch = sys.argv[4] #'test'


release_no = '2.0.111.1.2'
tagfrom = 'BugFix_2.0.111.1.1'
tagto = 'bugfix'
target_branch = 'bugfix'


git_repo_dir = json_params['git_repo_dir'] #sys.argv[5] #'C:\\Git\\obuabs\\mmfo1'
releases_dir = json_params['releases_dir'] #sys.argv[6] #'C:\\Git\\obuabs\\Release'

note_body = '|'.ljust(304, '-') + '|' + os.linesep
note_body += '|         Заявка          |       Заявка в ОТ       |' + ' '.rjust(37, ' ') + 'Контакт' + ' '.rjust(36, ' ') + '|' + ' '.rjust(83, ' ') + 'Опис' + ' '.rjust(83, ' ') + '|' + os.linesep
note_body += '|'.ljust(304, '-') + '|'  + os.linesep

#creating release prefix
release_name = target_branch

if target_branch == 'test' : 
    release_name = 'TestRelease'

if target_branch[0:3] == 'rc_' : 
    release_name = 'Release'

if target_branch == 'master' or target_branch == 'bugfix': 
    release_name = 'BugFix'

release_name += '_' + release_no

#concatenate directory name for release
release_dir = os.path.join(releases_dir, release_name)

#create repo object
repo = Repo(git_repo_dir)
#checkout target branch
repo.git.checkout(target_branch)
#pull from target branch
repo.remotes.origin.pull(target_branch)
diffs_file = repo.git.log( tagfrom + '..' + tagto, '--format="%s"')
diffs_file = re.findall(r'^"Merge.*' + "into '" + target_branch + "'", diffs_file, flags=re.MULTILINE)
task_list = []
for log_str in diffs_file:
    try:
        log_str = log_str.upper() 
        task = re.search('COBU([A-Z]|[a-z])*(-|_)\\d{1,}', log_str).group(0).replace('_', '-')
        if task not in task_list :
            task_list.append(task)
    except AttributeError:
        task = None

session = requests.Session()
session.auth = (jira_login, jira_pass)
session.headers = {'Content-type': 'application/json'}

for task in task_list:
    response = session.get(jira_url + task, verify=False)
    try:    
        json_data = json.loads(response.text)
        if json_data['key'] != None :
            note_body += '|' + '{:25s}'.format(json_data['key'][0:25])
        else :
            note_body += '|' + '{:25s}'.format(' ')    
        if json_data['fields']['customfield_11111'] != None :    
            note_body += '|' + '{:25s}'.format(json_data['fields']['customfield_11111'][0:25])
        else :
            note_body += '|' + '{:25s}'.format(' ')        
        if json_data['fields']['customfield_11112'] != None :      
            note_body += '|' + '{:80s}'.format(json_data['fields']['customfield_11112'][0:80])
        else :
            note_body += '|' + '{:80s}'.format(' ')
        if json_data['fields']['summary'] != None :     
            note_body += '|' + '{:170s}'.format(json_data['fields']['summary'][0:170]) + '|' + os.linesep
        else :
            note_body += '|' + '{:170s}'.format(' ') + '|' + os.linesep
    except KeyError:
        None
    except json.JSONDecodeError:
        print(response.text) 
session.close()        
note_body += '-'.ljust(304, '-') + '-'
print(note_body)

# with open(os.path.join(release_dir, 'release_note.txt'), 'wb') as the_file:
#     the_file.write(note_body.encode('cp1251'))