#! /usr/bin/env python3
import os
from flask import Flask
from flask_script import Manager
from tklc import tklc_init
from datetime import timedelta

app = tklc_init(os.getenv('FLASK_ENV') or 'default')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)
manager = Manager(app)

if __name__ == "__main__":
    manager.run()
