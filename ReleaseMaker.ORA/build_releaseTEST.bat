setlocal enabledelayedexpansion
set release_no=8.0.6
set tagfrom=TestRelease_PROJ_13.0.030
set tagto=test

set target_branch=test

python.exe release_creator.py %release_no% %tagfrom% %tagto% %target_branch%
rem python.exe release_note_crt_web.py %release_no% %tagfrom% %tagto% %target_branch%

