@echo off
if not exist venv (
    pip install virtualenv
    virtualenv venv
)
pip install -U -r requirements.txt
venv\Scripts\activate
