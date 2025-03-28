from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    highest_score = db.Column(db.Integer, default=0)
    scores = db.relationship('Score', backref='user', lazy=True)  

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)


with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form.get('username')
        
        if username:
            user = User.query.filter_by(username=username).first()
            
            if not user:
                user = User(username=username)
                db.session.add(user)
                db.session.commit()

        
            session['user_id'] = user.id
            session['username'] = user.username
            
            return redirect('/exam')
    return render_template('index.html')

@app.route('/exam')
def exam():
    user_id = session.get('user_id')
    user_highest_score = None

    if user_id:
        user_highest_score = db.session.query(db.func.max(Score.score)).filter_by(user_id=user_id).scalar() or 0

    highest_overall = db.session.query(db.func.max(Score.score)).scalar() or 0

    return render_template('exam.html', user_highest_score=user_highest_score, highest_overall=highest_overall)


@app.route('/submit', methods=['POST'])
def submit():
    if 'username' not in session:
        return redirect(url_for('index'))

    username = session['username']
    user = User.query.filter_by(username=username).first()

    
    answers = {
        'q1': 'discord.py',
        'q2': 'python',
        'q3': 'bilgisayar görüşü',
        'q4': 'python',
        'q5': 'web scraping'
    }
    score = 0
    for question, correct_answer in answers.items():
        if request.form.get(question) == correct_answer:
            score += 20

    current_score = score
    
    if score > user.highest_score:
        user.highest_score = score

    
    user.last_score = score

    
    new_score = Score(user_id=user.id, score=score)
    db.session.add(new_score)
    db.session.commit()

    
    highest_overall = db.session.query(db.func.max(Score.score)).scalar() or 0

    
    return render_template(
        'result.html',
        current_score=current_score,
        user_highest_score=user.highest_score,
        highest_overall=highest_overall 
    )


@app.route('/result')
def result():
    if 'user_id' not in session:
        return redirect('/')
    return render_template('result.html')

if __name__ == '__main__':
    app.run(debug=True)
