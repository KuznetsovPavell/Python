import re 
import os
from git import Repo
from shutil import copyfile

release_no='1_01_2'
tagfrom='GIT_START'
tagto='HEAD'
target_branch='change_install'
git_repo_dir='C:\\Git\\obuabs\\mmfo'
releases_dir='C:\\Git\\obuabs\\Release'
install_sql_dir = 'install_sql'

install_list = []

install_sql = ''

#формируем имя диреткории для релиза
release_prfx = target_branch

if target_branch == 'test' : 
    release_prfx = 'TestRelease'

if target_branch[0:3] == 'rc_' : 
    release_prfx = 'Release'

if target_branch == 'master' or target_branch == 'bugfix': 
    release_prfx = 'BugFix'

release_dir = os.path.join(releases_dir, release_prfx + '_' + release_no)

release_sql_dir = os.path.join(release_dir, 'sql')
release_web_dir = os.path.join(release_dir, 'web')
release_webrz_dir = os.path.join(release_dir, 'web_rozdrib')

if not os.path.exists(release_dir) :
    os.makedirs(release_dir)

with open(os.path.join('templates', 'install_head.sql'), 'r') as install_head :
    install_sql = install_head.read()

install_sql += os.linesep + 'define release_name=' + release_prfx + '_' + release_no

with open( os.path.join('templates', 'install_head_2.sql'), 'r') as install_head_2 :
    install_sql += os.linesep + install_head_2.read()


repo = Repo(git_repo_dir)
repo.git.checkout(target_branch)
repo.remotes.origin.pull(target_branch)
install_commits = repo.git.log(tagfrom, tagto, install_sql_dir, format='%H', reverse=True).splitlines()
for install_commit in install_commits :
    diff_files = repo.git.diff (install_commit + '~1', install_commit, install_sql_dir, ignore_blank_lines=True, ignore_space_at_eol=True, name_only=True).splitlines()
    for diff_file in diff_files :
        diffs_file = repo.git.diff (install_commit + '~1', install_commit, diff_file, ignore_blank_lines=True, ignore_space_at_eol=True)
        diffs_file = diffs_file[diffs_file.find('@@'):]
        diffs_file = re.findall(r'^\+..*', diffs_file, flags=re.MULTILINE)
        for diff_line in diffs_file :
            diff_line = diff_line[2:].lower().replace('/', '\\').replace(' ', '')
            if diff_line not in install_list :
                install_list.append(diff_line)
for install_item in install_list :
    copyfile(os.path.join(git_repo_dir, 'sql', install_item), os.path.join(release_sql_dir, install_item))
