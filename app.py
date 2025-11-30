from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, date

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ehospital_secret_key_2025'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ehospital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    un = db.Column(db.String(80), unique=True, nullable=False)
    pw = db.Column(db.String(200), nullable=False)
    rl = db.Column(db.String(20), nullable=False)  # admin, doctor, patient
    nm = db.Column(db.String(100), nullable=False)
    em = db.Column(db.String(120), unique=True, nullable=False)
    ph = db.Column(db.String(15))

class Doc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sp = db.Column(db.String(100), nullable=False)  # specialization
    exp = db.Column(db.Integer)  # experience in years
    fee = db.Column(db.Float)
    av = db.Column(db.String(200))  # availability
    user = db.relationship('User', backref=db.backref('doc', uselist=False))

class Pat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    dob = db.Column(db.Date)
    gen = db.Column(db.String(10))  # gender
    bg = db.Column(db.String(5))  # blood group
    addr = db.Column(db.Text)
    user = db.relationship('User', backref=db.backref('pat', uselist=False))

class Apt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.Integer, db.ForeignKey('pat.id'), nullable=False)
    did = db.Column(db.Integer, db.ForeignKey('doc.id'), nullable=False)
    dt = db.Column(db.Date, nullable=False)
    tm = db.Column(db.String(20), nullable=False)
    st = db.Column(db.String(20), default='pending')  # status: pending, approved, completed, cancelled
    nt = db.Column(db.Text)  # notes
    pat = db.relationship('Pat', backref='apts')
    doc = db.relationship('Doc', backref='apts')

class Rec(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.Integer, db.ForeignKey('pat.id'), nullable=False)
    did = db.Column(db.Integer, db.ForeignKey('doc.id'), nullable=False)
    dt = db.Column(db.Date, default=date.today)
    dg = db.Column(db.Text)  # diagnosis
    pr = db.Column(db.Text)  # prescription
    nt = db.Column(db.Text)  # notes
    pat = db.relationship('Pat', backref='recs')
    doc = db.relationship('Doc', backref='recs')

