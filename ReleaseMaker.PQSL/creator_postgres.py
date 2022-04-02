import re
import json 
import os
import sys
from git import Repo
from shutil import copyfile

def conv_str(inputStr): # Конвертирует строку в нижний регистр, удаляет пробелы, устанавливает слэши в соответствии с ОС
    return inputStr.lower().replace('/', os.sep).replace('\\', os.sep).replace(' ', '') 

def conv_str_nospace(inputStr): 
    return inputStr.lower().replace('/', os.sep).replace('\\', os.sep)


release_no ='0.0.1'
target_branch = 'dev'
tagfrom = 'e5b14ce963bbab3070dcdac7538ea2cf1ca9313a'
tagto   = 'dev'

json_path ="params.json"
json_dbconnect ="db_connect.json"

with open( json_dbconnect, 'r') as the_file:
    json_dbconnect = json.load(the_file)

# Read params
with open( json_path, 'r') as the_file:
    json_params = json.load(the_file)

git_repo_dir = json_params['git_repo_dir'] # RepositoryPath
releases_dir = json_params['releases_dir'] # ReleasePath
dbconn = json_params['dbconn']


current_sql_schem = ''

release_name = target_branch
host = ''
port = ''
login = ''
passw = ''

# Write in params_json

for dc in dbconn:
    if dc['target_branch'] == target_branch:
        release_name = dc['release_name']
        host = dc['host']
        port = dc['port']
        login = dc['login']
        passw = dc['pass']

# Install.bat
#login_db =  'psql -d postgresql://' +  json_dbconnect['dbuser'] + ':' + json_dbconnect['pass'] + '@' + json_dbconnect['host'] + ':' + json_dbconnect['port'] + '/' +json_dbconnect['dbname']
#login_db += ' -q -f install.psql -L install.log ON_ERROR_STOP=on' 

login_db =  'psql -d postgresql://' +  login + ':' + passw + '@' + host + ':' + port + '/' +json_dbconnect['dbname']
login_db += ' -q -f install.psql -L install.log ON_ERROR_STOP=on' 

# db_name = 'OBMMFOT'

# if target_branch == 'test' : 
#     release_name = 'TestRelease'
#     db_name = 'OBMMFOT'

# if target_branch == 'sdo' : 
#     release_name = 'Test_update'
#     db_name = 'OBMMFOSDO'

# if target_branch[0:3] == 'rc_' : 
#     release_name = 'Release'
#     db_name = 'OBMMFORC'

# if target_branch == 'master' or target_branch == 'bugfix': 
#     release_name = 'BugFix'
#     db_name = 'OBMMFOM'

release_name += '_' + release_no
#install_stop_line = '--------stop gather patches from ' + tagfrom + ' to ' + tagto + ' for ' + release_name + ' -------'

release_dir = os.path.join(releases_dir, release_name)


# Part 1 Создание корневого каталога
if not os.path.exists(release_dir) :
    os.makedirs(release_dir)

# Create install.bat
inst_file = open (os.path.join(release_dir, 'install.bat'), 'w')
inst_file.write('chcp 1251' + '\n')
inst_file.write(login_db + '\n')
inst_file.close()



#create repo object
repo = Repo(git_repo_dir)

#checkout target branch
repo.git.checkout(target_branch)

#pull from target branch
repo.remotes.origin.pull(target_branch)

#  ---SQL---
install_psql = ''
diffs_file_set = set() # Масив уникальных схем
diffs_file_dir = set() # Масив уникальных каталогов
diffs_file_objects = ('tables', 'types', 'materializedviews', 'materialized views', 'views', 'procedures', ) # Масив порядка следования объектов

#get diff of install file
diffs_file = conv_str_nospace(repo.git.diff (tagfrom, tagto, '*', ignore_blank_lines=True, ignore_space_at_eol=True, name_status=True))
diffs_file = diffs_file.splitlines()

for i in diffs_file:
    i = i.split('\t')
    if i[1].find('install.bat') == -1 and i[1].find('install.psql') == -1:
        i[1] = conv_str(i[1])
        diffs_file_set.add(i[1][0:i[1].find(os.sep)])

diffs_file_set = sorted(diffs_file_set)        

for i in diffs_file:
    i = i.split('\t')
    i[1] = conv_str(i[1])

    if i[1].rfind(os.sep) > 0 and i[1].rfind(os.sep):
        diffs_file_dir.add(i[1][0:i[1].rfind(os.sep)])
        
diffs_file_dir = sorted(diffs_file_dir)

for i in diffs_file_dir:
    diffs_file_current = os.path.join(release_dir, i)

    #Creation release directory
    if not os.path.exists(diffs_file_current) :
        os.makedirs(diffs_file_current)

for set in diffs_file_set:
    release_dir_current = os.path.join(release_dir, set)

    for i in diffs_file:
        i = i.split('\t')

        if i[1].lower()[0:i[1].find(os.sep)] == set.lower() and i[1].count(os.sep) == 1 and i[1].find('install.bat') == -1 and i[1].find('install.psql') == -1:
            install_psql += "\n"
            install_psql += f"\i {i[1].replace(os.sep,'/')}\n"
            install_psql += f"set search_path to {set};\n"

            src_path = os.path.join(git_repo_dir,i[1].lower())
            dst_path = os.path.join(release_dir,i[1].lower())
            copyfile(conv_str_nospace(src_path), conv_str(dst_path))
  
    for obj in diffs_file_objects:
        release_dir_current = os.path.join(release_dir, set, obj)
        for diff_line in diffs_file:
            diff_line = diff_line.split('\t')
#            diff_line[2] = conv_str(diff_line[2])
# Копирование файлов                
            if diff_line[0] == 'm' or diff_line[0] == 'a':
                dst_path = os.path.join(release_dir, conv_str(diff_line[1]))
                src_path = os.path.join(git_repo_dir, diff_line[1])

                if diff_line[1][0:diff_line[1].find(os.sep)] == set and diff_line[1][diff_line[1].find(os.sep)+1:diff_line[1].find(os.sep,diff_line[1].find(os.sep)+1)] == obj \
                        and diff_line[1].find('install.bat') == -1 and diff_line[1].find('install.psql') == -1:
                    install_psql += '\i ' + diff_line[1].replace('\\','/') +'\n'
                    copyfile(src_path, dst_path)

            elif diff_line[0][0:1] == 'r':
                diff_line[2] = conv_str(diff_line[2])
                dst_path = os.path.join(release_dir, diff_line[2])  
                src_path = os.path.join(git_repo_dir, diff_line[2])
                if diff_line[2][0:diff_line[2].find(os.sep)] == set and diff_line[2][diff_line[2].find(os.sep)+1:diff_line[2].find(os.sep,diff_line[2].find(os.sep)+1)] == obj \
                        and diff_line[2].find('install.bat') == -1 and diff_line[2].find('install.psql') == -1:
                    install_psql += f"\i '{diff_line[2].lower()}'\n"
                    copyfile(src_path, conv_str(dst_path))
try:
	with open(os.path.join(release_dir, 'install.psql'), 'wb') as the_file:
		the_file.write(install_psql.encode('cp1251'))
except FileNotFoundError:  
    None