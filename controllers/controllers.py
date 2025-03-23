from flask import request, session, render_template, flash, redirect, url_for
from main import app
from applications.models import *
from datetime import datetime
import plotly.express as px
import plotly.utils
import json
from collections import Counter, defaultdict


@app.route('/edit_quiz/<int:quiz_id>', methods=['GET', 'POST'])
def edit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    all_chapters = Chapter.query.all()
    
    if 'user_email' not in session:
        flash("Please log in to access the dashboard.", "warning")
        return redirect(url_for('login'))
    
    if session['user_role'] != 'admin':
        flash("You are not authorized to access this page.", "warning")
        return redirect(url_for('user_dashboard'))
    
    if request.method == 'POST':
        quiz.chapter_id = request.form['chapter_id']
        quiz.date_of_quiz = datetime.strptime(request.form['date_of_quiz'], "%Y-%m-%d").date()
        quiz.time_duration = request.form['time_duration']

        db.session.commit()
        flash('Quiz updated successfully')
        return redirect("/quiz")

    return render_template('editors/edit_quiz.html', quiz=quiz, chapters=all_chapters)

@app.route('/delete_quiz/<int:quiz_id>', methods=['POST'])
def delete_quiz(quiz_id):
    if session['user_role'] != 'admin':
        flash("You are not authorized to delete this quiz.", "warning")
        return redirect(url_for('user_dashboard'))
    quiz = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
    flash('Quiz deleted successfully')
    return redirect("/quiz")

@app.route('/delete_subject/<int:subject_id>', methods=['POST'])
def delete_subject(subject_id):
    if session['user_role'] != 'admin':
        flash("You are not authorized to delete this subject.", "warning")
        return redirect(url_for('user_dashboard'))
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted successfully')
    return redirect("/admin_dashboard")

@app.route('/add_question/<int:quiz_id>', methods=['GET', 'POST'])
def add_question(quiz_id):
    if session['user_role'] != 'admin':
        flash("You are not authorized to access this page.", "warning")
        return redirect(url_for('user_dashboard'))
    quiz = Quiz.query.get_or_404(quiz_id)  # Fetch the quiz to pass it to the template
    chapters = Chapter.query.all()

    if request.method == 'POST':
        question_statement = request.form.get('question_statement')
        option1 = request.form.get('option_1')
        option2 = request.form.get('option_2')
        option3 = request.form.get('option_3')
        option4 = request.form.get('option_4')
        correct_option = request.form.get('correct_option')

        if not question_statement or not option1 or not option2 or not option3 or not option4 or not correct_option:
            flash('All fields are required!', 'error')
            return redirect(url_for('add_question', quiz_id=quiz_id))

        # Create new question
        question = Question(
            quiz_id=quiz_id,
            question_statement=question_statement,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            correct_option=int(correct_option)
        )
        db.session.add(question)
        db.session.commit()

        flash('Question added successfully!', 'success')
        return redirect(url_for('quiz_details', quiz_id=quiz_id))

    return render_template('add_question.html', quiz=quiz, chapters=chapters)  # Pass quiz object

@app.route('/delete_question/<int:question_id>', methods=['POST'])
def delete_question(question_id):
    if session['user_role'] != 'admin':
        flash("You are not authorized to delete this question.", "warning")
        return redirect(url_for('user_dashboard'))
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted successfully!', 'success')
    return redirect(url_for('quiz_details', quiz_id=question.quiz_id))

@app.route('/edit_question/<int:question_id>', methods=['GET', 'POST'])
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)
    
    if 'user_email' not in session:
        flash("Please log in to access the dashboard.", "warning")
        return redirect(url_for('login'))
    
    if session['user_role'] != 'admin':
        flash("You are not authorized to access this page.", "warning")
        return redirect(url_for('user_dashboard'))
    
    if request.method == 'POST':
        question.question_statement = request.form['question_statement']
        question.option1 = request.form['option1']
        question.option2 = request.form['option2']
        question.option3 = request.form['option3']
        question.option4 = request.form['option4']
        question.correct_option = request.form['correct_option']
    
        db.session.commit()
        flash('Question updated successfully!', 'success')
        return redirect(url_for('quiz_details', quiz_id=question.quiz_id))
    
    return render_template('editors/edit_question.html', question=question)

