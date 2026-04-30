import os
import uuid
from PIL import Image
from flask import Blueprint, request, render_template, redirect, url_for, flash
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from utils.pagination import paginate_query
from db import db
from models import Products, Categories
from decimal import Decimal, InvalidOperation

admin_products_bp = Blueprint("admin_products", __name__, template_folder="templates")

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.webp'}
def allowed_file(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS

@admin_products_bp.route("/", methods = ["GET"])
def products():
    page = request.args.get("page", 1, type=int)
    per_page = 5

    base_query = products = (
        Products.query
        .options(selectinload(Products.category))
        .order_by(Products.is_active.desc(), Products.id.asc())
    )

    min_price_str = request.args.get("min-price", "").strip()
    max_price_str = request.args.get("max-price", "").strip()

    min_price_val = None
    max_price_val = None

    if min_price_str != "":
        try:
            min_price_val =  Decimal(min_price_str)
        except InvalidOperation:
            flash("Preço mínimo inválido", "error")
            return redirect(url_for('admin_panel.admin_products.products'))
        if min_price_val < 0:
            flash("Preço mínimo inválido", "error")
            return redirect(url_for('admin_panel.admin_products.products'))
    
    if max_price_str != "":
        try:
            max_price_val = Decimal(max_price_str)
        except InvalidOperation:
            flash("Preço máximo inválido", "error")
            return redirect(url_for('admin_panel.admin_products.products'))
        if max_price_val < 0:
            flash("Preço máximo inválido", "error")
            return redirect(url_for('admin_panel.admin_products.products'))

    if min_price_val != None and max_price_val != None:
        if min_price_val > max_price_val:
            flash("O mínimo não pode ser maior que o máximo", "error")
            return redirect(url_for('admin_panel.admin_products.products'))

    if min_price_val != None:
        base_query = base_query.filter(Products.price >= min_price_val)
    if max_price_val != None:
        base_query = base_query.filter(Products.price <= max_price_val)


    product_name = request.args.get("product-name", "").strip().lower()
    if product_name != "":
        base_query = base_query.filter(
            Products.name.ilike(f"%{product_name}%")
        )


    category_name = request.args.get("category-name", "").strip().lower()
    if category_name != "":
        base_query = base_query.filter(
            Products.category.has(
                Categories.name.ilike(f"%{category_name}%")
            )
        )

    products, total, total_pages, page = paginate_query(base_query, page, per_page)
    
    categories = Categories.query.all()

    return render_template(
        "admin_products.html", 
        products=products,
        page=page,
        total_pages=total_pages,
        categories = categories,
        min_price_val=min_price_val,
        max_price_val = max_price_val,
        product_name=product_name,
        category_name=category_name,
        current_category_name=category_name
    )

@admin_products_bp.route("/create", methods = ["POST", "GET"])
def create_product():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if name == "":
            flash("Nome do produto não foi fornecido.", "error")
            return redirect(url_for('.create_product'))
        if len(name) > 30:
            flash("Nome grande demais. Limite de 30 caracteres.", "error")
            return redirect(url_for('.create_product'))

        price = request.form.get("price", "").strip()
        if price == "":
            flash("O preço do produto não foi fornecido.", "error")
            return redirect(url_for('.create_product'))
        try:
            price = Decimal(price)
        except InvalidOperation:
            flash("O preço do produto deve ser um número.", "error")
            return redirect(url_for('.create_product'))
        if price < 0:
            flash("O preço não pode ser um número negativo.","error")
            return redirect(url_for('.create_product'))

        description = request.form.get("description", "").strip()

        category_id = request.form.get("category-id", "")
        if category_id == "" or category_id == "0":
            flash("A categoria do produto não foi fornecida", "error")
            return redirect(url_for('.create_product'))
        try: 
            category_id = int(category_id)
        except ValueError:
            flash("O id da categoria do produto deve ser um número", "error")
            return redirect(url_for('.create_product'))
        if category_id < 1:
            flash("O id da categoria do produto deve ser maior que 0", "error")
            return redirect(url_for('.create_product'))
        if not Categories.query.filter_by(id=category_id).first():
            flash("A categoria inserida não existe", "error")
            return redirect(url_for('.create_product'))

        stock = request.form.get("stock","")
        if stock == "":
            flash("O estoque do produto não foi fornecido", "error")
            return redirect(url_for('.create_product'))
        try: 
            stock = int(stock)
        except ValueError:
            flash("O estoque deve ser um número", "error")
            return redirect(url_for('.create_product'))
        if stock < 0:
            flash("O estoque não pode ser um número negativo", "error")
            return redirect(url_for('.create_product'))

        is_active = "is-active" in request.form

        image = request.files.get("image")
        image_path = None
        upload_folder = os.path.join(os.path.dirname(__file__), '..', '..', 'static', 'uploads')
        upload_folder = os.path.abspath(upload_folder)
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        if image and image.filename != "":
            if not allowed_file(image.filename):
                flash("Apenas arquivos JPG, WEBP ou JPEG são permitidos.", "error")
                return redirect(url_for('.create_product'))
            
            #verifica tamanho do arquivo
            image.seek(0, os.SEEK_END)
            size = image.tell()
            image.seek(0)
            if size > 2 * 1024 * 1024: #2MB
                flash("A imagem deve ter no máximo 2MB.", "error")
                return redirect(url_for('.create_product'))

            img = Image.open(image)
            width, height = img.size
            if width > 800 or height > 800:
                flash("A imagem deve ter no máximo 800x800 pixels.", "error")
                return redirect(url_for('.create_product'))

            ext = os.path.splitext(image.filename)[1]
            unique_filename = f"{uuid.uuid4().hex}{ext}"
            image_path = f"static/uploads/{unique_filename}"
            image.seek(0)
            image.save(os.path.join(upload_folder, unique_filename))

        new_product = Products(
                name=name, 
                price=price, 
                description=description, 
                category_id=category_id, 
                stock=stock, 
                is_active=is_active, 
                image=image_path
            )
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for('.products'))
    else:
        categories = Categories.query.all()
        return render_template("create.html", categories=categories)
    

