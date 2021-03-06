from flask import Flask, render_template, request, redirect, url_for
import numpy as np
import pandas as pd
import pickle
import mysql.connector
import datetime


model = pickle.load(open('model.pkl', 'rb'))
app = Flask(__name__)
global name
name = ""
global mobile
mobile = "-000-"

db = mysql.connector.connect(
    host='freedb.tech',
    user='freedbtech_deepraj',
    passwd='deep123@raj',
    database='freedbtech_myminorproject'
    )
# db = mysql.connector.connect(
#     host='db4free.net',
#     user='deep_132',
#     passwd='deep132@raj',
#     database='minor_132project'
# )

@app.route('/')
def start():
    return render_template('index.html')


@app.route('/reg', methods=["POST", "GET"])
def reg():
    return render_template('first.html')


@app.route('/already', methods=["POST", "GET"])
def already():
    return render_template('already.html')


@app.route('/logout')
def logout():
    return render_template('first.html')


# @app.route('/hom', methods=['POST', 'GET'])
# def hom():
#     global name
#     global mobile

#     cred = request.form["mob"]
#     cursor = db.cursor()
#     cursor.execute("select * from user")
#     x = ()
#     for i in cursor:
#         if (i[1] == cred) or (i[2] == cred):
#             x = i
#     if len(x) > 1:
#         name = x[0]
#         mobile = x[1]
#         return render_template('home.html', name_nam=name.title())
#     else:
#         return render_template('already.html', alert="Account not find !!!")
@app.route('/hom', methods=['POST', 'GET'])
def hom():
    global name
    global mobile
    try:
        cred = request.form["mob"]
    except Exception:
        return redirect(url_for('reg'))
    cursor = db.cursor()
    cursor.execute("select * from user")
    x = ()
    for i in cursor:
        if (i[1] == cred) or (i[2] == cred):
            x = i
    if len(x) > 1:
        name = x[0]
        mobile = x[1]
        return render_template('home.html', name_nam=name.title())
    else:
        return render_template('already.html', alert="Account not find !!!")

@app.route('/home', methods=["POST", "GET"])
def home():
    global name
    global mobile
    alert = ''
    name = request.form["name"]
    email = request.form["email"]
    mobile = request.form["mobile"]
    cursor = db.cursor()
    cursor.execute("select * from user")
    for i in cursor:
        if i[1] == mobile:
            alert = 'Mobile no already Registered'

        elif i[2] == email:
            alert = 'Email already Registered'

    if len(alert) > 5:
        return render_template('first.html', msg=alert)
    cursor = db.cursor()
    current_time = datetime.datetime.now()
    date = current_time.date()
    time = "{}:{}".format(current_time.time().hour, current_time.time().minute)
    detail = (name, mobile, email, date, time)
    statement = "Insert into user (name, mobile, email, date, time) values(%s, %s, %s, %s, %s)"
    cursor.execute(statement, detail)
    db.commit()
    return render_template('home.html', name_nam=str(name.title()))


@app.route('/prediction', methods=["POSt", "GET"])
def prediction():

    return render_template('predict.html', name=name.title())


@app.route('/Home', methods=["POST", "GET"])
def Home():
    return render_template('home.html', name_nam=str(name.title()))


@app.route('/symptom', methods=["POST", "GET"])
def symptom():
    return render_template('symptoms.html')


@app.route('/prevention', methods=["POSt", "GET"])
def prevention():

    return render_template('prevention.html')


@app.route('/about', methods=["POSt", "GET"])
def about():

    return render_template('about.html')


@app.route('/predict', methods=["POST", "GET"])
def predict():


    input_features = []

    for x in request.form.values():
        x = float(x)
        input_features.append(x)
        
    if len(input_features) == 0:
        return redirect(url_for('prediction'))
      
    features_value = [np.array(input_features)]
    features_name = ['mean radius', 'mean texture', 'mean perimeter', 'mean area',
                     'mean smoothness', 'mean compactness', 'mean concavity',
                     'mean concave points', 'mean symmetry', 'mean fractal dimension',
                     'radius error', 'texture error', 'perimeter error', 'area error',
                     'smoothness error', 'compactness error', 'concavity error',
                     'concave points error', 'symmetry error', 'fractal dimension error',
                     'worst radius', 'worst texture', 'worst perimeter', 'worst area',
                     'worst smoothness', 'worst compactness', 'worst concavity',
                     'worst concave points', 'worst symmetry', 'worst fractal dimension']
    df = pd.DataFrame(features_value, columns=features_name)
    output = model.predict(df)
    cursor = db.cursor()
    current_time = datetime.datetime.now()
    date = current_time.date()
    time = "{}:{}".format(current_time.time().hour, current_time.time().minute)
    statement_result = "Insert into result (mobile, output, date, time) values( %s, %s, %s, %s)"
    detail = (mobile, str(output[0]), date, time)
    cursor.execute(statement_result, detail)
    db.commit()
    if output == 0:
        result_value = "Patient has higher chance of Breast cancer "
        suggestion = "You need to concern with the doctor."
        return render_template('result.html', cancer_txt=result_value, sugs_txt=suggestion)
    else:
        result_value = "Patient has no Breast Cancer"
        return render_template('result.html', cancer_txt=result_value)


@app.route('/contact', methods=["POST", "GET"])
def contact():
      return render_template('contact.html')

@app.route('/feedback', methods=["POST", "GET"])
def feedback():
    return render_template('feedback.html')


@app.route('/submit', methods=["POST", "GET"])
def submit():
    feedback = []
    for i in request.form.values():
        if len(i) == 0:
            feedback.append("NAN")
            continue
        feedback.append(i)
        
        
    if len(feedback) == 5:
        feedback.append('NAN')
        
    statement = "Insert into FEEDBACK (mobile, rating, descr, needed, suggest, report, probl)" \
                " values(%s, %s, %s, %s, %s, %s, %s)"
    detail = (mobile, feedback[0], feedback[1], feedback[2], feedback[3], feedback[4], feedback[5])
    cursor = db.cursor()
    cursor.execute(statement, detail)
    db.commit()
    return render_template('last.html')
  

@app.route('/send', methods=['POST', 'GET'])
def send():
    credential = []
    for data in request.form.values():
        credential.append(data)
    statement = "Insert into message (name, email, msg)" \
                " values(%s, %s, %s)"
    information = (credential[0], credential[1], credential[2])
    cursor = db.cursor()
    cursor.execute(statement, information)
    db.commit()
    return render_template('contact.html')


if __name__ == '__main__':
    app.run(debug=True)
