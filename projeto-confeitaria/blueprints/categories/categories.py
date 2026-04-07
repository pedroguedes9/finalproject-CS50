from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required
from sqlalchemy.exc import IntegrityError
from db import db
from models import Products, Categories

categories_bp = Blueprint("categories", __name__, template_folder="templates")

@categories_bp.route("/categories", methods=["GET"])
@login_required
def categories():
    categories = Categories.query.all()
    return render_template("categories.html", categories=categories)

@categories_bp.route("/add", methods = ["POST"])
@login_required
def add_category():
    name = request.form.get("name", "").strip().lower()
    if name == "":
        flash("Insira um nome para categoria", "error")
        return redirect(url_for('categories.categories'))
    if len(name) > 30: 
        flash("O nome da categoria só pode conter até 30 caracteres", "error")
        return redirect(url_for('categories.categories'))
    if Categories.query.filter_by(name=name).first():
        flash("Já existe uma categoria com esse nome, por favor, insira outro", "error")
        return redirect(url_for('categories.categories'))
    
    new_category = Categories(name=name)
    db.session.add(new_category)
    try:
        db.session.commit()
    except IntegrityError:
        flash("Não foi possível realizar a criação da categoria. Tente novamente mais tarde", "error")
        db.session.rollback()
        return redirect(url_for('categories.categories'))
    return redirect(url_for('categories.categories'))


@categories_bp.route("/edit", methods=["POST"])
@login_required
def edit_category():
    category_id = request.form.get("id","")
    if category_id == "":
        flash("O id da categoria que deseja editar não foi fornecido", "error")
        return redirect(url_for('categories.categories'))
    try:
        category_id = int(category_id)
    except ValueError:
        flash("O id da categoria tem que ser um número", "error")
        return redirect(url_for('categories.categories'))
    if category_id < 1:
        flash("O id da categoria não pode ser menor que 1", "error")
        return redirect(url_for('categories.categories'))
    category = Categories.query.filter_by(id=category_id).first()
    if not category:
        flash("O id da categoria fornecido não existe", "error")
        return redirect(url_for('categories.categories'))

    new_name = request.form.get("new-name","").strip().lower()
    if new_name == "":
        flash("O novo nome da categoria não foi fornecido", "error")
        return redirect(url_for('categories.categories'))
    if len(new_name) > 30:
        flash("O novo nome não pode ter mais de 30 caracteres", "error")
        return redirect(url_for('categories.categories'))
    if Categories.query.filter_by(name=new_name).first():
        flash("Já existe uma categoria com esse nome que você tentou trocar. Por favor, insira outro.", "error")
        return redirect(url_for('categories.categories'))
    
    category.name = new_name
    try:
        db.session.commit()
    except IntegrityError:
        flash("Ocorreu algum erro, sua alteração não foi confirmada. Tente novamente mais tarde", "error")
        db.session.rollback()
        return redirect(url_for('categories.categories'))
    return redirect(url_for('categories.categories'))

@categories_bp.route("/delete", methods=["POST"])
@login_required
def delete_category():
    category_id = request.form.get("category-id","")
    if category_id == "":
        flash("Por favor, forneça o id da categoria.", "error")
        return redirect(url_for('categories.categories'))
    try:
        category_id = int(category_id)
    except:
        flash("O id da categoria deve ser um número", "error")
        return redirect(url_for('categories.categories'))
    if category_id < 1:
        flash("O id da categoria não pode ser menor que 1")
        return redirect(url_for('categories.categories'))
    
    category = Categories.query.filter_by(id=category_id).first()
    if not category:
        flash("A categoria que você está tentando deletar não existe", "error")
        return redirect(url_for('categories.categories'))
    
    if category.name == "sem categoria":
        flash("A categoria que você está tentando excluir não pode ser excluída", "error")
        return redirect(url_for('categories.categories'))

    without_category = Categories.query.filter_by(name="sem categoria").first()
    if not without_category:
        without_category = Categories(name="sem categoria")
        db.session.add(without_category)
        db.session.flush()

    if Products.query.filter_by(category_id=category_id).count() > 0:
        flash('Já existem produtos com essa categoria, então eles agora estão "Sem categoria"', "info")

    # Update em massa: move TODOS os produtos da categoria atual para "sem categoria"
    Products.query.filter_by(category_id=category_id).update(
        {"category_id": without_category.id},
        synchronize_session=False
    )

    db.session.delete(category)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("Não é possível excluir essa categoria pois ela já está em algum produto", "error")
        return redirect(url_for('categories.categories'))
    
    return redirect(url_for('categories.categories'))