__author__ = 'krishnateja'

import logging
from flaskext.mysql import MySQL
from flask import Flask, render_template, request
from flask_ask import Ask, statement, question, session

mysql = MySQL()

app = Flask(__name__)
app.config.from_object(__name__)
app.config['MYSQL_DATABASE_USER'] = 'xxx'
app.config['MYSQL_DATABASE_PASSWORD'] = 'xxxx'
app.config['MYSQL_DATABASE_DB'] = 'xxxxx'
app.config['MYSQL_DATABASE_HOST'] = 'xxxxx.xxx.xxx.xxxx'
mysql.init_app(app)

ask = Ask(app, "/")

logging.getLogger("flask_ask").setLevel(logging.DEBUG)


@ask.launch
def new_conference():
    welcome_msg = render_template('welcome')
    return question(welcome_msg)


@ask.intent("SpeakerIntent")
def session_details(speaker_name):
    session.attributes['speaker'] = speaker_name
    cursor = mysql.connect().cursor()

    cursor.execute(
        "SELECT * from conference.talk JOIN conference.speaker "
        "ON conference.talk.speaker = conference.speaker.speakerid "
        "JOIN conference.slot "
        "ON conference.talk.slot = conference.slot.slotid "
        "WHERE conference.speaker.name LIKE '%" + speaker_name + "%';")

    data = cursor.fetchone()
    if data is None:
        message = "There was no speaker by that name."
    else:
        hours_start, remainder = divmod(data[13].seconds, 3600)
        minutes_start, seconds_start = divmod(remainder, 60)
        if len(str(minutes_start)) < 2:
            minutes_start = str(minutes_start) + '0'
        time_start = str(hours_start) + ":" + str(minutes_start)

        hours_end, remainder = divmod(data[14].seconds, 3600)
        minutes_end, seconds_start = divmod(remainder, 60)
        if len(str(minutes_end)) < 2:
            minutes_end = str(minutes_end) + '0'
        time_end = str(hours_end) + ":" + str(minutes_end)

        message = "Session that you are looking for is " + data[
            2] + " which starts at " + time_start + " and ends at " + time_end + ", given by " + data[9] + ","

        question_msg = render_template('speaker')

        message += question_msg

    return question(message)


@ask.intent("YesIntent")
def speaker_details():
    cursor = mysql.connect().cursor()
    speaker_name = session.attributes['speaker']
    cursor.execute(
        "SELECT bio from conference.speaker "
        "WHERE conference.speaker.name LIKE '%" + speaker_name + "%';")
    data = cursor.fetchone()
    if data is None:
        message = "I am so sorry. The speaker wants to maintain a sense of surprise and did not let me aware of his capabilities and any information about him"
    else:
        message = data[0]
        question_msg = render_template('session')
        message += "," + question_msg

    return question(message)

@ask.intent("NoIntent")
def no_intentions():
    message = render_template('nointent')
    return statement(message)

@ask.intent("AMAZON.StopIntent")
def stop():
    message = render_template('nointent')
    return statement(message)

if __name__ == '__main__':
    app.run(debug=True)