# Decorators
def login_req(f):
    @wraps(f)
    def dec(*args, **kwargs):
        if 'uid' not in session:
            flash('Please login first', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return dec

def admin_req(f):
    @wraps(f)
    def dec(*args, **kwargs):
        if 'uid' not in session or session.get('rl') != 'admin':
            flash('Admin access required', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return dec

def doc_req(f):
    @wraps(f)
    def dec(*args, **kwargs):
        if 'uid' not in session or session.get('rl') != 'doctor':
            flash('Doctor access required', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return dec

def pat_req(f):
    @wraps(f)
    def dec(*args, **kwargs):
        if 'uid' not in session or session.get('rl') != 'patient':
            flash('Patient access required', 'error')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return dec

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        un = request.form.get('un')
        pw = request.form.get('pw')
        u = User.query.filter_by(un=un).first()
        if u and check_password_hash(u.pw, pw):
            session['uid'] = u.id
            session['un'] = u.un
            session['rl'] = u.rl
            session['nm'] = u.nm
            flash('Login successful', 'success')
            if u.rl == 'admin':
                return redirect(url_for('admin_dash'))
            elif u.rl == 'doctor':
                return redirect(url_for('doc_dash'))
            else:
                return redirect(url_for('pat_dash'))
        flash('Invalid credentials', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        un = request.form.get('un')
        pw = request.form.get('pw')
        nm = request.form.get('nm')
        em = request.form.get('em')
        ph = request.form.get('ph')
        rl = request.form.get('rl', 'patient')
        
        if User.query.filter_by(un=un).first():
            flash('Username already exists', 'error')
            return redirect(url_for('register'))
        if User.query.filter_by(em=em).first():
            flash('Email already exists', 'error')
            return redirect(url_for('register'))
        
        u = User(un=un, pw=generate_password_hash(pw), nm=nm, em=em, ph=ph, rl=rl)
        db.session.add(u)
        db.session.commit()
        
        if rl == 'patient':
            dob = request.form.get('dob')
            gen = request.form.get('gen')
            bg = request.form.get('bg')
            addr = request.form.get('addr')
            p = Pat(uid=u.id, dob=datetime.strptime(dob, '%Y-%m-%d').date() if dob else None, gen=gen, bg=bg, addr=addr)
            db.session.add(p)
            db.session.commit()
        
        flash('Registration successful. Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('home'))

# Admin Routes
@app.route('/admin')
@admin_req
def admin_dash():
    docs = Doc.query.all()
    pats = Pat.query.all()
    apts = Apt.query.all()
    return render_template('admin/dash.html', docs=docs, pats=pats, apts=apts)

@app.route('/admin/docs')
@admin_req
def admin_docs():
    docs = Doc.query.all()
    return render_template('admin/docs.html', docs=docs)

@app.route('/admin/doc/add', methods=['GET', 'POST'])
@admin_req
def admin_doc_add():
    if request.method == 'POST':
        un = request.form.get('un')
        pw = request.form.get('pw')
        nm = request.form.get('nm')
        em = request.form.get('em')
        ph = request.form.get('ph')
        sp = request.form.get('sp')
        exp = request.form.get('exp')
        fee = request.form.get('fee')
        av = request.form.get('av')
        
        if User.query.filter_by(un=un).first():
            flash('Username already exists', 'error')
            return redirect(url_for('admin_doc_add'))
        
        u = User(un=un, pw=generate_password_hash(pw), nm=nm, em=em, ph=ph, rl='doctor')
        db.session.add(u)
        db.session.commit()
        
        d = Doc(uid=u.id, sp=sp, exp=int(exp) if exp else 0, fee=float(fee) if fee else 0, av=av)
        db.session.add(d)
        db.session.commit()
        
        flash('Doctor added successfully', 'success')
        return redirect(url_for('admin_docs'))
    return render_template('admin/doc_form.html', doc=None)

@app.route('/admin/doc/edit/<int:id>', methods=['GET', 'POST'])
@admin_req
def admin_doc_edit(id):
    d = Doc.query.get_or_404(id)
    if request.method == 'POST':
        d.user.nm = request.form.get('nm')
        d.user.em = request.form.get('em')
        d.user.ph = request.form.get('ph')
        d.sp = request.form.get('sp')
        d.exp = int(request.form.get('exp')) if request.form.get('exp') else 0
        d.fee = float(request.form.get('fee')) if request.form.get('fee') else 0
        d.av = request.form.get('av')
        db.session.commit()
        flash('Doctor updated successfully', 'success')
        return redirect(url_for('admin_docs'))
    return render_template('admin/doc_form.html', doc=d)

@app.route('/admin/doc/delete/<int:id>')
@admin_req
def admin_doc_delete(id):
    d = Doc.query.get_or_404(id)
    u = d.user
    db.session.delete(d)
    db.session.delete(u)
    db.session.commit()
    flash('Doctor deleted successfully', 'success')
    return redirect(url_for('admin_docs'))

@app.route('/admin/pats')
@admin_req
def admin_pats():
    pats = Pat.query.all()
    return render_template('admin/pats.html', pats=pats)

@app.route('/admin/pat/view/<int:id>')
@admin_req
def admin_pat_view(id):
    p = Pat.query.get_or_404(id)
    return render_template('admin/pat_view.html', pat=p)

@app.route('/admin/apts')
@admin_req
def admin_apts():
    apts = Apt.query.all()
    return render_template('admin/apts.html', apts=apts)

# Doctor Routes
@app.route('/doctor')
@doc_req
def doc_dash():
    d = Doc.query.filter_by(uid=session['uid']).first()
    apts = Apt.query.filter_by(did=d.id).all() if d else []
    return render_template('doctor/dash.html', doc=d, apts=apts)

@app.route('/doctor/apts')
@doc_req
def doc_apts():
    d = Doc.query.filter_by(uid=session['uid']).first()
    apts = Apt.query.filter_by(did=d.id).all() if d else []
    return render_template('doctor/apts.html', apts=apts)

@app.route('/doctor/apt/<int:id>/approve')
@doc_req
def doc_apt_approve(id):
    a = Apt.query.get_or_404(id)
    a.st = 'approved'
    db.session.commit()
    flash('Appointment approved', 'success')
    return redirect(url_for('doc_apts'))

@app.route('/doctor/apt/<int:id>/complete')
@doc_req
def doc_apt_complete(id):
    a = Apt.query.get_or_404(id)
    a.st = 'completed'
    db.session.commit()
    flash('Appointment completed', 'success')
    return redirect(url_for('doc_apts'))

@app.route('/doctor/apt/<int:id>/cancel')
@doc_req
def doc_apt_cancel(id):
    a = Apt.query.get_or_404(id)
    a.st = 'cancelled'
    db.session.commit()
    flash('Appointment cancelled', 'success')
    return redirect(url_for('doc_apts'))

@app.route('/doctor/recs')
@doc_req
def doc_recs():
    d = Doc.query.filter_by(uid=session['uid']).first()
    recs = Rec.query.filter_by(did=d.id).all() if d else []
    return render_template('doctor/recs.html', recs=recs)

@app.route('/doctor/rec/add/<int:pid>', methods=['GET', 'POST'])
@doc_req
def doc_rec_add(pid):
    p = Pat.query.get_or_404(pid)
    d = Doc.query.filter_by(uid=session['uid']).first()
    if request.method == 'POST':
        dg = request.form.get('dg')
        pr = request.form.get('pr')
        nt = request.form.get('nt')
        r = Rec(pid=pid, did=d.id, dg=dg, pr=pr, nt=nt)
        db.session.add(r)
        db.session.commit()
        flash('Medical record added', 'success')
        return redirect(url_for('doc_recs'))
    return render_template('doctor/rec_form.html', pat=p, rec=None)

@app.route('/doctor/pats')
@doc_req
def doc_pats():
    d = Doc.query.filter_by(uid=session['uid']).first()
    apts = Apt.query.filter_by(did=d.id).all() if d else []
    pids = list(set([a.pid for a in apts]))
    pats = Pat.query.filter(Pat.id.in_(pids)).all() if pids else []
    return render_template('doctor/pats.html', pats=pats)

@app.route('/doctor/profile', methods=['GET', 'POST'])
@doc_req
def doc_profile():
    d = Doc.query.filter_by(uid=session['uid']).first()
    if request.method == 'POST':
        d.user.nm = request.form.get('nm')
        d.user.ph = request.form.get('ph')
        d.sp = request.form.get('sp')
        d.exp = int(request.form.get('exp')) if request.form.get('exp') else 0
        d.fee = float(request.form.get('fee')) if request.form.get('fee') else 0
        d.av = request.form.get('av')
        db.session.commit()
        flash('Profile updated', 'success')
        return redirect(url_for('doc_profile'))
    return render_template('doctor/profile.html', doc=d)

# Patient Routes
@app.route('/patient')
@pat_req
def pat_dash():
    p = Pat.query.filter_by(uid=session['uid']).first()
    apts = Apt.query.filter_by(pid=p.id).all() if p else []
    recs = Rec.query.filter_by(pid=p.id).all() if p else []
    return render_template('patient/dash.html', pat=p, apts=apts, recs=recs)

@app.route('/patient/docs')
@pat_req
def pat_docs():
    docs = Doc.query.all()
    return render_template('patient/docs.html', docs=docs)

@app.route('/patient/apt/book/<int:did>', methods=['GET', 'POST'])
@pat_req
def pat_apt_book(did):
    d = Doc.query.get_or_404(did)
    p = Pat.query.filter_by(uid=session['uid']).first()
    if request.method == 'POST':
        dt = request.form.get('dt')
        tm = request.form.get('tm')
        nt = request.form.get('nt')
        a = Apt(pid=p.id, did=did, dt=datetime.strptime(dt, '%Y-%m-%d').date(), tm=tm, nt=nt)
        db.session.add(a)
        db.session.commit()
        flash('Appointment booked successfully', 'success')
        return redirect(url_for('pat_apts'))
    return render_template('patient/apt_form.html', doc=d)

@app.route('/patient/apts')
@pat_req
def pat_apts():
    p = Pat.query.filter_by(uid=session['uid']).first()
    apts = Apt.query.filter_by(pid=p.id).all() if p else []
    return render_template('patient/apts.html', apts=apts)

@app.route('/patient/apt/cancel/<int:id>')
@pat_req
def pat_apt_cancel(id):
    a = Apt.query.get_or_404(id)
    a.st = 'cancelled'
    db.session.commit()
    flash('Appointment cancelled', 'success')
    return redirect(url_for('pat_apts'))

@app.route('/patient/recs')
@pat_req
def pat_recs():
    p = Pat.query.filter_by(uid=session['uid']).first()
    recs = Rec.query.filter_by(pid=p.id).all() if p else []
    return render_template('patient/recs.html', recs=recs)

@app.route('/patient/profile', methods=['GET', 'POST'])
@pat_req
def pat_profile():
    p = Pat.query.filter_by(uid=session['uid']).first()
    if request.method == 'POST':
        p.user.nm = request.form.get('nm')
        p.user.ph = request.form.get('ph')
        p.gen = request.form.get('gen')
        p.bg = request.form.get('bg')
        p.addr = request.form.get('addr')
        dob = request.form.get('dob')
        if dob:
            p.dob = datetime.strptime(dob, '%Y-%m-%d').date()
        db.session.commit()
        flash('Profile updated', 'success')
        return redirect(url_for('pat_profile'))
    return render_template('patient/profile.html', pat=p)

# Initialize DB and create admin
def init_db():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(un='admin').first():
            admin = User(un='admin', pw=generate_password_hash('admin123'), nm='Administrator', em='admin@ehospital.com', ph='1234567890', rl='admin')
            db.session.add(admin)
            db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
