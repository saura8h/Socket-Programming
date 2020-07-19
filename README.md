# Socket Programming

Evaluating prelimaries for socket programming.

# Setup

+ Navigate to project root

    `cd /path/to/directory`

+ Initiate repository

    `git init`

+ Connect to remote repository

    `git remote add origin git@github.com:saura8h/Computer-Communications.git`

+ Install project

    `git pull origin master`

+ Create python 3 virtual environment

    `python3 -m venv proj`

+ Activate virtual environment

    `source proj/bin/activate`  

# Execution

+ Open two terminals and navigate to project root in both

+ Start server in one terminal

    `python sendfile/serv.py`

+ Send file from client to server in the other terminal

    `python sendfile/cli.py sendfile/file.txt`
