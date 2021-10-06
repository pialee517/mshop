from market import app, db, login_manager
from sqlalchemy.orm import sessionmaker
from flask import render_template, redirect, request, url_for, flash, session
from market.models import Product, User
from market.form import UserForm, ProductForm, LoginForm, InfoForm, SubmitForm, DeleteForm
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import create_engine
import os

login_manager.login_view = 'login_page'


def create_tables():
        engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        with engine.connect() as conn:
            with conn.begin():
                db.drop_all()
                db.create_all()

@login_manager.user_loader
def load_user(user_id):
    if session.get('user'):
        return User.query.get(int(user_id))
    else:
        return None

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index_page():
    # create_tables()
    return render_template(f'index.html')

@app.route("/static/<path:path>")
def static_dir(path):
    return send_from_directory("static", path)

@app.route('/about')
def about_page():
    return render_template(f'about.html') #Done

@app.route('/products', methods=['GET', 'POST'])
def products_page():
    product_form=ProductForm()
    submit_form=SubmitForm()
    products = Product.query.filter_by(userid=None)
    if request.method == 'POST':
        if 'Add' in request.form.get('submit'):
            try:
                uploaded_file = request.files['image']
                filename = secure_filename(uploaded_file.filename)
                uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))

                product = Product(name=product_form.name.data, price=product_form.price.data, barcode=product_form.barcode.data, image=filename, description=product_form.description.data)
                db.session.add(product)
                db.session.commit()
                flash(f'New product added successfully', category='success')
            except Exception as e:
                db.session.rollback()
                print(e)
                flash(f'Something went wrong! Please try again {str(e)}', category='danger')
        if product_form.validate_on_submit() and 'Edit' in request.form.get('submit'):
            try:
                uploaded_file = request.files['image']
                filename = secure_filename(uploaded_file.filename)
                uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))

                db.session.query(Product).filter(Product.id==request.form.get('product_id')).update({"name":product_form.name.data, "price":product_form.price.data, "barcode":product_form.barcode.data, "image":filename, "description":product_form.description.data})
                db.session.commit()
                flash(f'Product updated successfully', category='success')
            except:
                db.session.rollback()
                flash(f'Updating information of product didn\'t finish successfully Please try again later', category='danger')
        if submit_form.validate_on_submit() and 'Delete' in request.form.get('submit'):
            product_id = request.form.get('delete_product')
            product_object = db.session.query(Product).filter(Product.id==product_id).first()
            try:
                db.session.delete(product_object)
                db.session.commit()
                flash(f'Product {product_id} successfully is deleted', category='success')
            except Exception as e:
                db.session.rollback()
                flash(f'Something is wrong to delete {product_id}. Please try again later', category='danger')
        redirect(url_for('products_page'))
    return render_template(f'products.html', submit_form=submit_form, product_form=product_form, products=products)


@app.route('/market', methods=['GET', 'POST'])
def market_page():
    purchase_form = SubmitForm()
    sale_form = SubmitForm()
    if request.method == 'POST':
        if purchase_form.validate_on_submit() and 'Confirm' in request.form.get('submit'):
            product_object = Product.query.filter_by(id=request.form.get('available_product')).first()
            print(product_object)
            if product_object:
                if current_user.can_buy(product_object):
                    product_object.buy(current_user)
                    flash(f'Congratulations! You purchased {product_object.name}',category='success')
                else:
                    flash(f'Unfortunately, you don\'t have enough money to buy {product_object.name}', category='danger')
        if sale_form.validate_on_submit() and 'Sell' in request.form.get('submit'):
            user_product_object = Product.query.filter_by(id=request.form.get("owned_product")).first()
            if user_product_object:
                if current_user.can_sell(user_product_object):
                    user_product_object.sell(current_user)
                    flash(f'Congratulations! You sold {user_product_object.name}', category='success')
                else:
                    flash(f'Something went wrong to sell {user_product_object.name}', category='danger')
        return redirect(url_for('market_page'))
    if request.method == 'GET':
        products = Product.query.filter_by(userid=None)
        user_products = None
        if current_user.is_authenticated:
            user_products = Product.query.filter_by(userid=current_user.id)
        return render_template(f'market.html', purchase_form=purchase_form, sale_form=sale_form, products=products, user_products=user_products)