@app.route('/add_subject', methods=['GET', 'POST'])
def add_subject():
    if session['user_role'] != 'admin':
        flash("You are not authorized to access this page.", "warning")
        return redirect(url_for('user_dashboard'))
    
    if request.method == 'GET':
        return redirect("/admin_dashboard")
    
    if request.method == 'POST':
        subject_name = request.form.get('subject_name')
        description = request.form.get('description')
        
        if not subject_name or not description:
            flash('Please enter all fields')
            return redirect("/admin_dashboard")
        
        subject = Subject(name=subject_name, description=description)
        db.session.add(subject)
        db.session.commit()
        flash('Subject added successfully')
        return redirect("/admin_dashboard")

@app.route('/add_chapter', methods=['GET', 'POST'])
def add_chapter():
    if session['user_role'] != 'admin':
        flash("You are not authorized to access this page.", "warning")
        return redirect(url_for('user_dashboard'))
    
    if request.method == 'GET':
        return redirect("/admin_dashboard")
    
    if request.method == 'POST':
        chapter_name = request.form.get('chapter_name')
        description = request.form.get('description')
        subject_id = request.form.get('subject_id')
        
        if not chapter_name or not description:
            flash('Please enter all fields')
            return redirect("/admin_dashboard")
        
        chapter = Chapter(name=chapter_name, description=description, subject_id=subject_id)
        db.session.add(chapter)
        db.session.commit()
        flash('Chapter added successfully')
        return redirect("/admin_dashboard")

@app.route('/edit_subject/<int:subject_id>', methods=['GET', 'POST'])
def edit_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    
    if 'user_email' not in session:
        flash("Please log in to access the dashboard.", "warning")
        return redirect(url_for('login'))
    
    if session['user_role'] != 'admin':
        flash("You are not authorized to access this page.", "warning")
        return redirect(url_for('user_dashboard'))
    
    if request.method == 'POST':
        subject.name = request.form['subject_name']
        subject.description = request.form['description']
        db.session.commit()
        flash('Subject updated successfully')
        return redirect("/admin_dashboard")
    
    return render_template('editors/edit_subject.html', subject=subject)

@app.route('/edit_chapter/<int:chapter_id>', methods=['GET', 'POST'])
def edit_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    subjects = Subject.query.all()
    
    if 'user_email' not in session:
        flash("Please log in to access the dashboard.", "warning")
        return redirect(url_for('login'))
    
    if session['user_role'] != 'admin':
        flash("You are not authorized to access this page.", "warning")
        return redirect(url_for('user_dashboard'))
    
    if request.method == 'POST':
        chapter.subject_id = request.form['subject_id']
        chapter.name = request.form['chapter_name']
        chapter.description = request.form['description']
    
        db.session.commit()
        flash('Chapter updated successfully')
        return redirect("/admin_dashboard")
    
    return render_template('editors/edit_chapter.html', chapter=chapter, subjects=subjects)

@app.route('/delete_chapter/<int:chapter_id>', methods=['POST'])
def delete_chapter(chapter_id):
    if session['user_role'] != 'admin':
        flash("You are not authorized to delete this chapter.", "warning")
        return redirect(url_for('user_dashboard'))
    chapter = Chapter.query.get_or_404(chapter_id)
    db.session.delete(chapter)
    db.session.commit()
    flash('Chapter deleted successfully')
    return redirect("/admin_dashboard")

@app.route('/clear_attempts')
def clear_attempts():
    if session['user_role'] != 'admin':
        flash("You are not authorized to clear user attempts.", "warning")
        return redirect(url_for('user_dashboard'))
    UserAttempt.query.delete()
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/clear_scores')
def clear_scores():
    if session['user_role'] != 'admin':
        flash("You are not authorized to clear user scores.", "warning")
        return redirect(url_for('user_dashboard'))
    Score.query.delete()
    db.session.commit()
    return redirect(url_for('admin_dashboard'))