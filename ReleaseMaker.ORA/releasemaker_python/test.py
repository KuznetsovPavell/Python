
from git import Repo


git_repo_dir = 'C:\Git\obuabs\mmfo'
target_branch = 'test'


#create repo object
repo = Repo(git_repo_dir)
#checkout target branch
repo.git.checkout(target_branch)
#pull from target branch
--repo.remotes.origin.pull(target_branch)
--repo.git.commit('-m', 'test commit', author='pavlo.kuznetsov@unity-bars.com')