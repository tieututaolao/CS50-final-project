from flask import render_template, url_for, flash, redirect, request
from project import app, db, bcrypt
from project.forms import RegistrationForm, LoginForm
from project.models import User
from flask_login import login_user, current_user, logout_user, login_required
import numpy as np
import copy

grid = [
    [0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0]
]
result = []

def possible(y, x, n):
    global grid
    # check in row
    for i in range(9):
        if grid[y][i] == n: return False
    
    # check in column
    for i in range(9):
        if grid[i][x] == n: return False

    # check in mini square 3x3
    x0 = (x // 3) * 3
    y0 = (y // 3) * 3
    for i in range(3):
        for j in range(3):
            if grid[y0 + i][x0 + j] == n: return False

    return True

def fillSudoku():
    global grid
    continueFill = 1
    while continueFill == 1:
        changeGrid = 0
        for y in range(9):
            for x in range(9):
                if grid[y][x] == 0:
                    possibleList = []
                    for n in range(1, 10):
                        if possible(y, x, n):
                            possibleList.append(n)
                    if len(possibleList) == 1:
                        grid[y][x] = possibleList[0]
                        changeGrid = 1
        
        if changeGrid == 1:
            continueFill = 1
        else:
            break
                

def finalSolve():
    global result, grid
    for y in range(9):
        for x in range(9):
            if grid[y][x] == 0:
                for n in range(1, 10):
                    if possible(y, x, n):
                        grid[y][x] = n
                        finalSolve()
                        grid[y][x] = 0
                return
    
    if np.matrix(grid).sum() == 405 :
        result = copy.deepcopy(grid)

@app.route("/", methods=["GET", "POST"])
def home():
    global result, grid
    # input add to grid
    if request.method == "POST":
        for i in range(9):
            for j in range(9):
                number = request.form.get(f"cell-{i}{j}")
                if number:
                    grid[i][j] = int(number)
                else: grid[i][j] = 0

        # sovle sudoku
        
        fillSudoku()
        x = np.matrix(grid)
        if x.sum() != 405:
            finalSolve()
        else:
            result = grid

        return render_template("output.html", result=result)

    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html", title="Hello")

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created! You are now able to log in', 'success')
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash("Login Unsuccessful. Please check username and password", "danger")
    return render_template("login.html", title="Login", form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/account")
@login_required
def account():
    return render_template("account.html", title="Account")


