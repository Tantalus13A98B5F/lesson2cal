#!/bin/bash

# Detect Python Version
python_ver=`python -c 'import platform; major, minor, patch = platform.python_version_tuple(); print(major);'`
python3_ver=`python3 -c 'import platform; major, minor, patch = platform.python_version_tuple(); print(major);'`

if [ "$python_ver" = "2" ]; then
if [ "$python3_ver" = "3" ]; then
cmd_head="python3"
echo 'python3 check.'
else
echo "Invalid Python 3 Version."
fi
else
if ["$python_ver"="3"]; then
cmd_head="python"
echo 'python check.'
else
echo "Invalid Python 3 Version."
fi
fi

# Detect pip
pip_ver=`pip -V`
if [ -n "$pip_ver" ]; then
echo 'pip check.'
else
echo "pip Not Found."
exit 1
fi


# Start Server

if [ -n "$cmd_head" ]; then
pip install -r requirements.txt
$cmd_head server.py
else
exit 1
fi 