@admin_products_bp.route("/delete", methods = ["POST"])
def delete_product():
    product_id = request.form.get("id","").strip()
    if product_id == "":
        flash("Por favor, forneça o id do produto", "error")
        return redirect(url_for('.products'))
    try: 
        product_id = int(product_id)
    except ValueError:
        flash("O id do produto deve ser um número", "error")
        return redirect(url_for('.products'))
    if product_id < 1:
        flash("O id do produto não pode ser menor que 1", "error")
        return redirect(url_for('.products'))
    
    product = Products.query.filter_by(id=product_id).first()
    if not product:
        flash("O produto que você está tentando deletar não existe", "error")
        return redirect(url_for('.products'))
    
    if product.image:
        image_path = os.path.join(os.path.dirname(__file__),'..', '..', '..', product.image)
        image_path = os.path.abspath(image_path)
        if os.path.exists(image_path):
            os.remove(image_path)

    db.session.delete(product)
    try:
        db.session.commit()
    except IntegrityError: 
        db.session.rollback()
        flash("Não é possível excluir esse produto pois ele já está no carrinho ou no registro de pedidos de alguém", "error")
        return redirect(url_for('.products'))
    return redirect(url_for('.products'))


@admin_products_bp.route("/edit", methods=["POST", "GET"])
def edit_product():
    if request.method == "POST":
        product_id = request.form.get("product-id", "")
        if product_id == "":
            flash("Nenhum id do produto que quer editar foi fornecido", "error")
            return redirect(url_for('.products'))
        try:
            product_id = int(product_id)
        except ValueError:
            flash("O id do produto tem que ser um número", "error")
            return redirect(url_for('.products'))
        if product_id < 1:
            flash("O id do produto que quer editar deve ser maior que 0", "error")
            return redirect(url_for('.products'))
        
        product = Products.query.filter_by(id=product_id).first()
        if not product:
            flash("O produto que você quer editar não existe", "error")
            return redirect(url_for('.products'))
        
        changed = False

        name = request.form.get("name", "").strip()
        if name != "":
            if len(name) > 30:
                flash("Nome grande demais. Limite de 30 caracteres.", "error")
                return redirect(url_for('.edit_product', id=product_id))
            if product.name != name:
                product.name = name
                changed = True

        price = request.form.get("price", "").strip()
        if not price == "":
            try:
                price = Decimal(price)
            except InvalidOperation:
                flash("O preço do produto deve ser um número.", "error")
                return redirect(url_for('.edit_product', id=product_id))
            if price < 0:
                flash("O preço não pode ser um número negativo.","error")
                return redirect(url_for('.edit_product', id=product_id))
            if product.price != price:
                product.price = price
                changed = True


        description = request.form.get("description", "").strip()
        current_description = product.description or ""
        if current_description != description:
            product.description = description
            changed = True
            

        category_id = request.form.get("category-id", "")
        if not category_id == "" and not category_id == "0": 
            try: 
                category_id = int(category_id)
            except ValueError:
                flash("O id da categoria do produto deve ser um número", "error")
                return redirect(url_for('.edit_product', id=product_id))
            if category_id < 1:
                flash("O id da categoria do produto deve ser maior que 0", "error")
                return redirect(url_for('.edit_product', id=product_id))
            if not Categories.query.filter_by(id=category_id).first():
                flash("A categoria inserida não existe", "error")
                return redirect(url_for('.edit_product', id=product_id))
            if product.category_id != category_id:
                product.category_id = category_id
                changed = True

        stock = request.form.get("stock","")
        if not stock == "":
            try: 
                stock = int(stock)
            except ValueError:
                flash("O estoque deve ser um número", "error")
                return redirect(url_for('.edit_product', id=product_id))
            if stock < 0:
                flash("O estoque não pode ser um número negativo", "error")
                return redirect(url_for('.edit_product', id=product_id))
            if product.stock != stock:
                product.stock = stock
                changed = True

        is_active = "is-active" in request.form
        if product.is_active != is_active:
            product.is_active = is_active
            changed = True

        image = request.files.get("image")
        if image and image.filename != "":
            if not allowed_file(image.filename):
                flash("Apenas arquivos JPG, JPEG ou WEBP são permitidos.","error")
                return redirect(url_for('.edit_product', id=product_id))
        
        # Exclui imagem antiga
            if product.image:
                old_image_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', product.image)
                old_image_path = os.path.abspath(old_image_path)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)

            # Salva nova imagem
            image.seek(0, os.SEEK_END)
            size = image.tell()
            image.seek(0)
            if size > 2 * 1024 * 1024:
                flash("A imagem deve ter no máximo 2MB.", "error")
                return redirect(url_for('.edit_product', id=product_id))
            
            img = Image.open(image)
            width, height = img.size
            if width > 800 or height > 800:
                flash("A imagem deve ter no máximo 800x800 pixels.", "error")
                return redirect(url_for('.edit_product', id=product_id))
            
            ext = os.path.splitext(image.filename)[1]
            unique_filename = f"{uuid.uuid4().hex}{ext}"
            upload_folder = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'static', 'uploads')
            upload_folder = os.path.abspath(upload_folder)
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            image_path = f"static/uploads/{unique_filename}"
            image.seek(0)
            image.save(os.path.join(upload_folder, unique_filename))
            product.image = image_path
            changed = True

        if not changed:
            flash("Nenhuma alteração foi feita", "info")
            return redirect(url_for('.edit_product', id=product_id))

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Não foi possível editar esse produto. Tente novamente mais tarde.", "error")
            return redirect(url_for('.edit_product', id=product_id))
        
        flash("Edição concluída com sucesso", "success")
        return redirect(url_for('.products'))
    elif request.method == "GET":
        product_id = request.args.get("id", "")
        if product_id == "":
            flash("Nenhum id do produto que quer editar foi fornecido", "error")
            return redirect(url_for('.products'))
        try:
            product_id = int(product_id)
        except ValueError:
            flash("O id do produto tem que ser um número", "error")
            return redirect(url_for('.products'))
        if product_id < 1:
            flash("O id do produto que quer editar deve ser maior que 0", "error")
            return redirect(url_for('.products'))
        
        product = Products.query.filter_by(id=product_id).first()
        if not product:
            flash("O produto que você quer editar não existe", "error")
            return redirect(url_for('.products'))
        categories = Categories.query.all()
        return render_template("edit.html", product=product, categories=categories)

