from ntpath import realpath
import re
import json 
import os
import sys
from git import Repo
from shutil import copyfile

with open( 'params.json', 'r') as the_file:
    json_params = json.load(the_file)

release_no = '8.0.6' #sys.argv[1] #'8.0.6'
tagfrom = 'TestRelease_8.0.5' #sys.argv[2] #'TestRelease_8.0.5'
tagto = 'test' #sys.argv[3] #'test'
target_branch = 'test' #sys.argv[4] #.lower() #'test'
git_repo_dir = json_params['git_repo_dir'] #sys.argv[5] #'C:\\Git\\obuabs\\mmfo'
releases_dir = json_params['releases_dir'] #sys.argv[6] #'C:\\Git\\obuabs\\Release'

print('git_repo_dir: '+ git_repo_dir)
print('releases_dir: ' +releases_dir)

install_path=os.path.join('sql', 'install.sql')
schems_list = ['SYS', 'BARS', 'BARSUPL', 'BARS_DM', 'DM', 'PFU', 'SBON', 'MGW_AGENT', 'BARSAQ', 'BARSTRANS', 'BARS_INTGR', 'FINMON', 'FINMONIC', 'MSP', 'SYSTEM', 'NBU_GATEWAY' ,'CBD', 'BILLS', 'BARSOS']
install_list = []
current_sql_schem = ''

#creating release prefix
release_name = target_branch
db_name = ''

if target_branch == 'test' : 
    release_name = 'TestRelease'
    db_name = 'OBMMFOT'

if target_branch[0:3] == 'sdo' : 
    release_name = 'Test_update'
    db_name = 'OBMMFOSDO'

if target_branch[0:3] == 'rc_' : 
    release_name = 'Release'
    db_name = 'OBMMFORC'

if target_branch == 'master' or target_branch == 'bugfix': 
    release_name = 'BugFix'
    db_name = 'OBMMFOM'

release_name += '_' + release_no
install_stop_line = '--------stop gather patches from ' + tagfrom + ' to ' + tagto + ' for ' + release_name + ' -------'

#template for relogin
schem_change_str =  os.linesep + 'prompt ...' + os.linesep + 'prompt ... loading params' + os.linesep + 'prompt ...' + os.linesep + '@params.sql'
schem_change_str += os.linesep + 'whenever sqlerror exit' + os.linesep + 'prompt ...' + os.linesep + 'prompt ... connecting as '

#select for invalid objects and errors
select_invalids = 'select owner, object_name, object_type ' + os.linesep + "from all_objects a where a.status = 'INVALID' and a.owner in ("
select_errors = 'select owner, type, name, line, position, text, sequence ' + os.linesep + 'from all_errors' + os.linesep +  'where owner in ('
schem_counter = 0
for schem in schems_list:
    if schem_counter == 0 :
        select_invalids += "'" + schem + "'"
        select_errors += "'" + schem + "'"
    else:
        select_invalids += ", '" + schem + "'"
        select_errors += ", '" + schem + "'"
    schem_counter += 1
select_invalids += ')' + os.linesep + 'order by owner, object_type;' + os.linesep + os.linesep
select_errors += ')' + os.linesep + 'order by  owner, type, name;' + os.linesep + os.linesep

#head of install.sql
install_sql = '@params.sql' + os.linesep + os.linesep + 'set verify off' + os.linesep + 'set echo off' + os.linesep + 'set serveroutput on size 1000000'
install_sql += os.linesep + 'spool log' + os.sep + 'install_(&&dbname).log' + os.linesep + 'set lines 3000' + os.linesep + 'set SQLBL on' + os.linesep + 'set timing on'
install_sql += os.linesep + os.linesep + os.linesep + 'define release_name=' + release_name + os.linesep + os.linesep + os.linesep
install_sql += schem_change_str + 'bars' + os.linesep + 'conn bars@&&dbname/&&bars_pass' + os.linesep + 'whenever sqlerror continue' + os.linesep + os.linesep
install_sql += os.linesep + os.linesep + 'prompt ...' + os.linesep + 'prompt ... invalid objects before install'
install_sql += os.linesep + 'prompt ...'+ os.linesep + os.linesep + select_invalids + 'prompt ...' + os.linesep + 'prompt ... calculating checksum for bars objects before install'
install_sql += os.linesep + 'prompt ...' + os.linesep  + "exec bars.bars_release_mgr.install_begin('&&release_name');" + os.linesep + os.linesep

