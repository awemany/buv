#!/bin/bash
./setup-venv.sh
source venv/bin/activate
./make_testexample1.sh
./buv webserver --filelist testexample1/filelist.json --genesis-members 078ac7c8185b45312f1b52a74d6056089aaa7c514259ee2c046081adf041b8e6  --serve-root . -d