@app.route('/signup', methods=['GET', 'POST'])
def signup_page():
    form = UserForm()
    if form.validate_on_submit():
        new_customer = User(email=form.email.data, name=form.name.data, role='customer', password=form.password.data)
        try:
            db.session.add(new_customer)
            db.session.commit()
            flash(f'{new_customer.name}, thank you for joining us', category='success')
            return redirect(url_for("index_page"))
        except Exception as e:
            flash("Try again!\n" + str(e), category='danger')
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(err_msg, category='danger')
    return render_template(f'signup.html', form=form)

@app.route('/customers', methods=['GET', 'POST'])
def customers_page():
    info_form = InfoForm()
    customer_selected = request.form.get('select_customer')
    products = Product.query.filter_by(userid=id)
    customers = User.query.filter_by(role='customer')
    if request.method == 'POST':
        customer_id = request.form.get('select_customer')
        customer_selected = User.query.filter_by(id=customer_id).first()
        if info_form.validate_on_submit() and "Edit" in request.form.get("submit"):
            budget = request.form.get("budget")
            budget = float(budget.replace(',', ''))
            if budget >= 0:
                customer_id_selected = request.form.get("customer_for_edit")
                customer_selected = User.query.filter_by(id=customer_id_selected).first()
                if customer_selected:
                    try:
                        customer_selected.name = info_form.name.data
                        customer_selected.budget = budget
                        db.session.commit()
                        flash("Updated", category="success")
                    except Exception as e:
                        db.session.rollback()
                        flash(f"Failed to update", category='danger')
    return render_template(f'customers.html', info_form=info_form, customers=customers, products=products, customer_selected=customer_selected)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(email=form.email.data).first()
        if attempted_user and attempted_user.check_password(attempted_password=form.password.data):
            login_user(attempted_user)
            session['user'] = attempted_user.name
            flash(f'Hi {attempted_user.name}, welcome back', category='success')
            return redirect(url_for('index_page'))
        else:
            flash('Email and password are not match', category='danger')
    return render_template(f'login.html', form=form)

@app.route('/info', methods=['GET', 'POST'])
@login_required
def info_page():
    info_form = InfoForm()
    delete_form = DeleteForm()
    user_products = Product.query.filter_by(userid=current_user.id)
    if request.method == 'POST':
        if info_form.validate_on_submit() and 'Edit' in request.form.get('submit'):
            new_password = request.form.get('new_password')
            new_name = info_form.name.data
            found_user = User.query.filter_by(id=current_user.id).first()
            if len(new_password) == 0:
                try:
                    db.session.query(User).filter(User.id==current_user.id).update({"name":new_name})
                    db.session.commit()
                    flash("Information has updated successfully", category='success')
                except:
                    db.session.rollback()
                    flash("Fail to update information. Please try again", category='danger')
            elif len(new_password) >= 5 :
                try:
                    found_user.password = new_password
                    found_user.name = new_name
                    db.session.commit()
                    flash("Information has updated successfully", category='success')
                except:
                    db.session.rollback()
                    flash("Fail to update password", category='danger')
        if delete_form.validate_on_submit() and 'Delete Account' in request.form.get('submit'):
            user = User.query.filter_by(id=current_user.id).first()
            if user and user.email == delete_form.email.data and user.check_password(attempted_password=request.form.get('password')):
                try:
                    for user_product in user_products:
                        db.session.delete(user_product)
                    db.session.delete(user)
                    db.session.commit()
                    flash("Bye Hopefuly see you again!", category='success')
                    return redirect(url_for("index_page"))
                except Exception as e:
                    db.session.rollback()
                    flash(f"Sorry it did not complete a whole process. Please try again later! {e}", category='danger')
            else:
                flash("Information does not match", category="danger")
    return render_template(f'info.html', info_form=info_form, delete_form=delete_form, user_products=user_products)

@app.route('/references')
def references_page():
    return render_template(f"references.html")

@app.route('/logout')
def logout():
    session.pop('user')
    logout_user()
    return redirect(url_for('index_page'))
