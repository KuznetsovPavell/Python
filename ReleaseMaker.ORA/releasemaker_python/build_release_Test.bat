setlocal enabledelayedexpansion
set release_no=8.0.6
set tagfrom=TestRelease_8.0.5
set tagto=test

set target_branch=test

rem python.exe release_creator.py %release_no% %tagfrom% %tagto% %target_branch%
python.exe release_note_crt_web.py %release_no% %tagfrom% %tagto% %target_branch%
