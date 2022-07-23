# Logic
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///records.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Record(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    score = db.Column(db.Integer, nullable=False)
    out_of = db.Column(db.Integer, nullable=False)

    def __repr__(self) -> str:
        return f'{self.username}-{self.score}/{self.out_of}'


class Deck(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    english = db.Column(db.String(200), nullable=False)
    hindi = db.Column(db.String(200), nullable=False)
    option1 = db.Column(db.String(200), nullable=False)
    option2 = db.Column(db.String(200), nullable=False)
    option3 = db.Column(db.String(200), nullable=False)
    option4 = db.Column(db.String(200), nullable=False)

    def __repr__(self) -> str:
        return f'{self.english}-{self.hindi}'


answer_sheet = {}
username = ''
records = None
l = []
i = 0


def check_answers(answer_sheet):
    global c
    score = 0
    for i in answer_sheet:
        card = Deck.query.filter_by(sno=i).first()
        if answer_sheet[i] == card.hindi:
            score += 1
    return score


def make_report(answer_sheet):
    op = []
    n = 0
    for i in answer_sheet:
        row = []
        n += 1
        card = Deck.query.filter_by(sno=i).first()
        row.append(n)  # SrNo
        row.append(card.english)  # English Word
        row.append(card.hindi)  # Hindi Word
        row.append(answer_sheet[i])  # Your Response
        if card.hindi == answer_sheet[i]:
            row.append('Correct')
        else:
            row.append('Wrong')
        op.append(row)
    return op


def write_comment(qno, score):
    percent = score/qno
    if 0 <= percent <= 0.5:
        return 'Need more practice.'
    elif 0.5 < percent < 1.0:
        return 'Can do better.'
    elif percent == 1.0:
        return 'Excellent!'

# Flask


@app.route("/", methods=['GET', 'POST'])
def hello_world():

    return render_template('login.html')


@app.route("/records", methods=['GET', 'POST'])
def records():
    records = Record.query.filter_by(username=username)
    return render_template('records.html', username=username, records=records)


@app.route('/delete/<int:sno>')
def delete(sno):
    global username
    record = Record.query.filter_by(sno=sno).first()
    db.session.delete(record)
    db.session.commit()
    records = Record.query.filter_by(username=username)
    return render_template('records.html', username=username, records=records)


@app.route("/main", methods=['GET', 'POST'])
def main_page():
    global i, answer_sheet, username, l
    deck = Deck.query.all()

    l = [i.sno for i in deck]
    random.shuffle(l)
    i = 0
    answer_sheet = {}
    if request.method == "POST":
        username = request.form['username']
        print(username)
        return render_template('main.html', username=username)
    else:
        return render_template('main.html', username=username)


@app.route("/question/<int:qno>", methods=['GET', 'POST'])
def question(qno):
    global i, answer_sheet, username, l
    if i < qno:
        if request.method == "POST":
            choice = request.form['choice']
            answer_sheet[l[i]] = choice
            print(answer_sheet)
            i += 1
        if i == qno:
            result = (make_report(answer_sheet))
            score = (check_answers(answer_sheet))
            record = Record(username=username, score=score, out_of=qno)
            db.session.add(record)
            db.session.commit()

            return render_template('result.html', qno=qno, score=score, result=result, comment=write_comment(qno, score))
        else:
            card = Deck.query.filter_by(sno=l[i]).first()
            return render_template('question.html', card=card, qno=i+1, total_questions=qno)

# Deck


@app.route("/deck", methods=['GET', 'POST'])
def deck():
    allCards = Deck.query.all()
    return render_template('deck.html', allCards=allCards)


@app.route("/add_card", methods=['GET', 'POST'])
def add_card():
    if request.method == "POST":
        card = request.form['card']
        card = card.split(',')
        new_card = Deck(english=card[0], hindi=card[1], option1=card[2],
                        option2=card[3], option3=card[4], option4=card[5])
        db.session.add(new_card)
        db.session.commit()

    allCards = Deck.query.all()
    return render_template('deck.html', allCards=allCards)


@app.route("/delete_card/<int:sno>", methods=['GET', 'POST'])
def delete_card(sno):
    card = Deck.query.filter_by(sno=sno).first()
    db.session.delete(card)
    db.session.commit()
    allCards = Deck.query.all()
    return render_template('deck.html', allCards=allCards)


@app.route("/update_card/<int:sno>", methods=['GET', 'POST'])
def update_card(sno):
    if request.method == "POST":
        new_card = request.form['card']
        new_card = new_card.split(',')
        card = Deck.query.filter_by(sno=sno).first()

        card.english = new_card[0]
        card.hindi = new_card[1]
        card.option1 = new_card[2]
        card.option2 = new_card[3]
        card.option3 = new_card[4]
        card.option4 = new_card[5]

        db.session.add(card)
        db.session.commit()

        allCards = Deck.query.all()
        return render_template('deck.html', allCards=allCards)

    card = Deck.query.filter_by(sno=sno).first()
    return render_template('update_card.html', card=card)


if __name__ == '__main__':
    app.run(debug=True)
