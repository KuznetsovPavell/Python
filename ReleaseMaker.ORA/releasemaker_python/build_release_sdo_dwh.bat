setlocal enabledelayedexpansion
set release_no=0.0.1.2
set tagfrom=477756b41a7898419bec6542e96c314b6130f4e9
rem set tagfrom=sdo_dwh_7.0.016
set tagto=PRJ-MSA_API

set target_branch=PRJ-MSA_API

python.exe release_creator.py %release_no% %tagfrom% %tagto% %target_branch%
python.exe release_note_crt_web.py %release_no% %tagfrom% %tagto% %target_branch%