#botom part of install.sql
install_tail = schem_change_str + 'sys' + os.linesep + 'conn sys@&&dbname/&&sys_pass as sysdba' + os.linesep + 'whenever sqlerror continue' + os.linesep + os.linesep
install_tail += 'prompt ...' + os.linesep  + 'prompt ... compaling schemas' + os.linesep  + 'prompt ...' + os.linesep + os.linesep

for schem in schems_list:
    install_tail += 'prompt  >> schema ' + schem + os.linesep + os.linesep + "EXECUTE sys.UTL_RECOMP.RECOMP_SERIAL('" + schem + "');" + os.linesep + os.linesep

install_tail += os.linesep + os.linesep + 'prompt ...' + os.linesep + 'prompt ... calculating checksum for bars objects after install' + os.linesep + 'prompt ... '
install_tail += os.linesep + os.linesep + "exec bars.bars_release_mgr.install_end('&&release_name');" + os.linesep + os.linesep + 'prompt ...' + os.linesep
install_tail += 'prompt ... invalid objects after install' + os.linesep + 'prompt ...' + os.linesep + os.linesep + select_invalids + os.linesep + os.linesep
install_tail += 'prompt ...' + os.linesep + 'prompt ... errors for invalid objects' + os.linesep + 'prompt ...' + os.linesep + os.linesep + 'set line 10000'
install_tail += os.linesep + 'set trimspool on' + os.linesep + 'set pagesize 10000' + os.linesep + os.linesep + 'prompt ...' + os.linesep
install_tail += 'prompt ... errors for invalid objects' + os.linesep + 'prompt ...' + os.linesep + os.linesep + select_errors + os.linesep + os.linesep
install_tail += os.linesep + 'spool off' + os.linesep + 'quit'

install_bat = 'chcp 1251' + os.linesep + 'set NLS_LANG=AMERICAN_AMERICA.CL8MSWIN1251' + os.linesep + 'mkdir log' + os.linesep + 'sqlplus /nolog @install.sql' 
install_bat += os.linesep + os.linesep + 'echo off'  + os.linesep + 'set sword=dbname' + os.linesep + 'set file=params.sql'
install_bat += os.linesep + 'for /f "delims=" %%a in (' + "'find " + '"%sword%" ' + "%file%') do set db=%%a"
install_bat += os.linesep + 'set db=%db:define dbname=%' + os.linesep + 'set db=%db:~1%' + os.linesep + 'start log' + os.sep + 'install_("%db%").log'

bc_go_file = 'begin' + os.linesep + "bars.bc.go('/');" + os.linesep + 'exception when others then' + os.linesep 
bc_go_file += 'if sqlcode in (100, -01403, -04068, -04061, -04065, -06508) then null; else raise; end if;' + os.linesep + 'end;' + os.linesep + '/'

params_file = 'set define on' + os.linesep + os.linesep + '-- Синонім бази даних' + os.linesep + 'define dbname=' + db_name + os.linesep
for schem in schems_list:
    params_file += '-- Пароль користувача ' + schem.lower() + os.linesep
    if (schem.lower() == 'sys' or schem.lower() == 'system'):
        params_file += 'define ' + schem.lower() + '_pass=manager2' + os.linesep + os.linesep
    elif schem.lower() == 'bars':
        params_file += 'define ' + schem.lower() + '_pass=barsbars' + os.linesep + os.linesep
    else:
        params_file += 'define ' + schem.lower() + '_pass=' + schem.lower() + os.linesep + os.linesep


#concatenate directory name for release
release_dir = os.path.join(releases_dir, release_name)

#Creation release directory
if not os.path.exists(release_dir) :
    os.makedirs(release_dir)

#create repo object
repo = Repo(git_repo_dir)
#checkout target branch
repo.git.checkout(target_branch)
#pull from target branch
repo.remotes.origin.pull(target_branch)

#  ---SQL---

#get diff of install file
diffs_file = repo.git.diff (tagfrom, tagto, install_path, ignore_blank_lines=True, ignore_space_at_eol=True)
#substr diff start from @@
diffs_file = diffs_file[diffs_file.find('@@'):]
#split string to array and get string start on +@


diffs_file = re.findall(r'^\+@..*', diffs_file, flags=re.MULTILINE)

