from . import app,db
from flask import request,render_template,redirect,url_for,flash
from werkzeug.security import check_password_hash,generate_password_hash
from flask_login import login_user,logout_user,current_user,login_required
from datetime import datetime
from .models import User,Service

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login',methods=['GET', 'POST'])
def login():
    username=request.form.get('username')
    password=request.form.get('password')
    
    user_exists=User.query.filter_by(username=username).first()

    if user_exists and check_password_hash(user_exists.password_hash,password):
        login_user(user_exists)
        return redirect(url_for('user_dashboard'))

    return render_template('login.html')

@app.route('/register',methods=['GET', 'POST'])
def create_admin():
    if request.method == 'POST':
        username=request.form.get('username')
        email=request.form.get('email')
        password=request.form.get('password')

        user_exists=User.query.filter_by(username=username).first()

        if user_exists:
            flash("This user account is unsuccessfull")
            return redirect(url_for('create_admin'))

        new_user=User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )

        db.session.add(new_user)
        db.session.commit()
        flash("Account created Successfully")
        return redirect(url_for('create_admin'))
    return render_template('sign.html')

@login_required
@app.route('/dashboard')
def user_dashboard():
    return render_template('dashboard.html')
    
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@login_required
@app.route('/addrecord',methods=['GET', 'POST'])
def add_parking_record():
    date=datetime.utcnow()
    if request.method =='POST':
        vehicle_name=request.form.get('vehicle_name')
        num_plate=request.form.get('num_plate')
        owner=request.form.get('owner')
        contact=request.form.get('contact')
        date_parked=request.form.get('date_parked')
        payment=request.form.get('payment')

        new_record=Service(
            vehicle_name=vehicle_name,
            num_plate=num_plate,
            owner=owner,
            contact=contact,
            date_parked=date_parked,
            payment=False,
            parking=current_user
        )

        db.session.add(new_record)
        db.session.commit()
        flash("New Record has been added")
        return redirect(url_for('add_parking_record'))

    return render_template('addrecord.html',date=date)

@login_required
@app.route('/manage')
def manage_records():
    records=Service.query.order_by(Service.id.desc()).all()
    return render_template('manage.html',records=records)

@login_required
@app.route('/manage/<int:record_id>',methods=['GET', 'POST'])
def manage_record(record_id):
    rec=Service.query.get_or_404(record_id)

    if request.method == 'POST':
        rec.vehicle_name=request.form.get('vehicle_name')
        rec.num_plate=request.form.get('num_plate')
        rec.owner=request.form.get('owner')
        rec.contact=request.form.get('contact')
        rec.date_parked=request.form.get('date_parked')
        db.session.commit()
        return redirect(url_for('manage_records')) 
    return render_template('info.html',rec=rec)

@login_required
@app.route('/pay/<int:id>',methods=['POST'])
def set_payment(id):
    rec=Service.query.get_or_404(id)
    rec.payment=True
    db.session.commit()
    return render_template('info.html',rec=rec)

