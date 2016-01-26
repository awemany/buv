#!/bin/bash
cd `dirname $0`
python2.7 -m virtualenv -p /usr/bin/python2.7 venv/
source venv/bin/activate

pip2.7 install bottle==0.12.9
pip2.7 install ipython==1.2.1
pip2.7 install coverage==4.0.3
pip2.7 install jsoncomment==0.3.0
pip2.7 install git+https://github.com/vbuterin/pybitcointools@8e8a33d7281c871950519e5f256ad08cf0d5df69
