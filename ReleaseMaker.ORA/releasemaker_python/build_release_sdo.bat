setlocal enabledelayedexpansion
set release_no=SDO_7.0.17
set tagfrom=TestRelease_SDO_7.0.016
set tagto=sdo

set target_branch=sdo

python.exe release_creator.py %release_no% %tagfrom% %tagto% %target_branch%
rem python.exe release_note_crt_web.py %release_no% %tagfrom% %tagto% %target_branch%