# #loop for all lines in install
# for diff_line in diffs_file :
#     #remove +@ and replace / to \\
#     diff_line = diff_line[2:].lower().replace('/', os.sep).replace('\\', os.sep).replace(' ', '')
#     #sort array (remove duplication) --????
#     if diff_line not in install_list :
#         install_list.append(diff_line)
# #loop for all unique lines in install
# for install_item in install_list :
#     try:
#         dst_path = os.path.join(release_dir, 'sql', install_item)
#         src_path = os.path.join(git_repo_dir, 'sql', install_item)
#         #create directory if it not exists 
#         os.makedirs(os.path.dirname(dst_path), exist_ok=True)
#         copyfile(src_path, dst_path)
#     except IOError as io_err:
#         print('File :' + src_path + 'do not exists!!')
#     #write install file string
#     #split file path
#     line_items = install_item.split(os.sep)
#     #if script from new schem then relogin
#     if current_sql_schem != line_items[0].upper():
#         install_sql += schem_change_str + line_items[0].lower()
#         install_sql += os.linesep + 'conn ' + line_items[0].lower() + '@&&dbname/&&' + line_items[0].lower() + '_pass' 
#         if line_items[0].upper() == 'SYS':
#             install_sql += ' as sysdba'
#         install_sql += os.linesep + 'whenever sqlerror continue' + os.linesep + os.linesep        
#         current_sql_schem = line_items[0].upper()
#     #write comment    
#     install_sql += os.linesep + 'prompt @' + install_item + os.linesep + 'set define off'
#     #if schems SYS or SYSTEM then we dont need bc.go
#     install_sql += os.linesep + '@bc_go.sql'
#     #write script fo calling prom sqlplus
#     install_sql += os.linesep + '@' + install_item
    
#     if line_items[1].upper() == 'PACKAGE':
#         install_sql += os.linesep + 'show err'
#     install_sql += os.linesep
# install_sql += install_tail

# try:
# 	with open(os.path.join(release_dir, 'sql', 'install.sql'), 'wb') as the_file:
# 		the_file.write(install_sql.encode('cp1251'))
# 	with open(os.path.join(release_dir, 'sql', 'install.bat'), 'wb') as the_file:
# 		the_file.write(install_bat.encode('cp1251'))
# 	with open(os.path.join(release_dir, 'sql', 'params.sql'), 'wb') as the_file:
# 		the_file.write(params_file.encode('cp1251'))
# 	with open(os.path.join(release_dir, 'sql', 'bc_go.sql'), 'wb') as the_file:
# 		the_file.write(bc_go_file.encode('cp1251'))    
# except FileNotFoundError:  
#     None

# with open(os.path.join(git_repo_dir, install_path), 'r') as f:
#     line = f.read().splitlines()[-1]
# if line != install_stop_line :
#     with open(os.path.join(git_repo_dir, install_path), 'ab') as the_file:
#         install_stop_line = os.linesep + install_stop_line
#         the_file.write(install_stop_line.encode('UTF-8'))

# # ----WEB----

# with open(os.path.join(git_repo_dir, 'web', 'barsroot', 'version.abs'), 'w') as the_file:
#     the_file.write(release_no + '(' + tagfrom + '-' + tagto + ')')


# with open(os.path.join(git_repo_dir, 'web_rozdrib',  'barsroot', 'version.abs'), 'w') as the_file:
#     the_file.write(release_no + '(' + tagfrom + '-' + tagto + ')')

# repo.git.add(os.path.join(git_repo_dir, 'web', 'barsroot', 'version.abs'))
# repo.git.add(os.path.join(git_repo_dir, 'web_rozdrib', 'barsroot', 'version.abs'))
# repo.git.add(os.path.join(git_repo_dir, 'sql', 'install.sql'))
# repo.index.commit(release_name)

# diffs_file = repo.git.diff (tagfrom, tagto, '*web*\\*', ignore_blank_lines=True, ignore_space_at_eol=True, name_status=True)
# diffs_file = diffs_file.splitlines()
# del_file = ''
# for diff_line in diffs_file:
#     diff_line = diff_line.split('\t')
#     if diff_line[0] == 'M' or diff_line[0] == 'A':
#         dst_path = os.path.join(release_dir, diff_line[1])
#         src_path = os.path.join(git_repo_dir, diff_line[1])
#         #create directory if it not exists 
#         os.makedirs(os.path.dirname(dst_path), exist_ok=True)
#         copyfile(src_path, dst_path)
#     elif diff_line[0][0:1] == 'R':
#         dst_path = os.path.join(release_dir, diff_line[2])
#         src_path = os.path.join(git_repo_dir, diff_line[2])
#         #create directory if it not exists 
#         os.makedirs(os.path.dirname(dst_path), exist_ok=True)
#         copyfile(src_path, dst_path)
#     if diff_line[0] == 'D' or diff_line[0][0:1] == 'R':
#         del_file += 'del ' + diff_line[1] + os.linesep
# if del_file != '':
#     with open(os.path.join(release_dir, 'remove_web_files.bat'), 'wb') as the_file:
#         the_file.write(del_file.replace('/', os.sep).replace('\\', os.sep).encode('cp1251'))