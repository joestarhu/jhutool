#! /usr/bin/env python3
import os
from flask import Flask
from flask_script import Manager
from tklc import tklc_init

app = tklc_init(os.getenv('FLASK_ENV') or 'default')

manager = Manager(app)

if __name__ == "__main__":
    manager.run()
