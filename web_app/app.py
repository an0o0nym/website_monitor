# -*- coding: utf-8 -*-

"""Flask website application module."""
from flask import Flask, render_template
from website_monitor import db_utils
from datetime import datetime

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    records = db_utils.get_all_records()
    records = sorted(records, key=lambda x: datetime.strptime(
        x[3], "%d-%m-%Y %H:%M:%S"), reverse=True)

    return render_template('index.html', records=records)


def main():
    app.run()


if __name__ == '__main__':
    main()
