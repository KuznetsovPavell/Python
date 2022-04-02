setlocal enabledelayedexpansion
set release_no=PROJ_13.0.019
set tagfrom=TestRelease_PROJ_13.0.018
set tagto=test

set target_branch=test

python.exe release_creator.py %release_no% %tagfrom% %tagto% %target_branch%
rem python.exe release_note_crt_web.py %release_no% %tagfrom% %tagto% %target_branch%

