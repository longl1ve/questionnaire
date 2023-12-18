from flask import Flask, session, render_template, redirect, request, Response, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
import random
from datetime import datetime

app = Flask('questionnaire', static_folder='D:\\questionnaire')
app.config["SECRET_KEY"] = '12345'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///questionnaire.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    surveys = db.relationship('Surveys', backref='author')
    sessions = db.relationship('Sessions', backref='respondent')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Surveys(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(500), unique=True, nullable=False)
    access = db.Column(db.Boolean, nullable=False)
    title = db.Column(db.String(500), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    questions = db.relationship('Questions', backref='survey')
    sessions = db.relationship('Sessions', backref='survey')


class Sessions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'), nullable=False)
    date_time = db.Column(db.String(500), nullable=False)
    answersforsessions = db.relationship('Answersforsessions', backref='session')


class Answersforsessions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    answer_id = db.Column(db.Integer, db.ForeignKey('answers.id'), nullable=False)


class Questions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(3000), nullable=False)
    num_in_survey = db.Column(db.Integer, nullable=False)
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'), nullable=False)
    answers = db.relationship('Answers', backref='question')
    answersforsessions = db.relationship('Answersforsessions', backref='question')


class Answers(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(3000), nullable=False)
    num_in_question = db.Column(db.Integer, nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    answersforsessions = db.relationship('Answersforsessions', backref='answer')
    report = db.relationship('Reports', uselist=False, backref='answer')


class Reports(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    percentage = db.Column(db.Float)
    answer_id = db.Column(db.Integer, db.ForeignKey('answers.id'), nullable=False)


@app.route('/')
def main():
    session['survey_changed'] = False
    return render_template('index.html')


@app.route('/create')
def create():
    session['survey_closed'] = False
    session['survey_sent'] = False
    session['survey_not_found'] = False
    session['survey_changed'] = False
    session['survey_created'] = False
    session['email_exists_alert'] = False
    return render_template('create.html')


@app.route('/cabinet')
def cabinet():
    session['survey_closed'] = False
    session['survey_sent'] = False
    session['survey_not_found'] = False
    session['survey_created'] = False
    session['email_exists_alert'] = False
    try:
        user = Users.query.filter_by(id=session['user']).first()
        surveys_user = Surveys.query.filter_by(user_id=session['user']).all()
        return render_template('cabinet.html', user=user, surveys=surveys_user)
    except:
        return render_template('cabinet.html')


@app.route('/profile')
def profile():
    session['survey_not_found'] = False
    session['survey_changed'] = False
    session['mysurveys'] = False
    session['analytics'] = False
    session['creategraphic'] = False
    session['profile'] = True
    return redirect('/cabinet')


@app.route('/mysurveys')
def mysurveys():
    session['profile'] = False
    session['analytics'] = False
    session['creategraphic'] = False
    session['mysurveys'] = True
    return redirect('/cabinet')


@app.route('/analytics-cabinet')
def analytics_cabinet():
    session['survey_changed'] = False
    session['profile'] = False
    session['mysurveys'] = False
    session['creategraphic'] = False
    session['analytics'] = True
    return redirect('/cabinet')


@app.route('/creategraphic')
def creategraphic():
    session['survey_changed'] = False
    session['profile'] = False
    session['mysurveys'] = False
    session['analytics'] = False
    session['creategraphic'] = True
    return redirect('/cabinet')


@app.route('/analytics-sessions/<int:survey_code>')
def analytics_sessions(survey_code):
    session['analytics_report'] = False
    session['analytics_sessions'] = True

    survey_by_code = Surveys.query.filter_by(code=survey_code).first()
    try:
        if survey_by_code.author.id == session['user']:
            pass
        else:
            return redirect('/')
    except:
        return redirect('/')

    return redirect(url_for('analytics', survey_code=survey_code))


@app.route('/analytics-report/<int:survey_code>')
def analytics_report(survey_code):
    session['analytics_sessions'] = False
    session['analytics_report'] = True

    survey_by_code = Surveys.query.filter_by(code=survey_code).first()
    try:
        if survey_by_code.author.id == session['user']:
            pass
        else:
            return redirect('/')
    except:
        return redirect('/')

    return redirect(url_for('analytics', survey_code=survey_code))


@app.post('/registration')
def registration():
    session['survey_not_found'] = False
    form = request.form
    user = Users(
        name=form['nameSignUp'],
        email=form['emailSignUp']
    )

    user_email = Users.query.filter_by(email=form['emailSignUp']).first()
    if user_email:
        session['survey_closed'] = False
        session['survey_sent'] = False
        session['survey_changed'] = False
        session['survey_created'] = False
        session['email_alert'] = False
        session['password_alert'] = False
        session['email_exists_alert'] = True
        return redirect('/')
    elif form['passwordSignUp'] == form['password2SignUp']:
        user.set_password(form['passwordSignUp'])
        db.session.add(user)
        db.session.commit()
        session['survey_closed'] = False
        session['survey_sent'] = False
        session['survey_changed'] = False
        session['survey_created'] = False
        session['email_alert'] = False
        session['password_alert'] = False
        session['email_exists_alert'] = False
        session['registration_alert'] = True
        return redirect('/')
    else:
        session['survey_closed'] = False
        session['survey_sent'] = False
        session['survey_changed'] = False
        session['survey_created'] = False
        session['email_alert'] = False
        session['password_alert'] = False
        return Response(status=204)


@app.post('/log-in')
def log_in():
    form = request.form
    user = Users.query.filter_by(email=form['emailSignIn']).first()
    if not user:
        session['survey_closed'] = False
        session['survey_sent'] = False
        session['survey_not_found'] = False
        session['email_exists_alert'] = False
        session['password_alert'] = False
        session['email_alert'] = True
        return redirect('/')
    elif user.check_password(form['passwordSignIn']):
        session['survey_closed'] = False
        session['survey_sent'] = False
        session['survey_not_found'] = False
        session['email_exists_alert'] = False
        session['email_alert'] = False
        session['password_alert'] = False
        session['registration_alert'] = False
        session['user'] = user.id
        session['logged_in'] = True
        return redirect('/')
    else:
        session['survey_closed'] = False
        session['survey_sent'] = False
        session['survey_not_found'] = False
        session['email_exists_alert'] = False
        session['email_alert'] = False
        session['password_alert'] = True
        return redirect('/')


@app.post('/log-in-page-cabinet')
def log_in_page_cabinet():
    form = request.form
    user = Users.query.filter_by(email=form['emailSignIn']).first()
    if not user:
        session['email_alert'] = True
        session['password_alert'] = False
        return redirect('/cabinet')
    elif user.check_password(form['passwordSignIn']):
        session['email_alert'] = False
        session['password_alert'] = False
        session['registration_alert'] = False
        session['user'] = user.id
        session['logged_in'] = True
        return redirect('/cabinet')
    else:
        session['email_alert'] = False
        session['password_alert'] = True
        return redirect('/cabinet')


@app.post('/log-in-page-create')
def log_in_page_create():
    form = request.form
    user = Users.query.filter_by(email=form['emailSignIn']).first()
    if not user:
        session['email_alert'] = True
        session['password_alert'] = False
        return redirect('/create')
    elif user.check_password(form['passwordSignIn']):
        session['email_alert'] = False
        session['password_alert'] = False
        session['registration_alert'] = False
        session['user'] = user.id
        session['logged_in'] = True
        return redirect('/create')
    else:
        session['email_alert'] = False
        session['password_alert'] = True
        return redirect('/create')


@app.route('/log-out')
def log_out():
    session['survey_closed'] = False
    session['survey_changed'] = False
    session['survey_created'] = False
    session['user'] = 0
    session['logged_in'] = False
    return redirect('/')


@app.post('/create-survey')
def create_survey():
    form = request.form

    code_int = random.randint(5000000000000000, 9999999999999999)
    survey_int = Surveys.query.filter_by(code=code_int).first()
    while survey_int:
        code_int = random.randint(5000000000000000, 9999999999999999)
        survey_int = Surveys.query.filter_by(code=code_int).first()
        if not survey_int:
            break

    survey = Surveys(
        code=int(code_int),
        access=True,
        title=form['title-text'],
        user_id=session['user']
    )
    db.session.add(survey)
    db.session.commit()

    survey_id_id = survey.id

    question_count = 0

    print(survey_id_id)
    print("title : ", form['title-text'])

    for key in form.keys():
        question_bool = key.startswith("question")
        answer_bool = key.startswith("answer")
        answer_count = 0

        if question_bool:
            for value in form.getlist(key):
                question_text = value
                question_count += 1

                question = Questions(
                    text=str(question_text),
                    num_in_survey=int(question_count),
                    survey_id=int(survey_id_id)
                )
                db.session.add(question)
                db.session.commit()

                question_id_id = question.id

                print("question_text : ", question_text, "; question_count : ", question_count, "; survey_id : ", survey_id_id)

        elif answer_bool:
            for value in form.getlist(key):
                answer_text = value
                answer_count += 1

                answer = Answers(
                    text=str(answer_text),
                    num_in_question=int(answer_count),
                    question_id=int(question_id_id)
                )
                db.session.add(answer)
                db.session.commit()

                print("answer_text : ", answer_text, "; answer_count : ", answer_count, "; question_id : ", question_id_id)

        else:
            pass

    session['survey_created'] = True
    return redirect('/')


@app.route('/analytics/<int:survey_code>')
def analytics(survey_code):
    survey_by_code = Surveys.query.filter_by(code=survey_code).first()
    try:
        if survey_by_code.author.id == session['user']:
            pass
        else:
            return redirect('/')
    except:
        return redirect('/')

    questions = survey_by_code.questions
    for question in questions:

        answer_array = []
        for answer in question.answers:
            answer_array.append(len(answer.answersforsessions))

        answers_sum = sum(answer_array)
        for amount, answer in zip(answer_array, question.answers):
            percentage = (amount / answers_sum) * 100

            if answer.report:
                report = answer.report
                report.percentage = percentage
                db.session.add(report)
                db.session.commit()
            else:
                report = Reports(
                    percentage=str(percentage),
                    answer_id=int(answer.id)
                )
                db.session.add(report)
                db.session.commit()

    return render_template("analytics.html", survey=survey_by_code)


@app.post('/change-survey/<int:survey_id>')
def change_survey(survey_id):
    survey_by_id = Surveys.query.filter_by(id=survey_id).first()

    form = request.form

    sessions_to_delete_by_changing = Sessions.query.filter_by(survey_id=survey_id)
    for session_n in sessions_to_delete_by_changing:
        session_id = session_n.id
        answersforsession_to_delete_by_changing = Answersforsessions.query.filter_by(session_id=session_id)
        for answer in answersforsession_to_delete_by_changing:
            db.session.delete(answer)
            db.session.commit()

        db.session.delete(session_n)
        db.session.commit()

    questions_to_delete_by_changing = Questions.query.filter_by(survey_id=survey_id)
    for question in questions_to_delete_by_changing:
        question_id = question.id
        answers_to_delete_by_changing = Answers.query.filter_by(question_id=question_id)
        for answer in answers_to_delete_by_changing:
            db.session.delete(answer)
            db.session.commit()

        db.session.delete(question)
        db.session.commit()

    question_count = 0

    for key in form.keys():
        question_bool = key.startswith("question")
        answer_bool = key.startswith("answer")
        answer_count = 0

        if question_bool:
            for value in form.getlist(key):
                question_text = value
                question_count += 1

                question = Questions(
                    text=str(question_text),
                    num_in_survey=int(question_count),
                    survey_id=int(survey_id)
                )
                db.session.add(question)
                db.session.commit()

                question_id_id = question.id

        elif answer_bool:
            for value in form.getlist(key):
                answer_text = value
                answer_count += 1

                answer = Answers(
                    text=str(answer_text),
                    num_in_question=int(answer_count),
                    question_id=int(question_id_id)
                )
                db.session.add(answer)
                db.session.commit()

        else:
            pass

    session['survey_changed'] = True
    return redirect('/cabinet')


@app.post('/change-survey-access/<int:survey_id>')
def change_survey_access(survey_id):
    survey_by_id = Surveys.query.filter_by(id=survey_id).first()

    if request.form.get('switch'):
        switch_checked = True
    else:
        switch_checked = False

    print(switch_checked)
    survey_by_id.access = switch_checked
    db.session.add(survey_by_id)
    db.session.commit()

    return redirect('/cabinet')


@app.post('/delete-survey/<int:survey_id>')
def delete_survey(survey_id):
    survey_by_id = Surveys.query.filter_by(id=survey_id).first()

    sessions_to_delete_by_changing = Sessions.query.filter_by(survey_id=survey_id)
    for session_n in sessions_to_delete_by_changing:
        session_id = session_n.id
        answersforsession_to_delete_by_changing = Answersforsessions.query.filter_by(session_id=session_id)
        for answer in answersforsession_to_delete_by_changing:
            db.session.delete(answer)
            db.session.commit()

        db.session.delete(session_n)
        db.session.commit()

    questions_to_delete_by_changing = Questions.query.filter_by(survey_id=survey_id)
    for question in questions_to_delete_by_changing:
        question_id = question.id
        answers_to_delete_by_changing = Answers.query.filter_by(question_id=question_id)
        for answer in answers_to_delete_by_changing:
            db.session.delete(answer)
            db.session.commit()

        db.session.delete(question)
        db.session.commit()

    db.session.delete(survey_by_id)
    db.session.commit()
    return redirect('/cabinet')


@app.route('/mysurvey/<int:survey_code>')
def my_survey(survey_code):
    session['survey_changed'] = False

    survey_by_code = Surveys.query.filter_by(code=survey_code).first()
    try:
        if survey_by_code.author.id == session['user']:
            pass
        else:
            return redirect('/')
    except:
        return redirect('/')

    return render_template('mysurvey.html', survey=survey_by_code)


@app.post('/survey-redirect')
def survey_redirect():
    session['survey_not_found'] = False

    survey_code = request.form['survey_code']
    return redirect(url_for('survey', survey_code=survey_code))


@app.route('/survey/<int:survey_code>')
def survey(survey_code):
    session['survey_closed'] = False
    session['survey_sent'] = False
    session['survey_changed'] = False

    try:
        survey_by_code = Surveys.query.filter_by(code=survey_code).first()
        access = survey_by_code.access
        if survey_by_code and access == True:
            return render_template('survey.html', survey=survey_by_code)
        elif not access:
            session['survey_closed'] = True
            return redirect('/')
        else:
            session['survey_not_found'] = True
            return redirect('/')
    except:
        session['survey_not_found'] = True
        return redirect('/')


@app.route('/session-view/<int:session_id>')
def session_view(session_id):
    session_by_id = Sessions.query.filter_by(id=session_id).first()

    try:
        if session_by_id.survey.user_id == session['user']:
            pass
        else:
            return redirect('/')
    except:
        return redirect('/')

    return render_template('session.html', session_current=session_by_id)


@app.post('/send/<int:survey_id>')
def send(survey_id):
    form = request.form

    survey_by_id = Surveys.query.filter_by(id=survey_id).first()
    a = datetime.now()
    now = a.strftime("%d/%m/%Y, %H:%M:%S")

    try:
        if session['logged_in']:
            session_current = Sessions(
                user_id=session['user'],
                survey_id=survey_id,
                date_time=now
            )
        else:
            session_current = Sessions(
                user_id=0,
                survey_id=survey_id,
                date_time=now
            )
    except:
        session_current = Sessions(
            user_id=0,
            survey_id=survey_id,
            date_time=now
        )

    db.session.add(session_current)
    db.session.commit()

    session_current_id = session_current.id

    for key in form.keys():
        radio_bool = key.startswith("radio")

        if radio_bool:
            for value in form.getlist(key):
                answer_id = value
                answer_by_id = Answers.query.filter_by(id=answer_id).first()
                question_id = answer_by_id.question.id

                answersforsessions = Answersforsessions(
                    session_id=session_current_id,
                    question_id=int(question_id),
                    answer_id=int(answer_id)
                )
                db.session.add(answersforsessions)
                db.session.commit()

        else:
            pass

    session['survey_sent'] = True
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=False)
