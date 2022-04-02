setlocal enabledelayedexpansion
set release_no=2.0.111.1.2
set tagfrom=BugFix_2.0.111.1.1
set tagto=bugfix

set target_branch=bugfix

python.exe release_creator.py %release_no% %tagfrom% %tagto% %target_branch%
python.exe release_note_crt_web.py %release_no% %tagfrom% %tagto% %target_branch%

