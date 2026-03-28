import re
from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy.exc import IntegrityError
from db import db
from models import Users
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint("auth", __name__, template_folder="templates")

@auth_bp.route("/register",methods = ["GET", "POST"])
def register():
    if current_user.is_authenticated:
        flash("Você já está logado!", "info")
        return redirect(url_for('index'))
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        phone = request.form.get("phone", "").strip()


        if not username or not email or not password or not phone:
            flash("Preencha nome de usuário, email, senha e número", "error")
            return redirect(url_for('auth.register'))
        
        if len(username) < 3 or len(username) > 30:   
            flash("O nome de usuário tem que ter no mínimo 3 letras e no máximo 30", "error")
            return redirect(url_for('auth.register'))
        if len(email) < 7 or len(email) > 100:
            flash("O email tem que ter no mínimo 7 letras e no máximo 100", "error")
            return redirect(url_for('auth.register'))
        if len(password) < 8:
            flash("A senha deve ter no mínimo 8 caracteres", "error")
            return redirect(url_for('auth.register'))

        email_regex = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        if not re.fullmatch(email_regex, email):
            flash("Formato de email inválido.", "error")
            return redirect(url_for("auth.register"))

        phone_digits = re.sub(r"\D", "", phone)
        if not re.fullmatch(r"^(?:55)?[1-9][0-9][9][0-9]{8}$|^(?:55)?[1-9][0-9][2-8][0-9]{7}$", phone_digits):
            flash("Telefone inválido. Informe um número brasileiro válido.", "error")
            return redirect(url_for("auth.register"))
        phone = phone_digits
        
        if Users.query.filter_by(email=email).first():
            flash("Email já cadastrado", "error")
            return redirect(url_for('auth.register'))
        
        hashed_password = generate_password_hash(password)
        new_user = Users(
            username=username, 
            email=email, 
            password=hashed_password, 
            phone_number=phone
        )
        db.session.add(new_user)
        db.session.commit()
        
        

        login_user(new_user)
        flash("Conta criada com sucesso. Bem-vindo!", "success" )
        return redirect(url_for('index'))
    else:
        return render_template("register.html")


@auth_bp.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        flash("Você já está logado!", "info")
        return redirect(url_for('index'))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        
        if not email or not password:
            flash("Por favor, insira um email e senha", "error")
            return redirect(url_for('auth.login'))
        
        email_regex = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        if not re.fullmatch(email_regex, email):
            flash("Formato de email inválido.", "error")
            return redirect(url_for("auth.login"))

        user = Users.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash("Email ou senha incorretos", "error")
            return redirect(url_for('auth.login'))

        login_user(user)
        flash("Login realizado com sucesso. Bem-vindo de volta!", "success" )
        return redirect(url_for('index'))
    else:
        return render_template("login.html")

@auth_bp.route("/profile", methods = ["POST", "GET"])
@login_required
def profile():
    if request.method == "POST":
        changed = False
        username = request.form.get("username", "").strip().lower()
        if username != "":
            if len(username) < 3 or len(username) > 30:   
                flash("O nome de usuário tem que ter no mínimo 3 letras e no máximo 30", "error")
                return redirect(url_for('auth.profile'))
            if username != current_user.username:
                current_user.username = username
                changed = True

        phone = request.form.get("phone","").strip()
        if phone != "":
            phone_digits = re.sub(r"\D", "", phone)
            if not re.fullmatch(r"\d{8,15}", phone_digits):
                flash("Telefone inválido. Use entre 8 e 15 dígitos", "error")
                return redirect(url_for("auth.profile"))
            phone = phone_digits
            if current_user.phone_number != phone:
                current_user.phone_number = phone
                changed = True

        if not changed:
            flash("Nenhuma alteração no perfil foi feita", "warning")
            return redirect(url_for('index'))
        
        try: 
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Não foi possível salvar as alterações. Tente novamente mais tarde", "error")
            return redirect(url_for('auth.profile'))
        flash("Alteração concluida com sucesso", "success")
        return redirect(url_for('index'))
    else: 
        return render_template("profile.html", user=current_user)

@auth_bp.route("/logout", methods = ["GET"])
@login_required
def logout():
    logout_user()
    flash("Você saiu da conta.", "info")
    return redirect(url_for('auth.login'))
