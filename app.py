from flask import Flask, render_template, url_for, flash, redirect, request, abort
from forms import RegistrationForm, LoginForm, PostForm, CommentForm
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import (
    LoginManager, login_user, logout_user, login_required, current_user, UserMixin
)
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '888888818'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# CSRF Protection
csrf = CSRFProtect(app)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "danger"

@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password_hash = db.Column(db.String(128), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    flair = db.Column(db.String(20), nullable=False, default="OTHER")
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comments = db.relationship('Comment', backref='post', lazy=True, cascade="all, delete")

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted:%Y-%m-%d}')"


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    def __repr__(self):
        return f"Comment('{self.id}', '{self.date_posted:%Y-%m-%d}')"

def ensure_flair_column():
    from sqlalchemy import text
    with app.app_context():
        rows = db.session.execute(text("PRAGMA table_info(post)")).fetchall()
        cols = {row[1] for row in rows}
        if "flair" not in cols:
            db.session.execute(
                text("ALTER TABLE post ADD COLUMN flair VARCHAR(20) NOT NULL DEFAULT 'OTHER'")
            )
            db.session.commit()


@app.route("/")
@app.route("/home")
def home():
    selected_flair = request.args.get("flair")
    q = Post.query
    if selected_flair:
        q = q.filter_by(flair=selected_flair)
    posts = q.order_by(Post.date_posted.desc()).all()
    FLAIRS = [
        ("TRADE_HELP", "TRADE HELP"),
        ("WAIVER_WIRE", "WAIVER WIRE ADVICE"),
        ("INJURY_TALK", "INJURY TALK"),
        ("OTHER", "OTHER"),
    ]
    return render_template(
        "home.html", title="Home", posts=posts, flairs=FLAIRS, selected_flair=selected_flair
    )


@app.route("/about")
def about():
    return render_template("about.html", title="About")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        exists = User.query.filter(
            (User.username == form.username.data) | (User.email == form.email.data)
        ).first()
        if exists:
            flash("Username or email already taken.", "danger")
            return redirect(url_for("register"))
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(f"Welcome, {user.username}! Your account is ready.", "success")
        return redirect(url_for("home"))
    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f"Welcome back, {user.username}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("home"))
        flash("Login unsuccessful. Check email and password.", "danger")
    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "success")
    return redirect(url_for("home"))


@app.route("/post/new", methods=["GET", "POST"])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            flair=form.flair.data,
            content=form.content.data,
            author=current_user
        )
        db.session.add(post)
        db.session.commit()
        flash("Post published!", "success")
        return redirect(url_for("home"))
    return render_template("post_create.html", title="New Post", form=form)


@app.route("/post/<int:post_id>")
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("post_detail.html", title=post.title, post=post)


@app.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.flair = form.flair.data
        post.content = form.content.data
        db.session.commit()
        flash("Post updated.", "success")
        return redirect(url_for("post_detail", post_id=post.id))
    elif request.method == "GET":
        form.title.data = post.title
        form.flair.data = post.flair
        form.content.data = post.content
    return render_template("post_edit.html", title="Edit Post", form=form, post=post)


@app.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Post deleted.", "success")
    return redirect(url_for("home"))


@app.route("/post/<int:post_id>/comment", methods=["POST"])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        c = Comment(content=form.content.data, author=current_user, post=post)
        db.session.add(c)
        db.session.commit()
        flash("Comment added.", "success")
    else:
        flash("Could not add comment.", "danger")
    return redirect(url_for("post_detail", post_id=post.id))


@app.route("/seed")
def seed():
    if not User.query.first():
        u = User(username="Diego", email="diego@example.com")
        u.set_password("password")
        db.session.add(u)
        db.session.commit()
    u = User.query.first()
    if Post.query.count() == 0:
        db.session.add_all([
            Post(title="Hello World", flair="OTHER", content="First post content", author=u),
            Post(title="Trade Block", flair="TRADE_HELP", content="Who wants to trade RBs?", author=u),
        ])
        db.session.commit()
    flash("Seeded demo user and posts.", "success")
    return redirect(url_for("home"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        ensure_flair_column()
    app.run(debug=True)
