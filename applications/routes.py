from flask import request, session, render_template, flash, redirect, url_for
from main import app
from applications.models import *
from datetime import datetime
import plotly.express as px
import plotly.utils
import json
from collections import Counter, defaultdict

@app.route('/')
def index():
    if session.get('user_email'):
        if session['user_role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('user_dashboard'))
    return render_template("index.html")

@app.route('/admin_dashboard')
def admin_dashboard():
    subjects = Subject.query.all()
    chapters = Chapter.query.all()
    quizzes = Quiz.query.all()
    questions = Question.query.all()
    quiz_chapter_map = {quiz.id: quiz.chapter_id for quiz in quizzes}
    chapter_question_count = {}
    for chapter in chapters:
        count = sum(
            1 for question in questions if quiz_chapter_map.get(question.quiz_id) == chapter.id
        )
        chapter_question_count[chapter.id] = count
    
    if 'user_email' not in session:
        flash("Please log in to access the dashboard.", "warning")
        return redirect(url_for('login'))
    
    if session['user_role'] != 'admin':
        flash("You are not authorized to access this page.", "warning")
        return redirect(url_for('user_dashboard'))
    
    return render_template('admin_dashboard.html', subjects=subjects, chapters=chapters, quizzes=quizzes, questions=questions, chapter_question_count=chapter_question_count)

@app.route('/user_dashboard')
def user_dashboard():
    if session['user_role'] != 'user':
        flash("You are logged in as an admin.", "warning")
        return redirect(url_for('admin_dashboard'))
    date = datetime.now().date()
    subjects = Subject.query.all()
    chapters = Chapter.query.all()
    quizzes = Quiz.query.all()
    questions = Question.query.all()
    quiz_chapter_map = {quiz.id: quiz.chapter_id for quiz in quizzes}
    chapter_question_count = {}
    for chapter in chapters:
        count = sum(
            1 for question in questions if quiz_chapter_map.get(question.quiz_id) == chapter.id
        )
        chapter_question_count[chapter.id] = count
        
    if 'user_email' not in session:
        flash("Please log in to access the dashboard.", "warning")
        return redirect(url_for('login'))
    
    return render_template('user_dashboard.html', subjects=subjects, chapters=chapters, quizzes=quizzes, questions=questions, chapter_question_count=chapter_question_count, date=date)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Please enter email and password')
            return render_template("login.html")
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('User not found')
            return render_template("login.html")
        
        if user.password != password:
            flash('Incorrect password')
            return render_template("login.html")
        
        session['user_id'] = user.id
        session['user_email'] = user.email
        session['user_name'] = user.name
        session['user_role'] = user.roles[0].name
        flash('Logged in successfully')
        
        if user.roles[0].name == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_email', None)
    session.pop('user_role', None)
    session.pop('user_name', None)
    return redirect("/login")

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        name = request.form.get('name')
        qualifications = request.form.get('qualifications')
        dob_str = request.form.get('dob')  # Get date string from form
        dob = datetime.strptime(dob_str, "%Y-%m-%d").date()  # Convert to date object
        role = request.form.get('role')
        
        if User.query.filter_by(email=email).first():
            flash('User already exists')
            return render_template("register.html")
        
        if not email or not password or not confirm_password or not name or not qualifications or not dob:
            flash('Please enter all fields')
            return render_template("register.html")
        
        if password != confirm_password:
            flash('Passwords do not match')
            return render_template("register.html")
        
        role_object = Role.query.filter_by(name=role).first()
        
        user = User(email=email, password=password, name=name, qualifications=qualifications, dob=dob, roles=[role_object])
        db.session.add(user)
        
        db.session.commit()
        flash('User Registered successfully')
        return render_template("login.html")

@app.route('/user_management')
def user_management():
    if 'user_email' not in session:
        flash("Please log in to access the dashboard.", "warning")
        return redirect(url_for('login'))
    
    if session['user_role'] != 'admin':
        flash("You are not authorized to access this page.", "warning")
        return redirect(url_for('user_dashboard'))
    
    users = User.query.filter(User.roles.any(name='user')).all()
    return render_template('admin_search/user_management.html', users=users)

@app.route('/remove_user/<int:user_id>')
def remove_user(user_id):
    if session['user_role'] != 'admin':
        flash("You are not authorized to access this page.", "warning")
        return redirect(url_for('user_dashboard'))
    
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('User removed successfully')
    else:
        flash('User not found')
    return redirect(url_for('user_management'))

@app.route('/summary')
def summary():
    if 'user_email' not in session:
        flash('Please log in to access summary')
        return redirect(url_for('login'))

    if session['user_role'] == 'user':
        subjects = Subject.query.all()
        quizzes = Quiz.query.all()
        chapters = Chapter.query.all()

        # Create a mapping of subject_id to subject_name
        subject_map = {subject.id: subject.name for subject in subjects}

        # Fetch subject-wise quiz counts correctly
        subject_wise_quiz_count = Counter()
        for quiz in quizzes:
            chapter = Chapter.query.get(quiz.chapter_id)  # Get chapter of the quiz
            if chapter and chapter.subject_id in subject_map:  
                subject_wise_quiz_count[subject_map[chapter.subject_id]] += 1

        sub_keys = list(subject_wise_quiz_count.keys())
        sub_values = list(subject_wise_quiz_count.values())

        # Monthly quiz count (only include months with quizzes)
        monthly_quiz_count = Counter()
        for quiz in quizzes:
            month_name = quiz.date_of_quiz.strftime('%b')  # Short month name (Jan, Feb, etc.)
            monthly_quiz_count[month_name] += 1

        monthly_keys = list(monthly_quiz_count.keys())
        monthly_values = list(monthly_quiz_count.values())

        # Create Subject-wise Bar Chart using Plotly
        bar_fig = px.bar(
            x=sub_keys, y=sub_values, 
            labels={'x': 'Subjects', 'y': 'Number of Quizzes'}, 
            title="Subject-wise Quiz Distribution", 
            text=sub_values
        )

        # Explicitly set category order to ensure all subjects appear correctly
        bar_fig.update_layout(
            xaxis=dict(categoryorder='array', categoryarray=sub_keys)
        )

        # Ensure all bars are displayed properly
        bar_fig.update_traces(textposition='outside', marker_color='blue')

        # Create Monthly Quiz Pie Chart using Plotly
        pie_fig = px.pie(
            names=monthly_keys, values=monthly_values,
            title="Monthly Quiz Distribution",
            hole=0.4
        )

        # Ensure the legend and layout are clear
        pie_fig.update_traces(textinfo='percent+label')
        
        # Theming the charts
        bar_colors = ["#8A2BE2", "#00CC96", "#FF69B4", "#1E90FF", "#FF8C00", "#FFD700", "#FF1493", "#00CED1", "#FF4500", "#ADFF2F"]

        # Extend color list if there are more subjects than colors
        bar_colors *= (len(sub_keys) // len(bar_colors)) + 1
        bar_colors = bar_colors[:len(sub_keys)]  # Trim to the exact number of subjects
        bar_chart_json = json.dumps({
            "data": [{
                "type": "bar",
                "x": sub_keys,
                "y": sub_values,
                "marker": {"color": bar_colors}
            }],
            "layout": {
                "title": {"text": "Subject-wise Quiz Distribution", "font": {"color": "white"}},
                "xaxis": {
                    "categoryorder": "array",
                    "categoryarray": sub_keys,
                    "tickfont": {"color": "white"}
                },
                "yaxis": {"tickfont": {"color": "white"}},
                "paper_bgcolor": "#2d3033",
                "plot_bgcolor": "#2d3033",
                "font": {"color": "white"}
            }
        })

        pie_chart_json = json.dumps({
            "data": [{
                "type": "pie",
                "labels": monthly_keys,
                "values": monthly_values,
                "marker": {"colors": ["#636EFA", "#EF553B", "#00CC96", "#FFDAB9", "#1E90FF", "#FF8C00", "#8A2BE2", "#FF1493", "#00CED1", "#FF4500", "#FF69B4", "#ADFF2F"]}
            }],
            "layout": {
                "title": {"text": "Monthly Quiz Distribution", "font": {"color": "white"}},
                "paper_bgcolor": "#2d3033",
                "plot_bgcolor": "#2d3033",
                "font": {"color": "white"}
            }
        })

        return render_template(
            'user_search/summary.html',
            subjects=subjects, quizzes=quizzes, chapters=chapters,
            subject_wise_quiz_count=subject_wise_quiz_count, monthly_quiz_count=monthly_quiz_count,
            sub_keys=sub_keys, sub_values=sub_values,
            monthly_keys=monthly_keys, monthly_values=monthly_values,
            bar_chart_json=bar_chart_json, pie_chart_json=pie_chart_json
        )

    if session['user_role'] == 'admin':
        users = User.query.filter(User.id != 1).all()
        scores = Score.query.all()
        user_attempts = UserAttempt.query.all()
        quizzes = Quiz.query.all()
        chapters = Chapter.query.all()
        subjects = Subject.query.all()
        
        # Subject wize top score
        # Initialize all subjects with zero
        subject_wise_top_score = {subject.name: 0 for subject in subjects}

        # Update only if a score exists
        for score in scores:
            quiz = Quiz.query.get(score.quiz_id)
            chapter = Chapter.query.get(quiz.chapter_id)
            subject = Subject.query.get(chapter.subject_id)
            subject_wise_top_score[subject.name] = max(subject_wise_top_score[subject.name], score.total_scored)

        sub_keys = list(subject_wise_top_score.keys())
        sub_values = list(subject_wise_top_score.values())
        
        # Bar chart
        bar_fig = px.bar(
            x=sub_keys, y=sub_values, 
            labels={'x': 'Subjects', 'y': 'Top Score'}, 
            title="Subject-wise Top Score Distribution", 
            text=sub_values
        )

        # Explicitly set category order to ensure all subjects appear correctly
        bar_fig.update_layout(
            xaxis=dict(categoryorder='array', categoryarray=sub_keys)
        )

        # Ensure all bars are displayed properly
        bar_fig.update_traces(textposition='outside', marker_color='blue')
        
        # Theming the charts
        bar_colors = ["#8A2BE2", "#00CC96", "#FF69B4", "#1E90FF", "#FF8C00", "#FFD700", "#FF1493", "#00CED1", "#FF4500", "#ADFF2F"]

        # Extend color list if there are more subjects than colors
        bar_colors *= (len(sub_keys) // len(bar_colors)) + 1
        bar_colors = bar_colors[:len(sub_keys)]  # Trim to the exact number of subjects
        bar_chart_json = json.dumps({
            "data": [{
                "type": "bar",
                "x": sub_keys,
                "y": sub_values,
                "marker": {"color": bar_colors}
            }],
            "layout": {
                "title": {"text": "Subject-wise Top Score", "font": {"color": "white"}},
                "xaxis": {
                    "categoryorder": "array",
                    "categoryarray": sub_keys,
                    "tickfont": {"color": "white"}
                },
                "yaxis": {"tickfont": {"color": "white"}},
                "paper_bgcolor": "#2d3033",
                "plot_bgcolor": "#2d3033",
                "font": {"color": "white"}
            }
        })
        
        # Pie chart for Subject wise user attempts
        # Initialize attempts dictionary
        subject_wise_user_attempts = defaultdict(int)

        # Efficiently fetch all relevant data using joins
        attempt_data = (
            db.session.query(Subject.name, db.func.count(UserAttempt.id))
            .join(Chapter, Chapter.subject_id == Subject.id)
            .join(Quiz, Quiz.chapter_id == Chapter.id)
            .join(UserAttempt, UserAttempt.quiz_id == Quiz.id)
            .group_by(Subject.name)
            .all()
        )

        # Store aggregated attempts
        for subject_name, attempt_count in attempt_data:
            subject_wise_user_attempts[subject_name] = attempt_count

        # # Fetch total questions per subject efficiently
        # subject_question_counts = dict(
        #     db.session.query(Subject.name, db.func.count(Question.id))
        #     .join(Chapter, Chapter.subject_id == Subject.id)
        #     .join(Quiz, Quiz.chapter_id == Chapter.id)
        #     .join(Question, Question.quiz_id == Quiz.id)
        #     .group_by(Subject.name)
        #     .all()
        # )

        # # Normalize attempts by total questions per subject
        # for subject, attempts in subject_wise_user_attempts.items():
        #     total_questions = subject_question_counts.get(subject, 1)  # Avoid division by zero
        #     subject_wise_user_attempts[subject] = round(attempts / total_questions, 2)

        # Convert data for pie chart
        pie_chart_json = json.dumps({
            "data": [{
                "type": "pie",
                "labels": list(subject_wise_user_attempts.keys()),
                "values": list(subject_wise_user_attempts.values()),
                "marker": {"colors": ["#636EFA", "#EF553B", "#00CC96", "#FFDAB9", "#1E90FF", "#FF8C00", "#8A2BE2", "#FF1493", "#00CED1", "#FF4500", "#FF69B4", "#ADFF2F"]}
            }],
            "layout": {
                "title": {"text": "Subject-wise User Attempts Distribution", "font": {"color": "white"}},
                "paper_bgcolor": "#2d3033",
                "plot_bgcolor": "#2d3033",
                "font": {"color": "white"}
            }
        })
        
        return render_template('admin_search/summary.html', users=users, scores=scores, user_attempts=user_attempts, quizzes=quizzes, chapters=chapters, subjects=subjects, sub_keys=sub_keys, sub_values=sub_values, bar_chart_json=bar_chart_json, pie_chart_json=pie_chart_json, subject_wise_user_attempts=subject_wise_user_attempts)

@app.route('/add_quiz', methods=['GET', 'POST'])
def add_quiz():
    if session['user_role'] != 'admin':
        flash("You are not authorized to access this page.", "warning")
        return redirect(url_for('user_dashboard'))
    
    if request.method == 'GET':
        return render_template("quiz.html")
    
    if request.method == 'POST':
        chapter_id = request.form.get('chapter_id')
        date_of_quiz = request.form.get('date_of_quiz')
        time_duration = request.form.get('time_duration')
        
        if not chapter_id or not date_of_quiz or not time_duration:
            flash('Please enter all fields')
            return render_template("quiz.html")
        
        try:
            date_of_quiz = datetime.strptime(date_of_quiz, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid date format")
            return render_template("quiz.html")
        
        # Validate and convert duration to seconds
        try:
            hh, mm, ss = map(int, time_duration.split(':'))
            time_duration_seconds = hh * 3600 + mm * 60 + ss
        except ValueError:
            flash("Invalid time format! Use HH:MM:SS.", "danger")
            return redirect(url_for('quiz'))
        
        quiz = Quiz(chapter_id=chapter_id, date_of_quiz=date_of_quiz, time_duration=time_duration)
        db.session.add(quiz)
        db.session.commit()
        flash('Quiz added successfully')
        return redirect("/quiz")

@app.route('/quiz')
def quiz():
    if 'user_email' not in session:
        flash("Please log in to access the dashboard.", "warning")
        return redirect(url_for('login'))
    
    if session['user_role'] != 'admin':
        flash("You are not authorized to access this page.", "warning")
        return redirect(url_for('user_dashboard'))
    
    all_quiz = Quiz.query.all()  # Fetch all quizzes from the database
    all_chapters = Chapter.query.all() # Fetch all chapters from the database
    quiz_chapter_map = {quiz.id: quiz.chapter_id for quiz in all_quiz}
    return render_template("quiz.html", quizzes=all_quiz, chapters=all_chapters, quiz_chapter_map=quiz_chapter_map)

@app.route('/quiz/<int:quiz_id>')
def quiz_details(quiz_id):
    if session['user_role'] != 'admin':
        flash("You are not authorized to access this page.", "warning")
        return redirect(url_for('user_dashboard'))
    quiz = Quiz.query.get_or_404(quiz_id)
    chapters = Chapter.query.all()
    return render_template("quiz_details.html", quiz=quiz, chapters=chapters)

@app.route('/subject/<int:subject_id>')
def subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    return render_template('user_search/subject.html', subject=subject, chapters=chapters)

@app.route('/chapter/<int:chapter_id>')
def chapter(chapter_id):
    subjects = Subject.query.all()
    chapter = Chapter.query.get_or_404(chapter_id)
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    return render_template('user_search/chapter.html', subjects=subjects, chapter=chapter, quizzes=quizzes)

@app.route("/quiz_master/<int:quiz_id>", methods=['GET', 'POST'])
def quiz_master(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return render_template("quiz_portal/quiz_master.html", quiz=quiz, questions=questions, getattr=getattr)

@app.route('/submit_quiz/<int:quiz_id>', methods=['POST'])
def submit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    
    # Determine the current attempt number for the user
    last_attempt = UserAttempt.query.filter_by(user_id=session['user_id'], quiz_id=quiz_id).order_by(UserAttempt.attempt_no.desc()).first()
    attempt_no = last_attempt.attempt_no + 1 if last_attempt else 1
    
    correct_count = 0
    
    # Store UserAttempt for each question
    for question in questions:
        selected_option = request.form.get(f'question_{question.id}')
        
        if selected_option is not None:
            selected_option = int(selected_option)
            is_correct = selected_option == question.correct_option
            if is_correct:
                correct_count += 1  # ✅ Increment correct count
        else:
            is_correct = False
            selected_option = None
        
        attempt = UserAttempt(
            attempt_no=attempt_no,
            user_id=session['user_id'],
            quiz_id=quiz.id,
            question_id=question.id,
            selected_option=selected_option,  # ✅ No need to convert None
            is_correct=is_correct
        )
        db.session.add(attempt)
    
    # Store total score only once per quiz attempt
    time_stamp = datetime.now().strftime("%H:%M:%S")  # ✅ Correct timestamp
    score = Score(quiz_id=quiz.id, user_id=session['user_id'], time_stamp_of_attempt=time_stamp, total_scored=correct_count)
    db.session.add(score)
    
    db.session.commit()
    
    flash(f'Quiz completed! Your Score: {correct_count}/{len(questions)}', 'success')
    return redirect(url_for('quiz_results', quiz_id=quiz_id))

@app.route('/quiz_result/<int:quiz_id>')
def quiz_results(quiz_id):
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    user_id = session.get('user_id')
    if not user_id:
        flash("User not logged in!", "danger")
        return redirect(url_for("login"))
    
    if session['user_role'] == 'admin':
        flash("You are logged in as an admin. Log in as a user to view your results.", "warning")
        return redirect(url_for('admin_dashboard'))

    attempts = UserAttempt.query.filter_by(user_id=user_id, quiz_id=quiz_id).all()

    score = sum(1 for a in attempts if a.is_correct)
    total_questions = len(attempts)

    return render_template('quiz_portal/quiz_result.html', score=score, total_questions=total_questions, questions=questions, getattr=getattr, attempts=attempts)

@app.route('/scores')
def scores():
    if session['user_role'] == 'admin':
        flash("You are logged in as an admin. Log in as a user to view your scores.", "warning")
        return redirect(url_for('admin_dashboard'))
    quizzes = Quiz.query.all()
    user_id = session.get('user_id')
    user_attempts = UserAttempt.query.filter_by(user_id=user_id).all()
    scores = Score.query.filter_by(user_id=user_id).all()
    return render_template('quiz_portal/scores.html', quizzes=quizzes, user_attempts=user_attempts, scores=scores)

@app.route('/view_quiz/<int:quiz_id>')
def view_quiz(quiz_id):
    subjects = Subject.query.all()
    chapters = Chapter.query.all()
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return render_template('quiz_portal/view_quiz.html', subjects=subjects, chapters=chapters, quiz=quiz, questions=questions)

@app.route('/search')
def search():
    query = request.args.get('query', '').strip().lower()  # Get the query and normalize it

    # Handle redirections based on specific keywords
    if query == "summary":
        return redirect(url_for('summary'))
    elif query == "quiz":
        return redirect(url_for('quiz'))
    elif query == "home":
        if session['user_role'] == 'user':
            return redirect(url_for('user_dashboard'))
        elif session['user_role'] == 'admin':
            return redirect(url_for('admin_dashboard'))
    elif query == "scores":
        return redirect(url_for('scores'))
    elif query == "manage users" or query == "user management" or query == "users" or query == "user":
        return redirect(url_for('user_management'))

    if session['user_role'] == 'user':
        user_id = session['user_id']
        subjects = Subject.query.filter(Subject.name.contains(query) | Subject.description.contains(query)).all()
        all_subjects = Subject.query.all()
        chapters = Chapter.query.filter(Chapter.name.contains(query) | Chapter.description.contains(query)).all()
        all_chapters = Chapter.query.all()
        quizzes = Quiz.query.filter(Quiz.chapter_id.contains(query)).all()
        all_quizzes = Quiz.query.all()
        dates = Quiz.query.filter(Quiz.date_of_quiz.contains(query)).all()
        scores = Score.query.filter(Score.user_id.contains(user_id), Score.total_scored.contains(query)).all()
        return render_template('user_search/search.html', query=query, subjects=subjects, all_subjects=all_subjects, chapters=chapters, all_chapters=all_chapters, quizzes=quizzes, all_quizzes=all_quizzes, dates=dates, scores=scores)

    if session['user_role'] == 'admin':
        subjects = Subject.query.filter(Subject.name.contains(query) | Subject.description.contains(query)).all()
        all_subjects = Subject.query.all()
        chapters = Chapter.query.filter(Chapter.name.contains(query) | Chapter.description.contains(query)).all()
        all_chapters = Chapter.query.all()
        quizzes = Quiz.query.filter(Quiz.chapter_id.contains(query)).all()
        all_quizzes = Quiz.query.all()
        users = User.query.filter(User.name.contains(query) | User.email.contains(query) | User.qualifications.contains(query) | User.dob.contains(query) | User.id.contains(query)).all()
        dates = Quiz.query.filter(Quiz.date_of_quiz.contains(query)).all()
        scores = Score.query.filter(Score.total_scored.contains(query)).all()
        return render_template('admin_search/search.html', query=query, subjects=subjects, all_subjects=all_subjects, chapters=chapters, all_chapters=all_chapters, quizzes=quizzes, all_quizzes=all_quizzes, users=users, dates=dates, scores=scores)