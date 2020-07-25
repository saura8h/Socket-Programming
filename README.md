# Socket Programming

Evaluating prelimaries for socket programming.

# Setup

+ Navigate to project root

    `cd /path/to/directory`

+ Initiate repository

    `git init`

+ Connect to remote repository

    `git remote add origin git@github.com:saura8h/Socket-Programming.git`

+ Install project

    `git pull origin master`

+ Create python 3 virtual environment

    `python3 -m venv proj`

+ Activate virtual environment

    `source proj/bin/activate`  

# Testing Functionality

+ Open two terminals and navigate to project root in both

+ Start server in one terminal

    `python server.py <PORT_NUMBER>`

+ Start client in the other terminal

    `python client.py <MACHINE_NAME> <PORT_NUMBER>`

+ In the client terminal **(indicated by `ftp> `)**:

    `ls`

    `get file.txt`

    `put file.txt`

    `quit`
