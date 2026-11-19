
from functools import wraps
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import DB_SETTINGS, SECRET_KEY
from db import Database
from repositories import UserRepository, RoomRepository, BookingRepository, ReviewRepository
from validators import RegistrationValidator

app = Flask(__name__)
app.secret_key = SECRET_KEY
db = Database(DB_SETTINGS)
users = UserRepository(db)
rooms = RoomRepository(db)
bookings = BookingRepository(db)
reviews = ReviewRepository(db)

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Для продолжения войдите в систему.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped

def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id") or session.get("role") != "admin":
            flash("Доступ разрешён только администратору.", "danger")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped

@app.route("/")
def index():
    return render_template("index.html", rooms=rooms.all())

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        form = {k: request.form.get(k, "").strip() for k in ("login", "password", "full_name", "phone", "email")}
        errors = RegistrationValidator.validate(form)
        if not errors and users.login_exists(form["login"]):
            errors["login"] = "Такой логин уже занят"
        if errors:
            return render_template("register.html", errors=errors, form=form)
        users.create(**form)
        flash("Пользователь создан. Теперь войдите в систему.", "success")
        return redirect(url_for("login"))
    return render_template("register.html", errors={}, form={})

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = users.authenticate(request.form.get("login", "").strip(), request.form.get("password", ""))
        if not user:
            flash("Неверный логин или пароль", "danger")
            return render_template("login.html")
        session.clear()
        session.update(user_id=user["id"], login=user["login"], full_name=user["full_name"], role=user["role"])
        flash("Вы успешно вошли.", "success")
        return redirect(url_for("admin" if user["role"] == "admin" else "cabinet"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Вы вышли из системы.", "info")
    return redirect(url_for("index"))

@app.route("/cabinet")
@login_required
def cabinet():
    if session.get("role") == "admin":
        return redirect(url_for("admin"))
    return render_template("cabinet.html", bookings=bookings.for_user(session["user_id"]))

@app.route("/booking/new", methods=["GET", "POST"])
@login_required
def booking_new():
    if session.get("role") == "admin":
        return redirect(url_for("admin"))
    room_list = rooms.all()
    errors, form = {}, {}
    if request.method == "POST":
        form = {k: request.form.get(k, "").strip() for k in ("room_name", "start_date", "payment_method")}
        room = rooms.find_by_name(form["room_name"])
        if not room:
            errors["room"] = "Выберите помещение из списка или укажите точное название из каталога"
        parsed_date = parse_date(form["start_date"])
        if not parsed_date:
            errors["start_date"] = "Введите дату в формате ДД.ММ.ГГГГ или ГГГГ-ММ-ДД"
        if form["payment_method"] not in BookingRepository.PAYMENT_METHODS:
            errors["payment_method"] = "Выберите способ оплаты"
        if not errors:
            bookings.create(session["user_id"], room["id"], parsed_date, form["payment_method"])
            flash("Заявка отправлена.", "success")
            return redirect(url_for("cabinet"))
    return render_template("booking_new.html", rooms=room_list, errors=errors, form=form)

def parse_date(value):
    for fmt in ("%d.%m.%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except (ValueError, TypeError):
            pass
    return None

@app.route("/booking/<int:booking_id>/delete", methods=["POST"])
@login_required
def booking_delete(booking_id):
    bookings.delete_for_user(booking_id, session["user_id"])
    flash("Заявка удалена, если она была новой.", "success")
    return redirect(url_for("cabinet"))

@app.route("/booking/<int:booking_id>/review", methods=["POST"])
@login_required
def booking_review(booking_id):
    text = request.form.get("text", "").strip()
    booking = bookings.get_for_user(booking_id, session["user_id"])
    if not booking or booking["status"] != "Завершено":
        flash("Отзыв можно оставить только по завершённой заявке.", "danger")
    elif not text:
        flash("Напишите текст отзыва.", "warning")
    else:
        reviews.create(booking_id, text)
        flash("Спасибо за отзыв!", "success")
    return redirect(url_for("cabinet"))

@app.route("/admin")
@admin_required
def admin():
    status = request.args.get("status", "")
    return render_template("admin.html", bookings=bookings.all(status or None),
                           statuses=BookingRepository.STATUSES, current_status=status)

@app.route("/admin/booking/<int:booking_id>/status", methods=["POST"])
@admin_required
def admin_change_status(booking_id):
    try:
        bookings.update_status(booking_id, request.form.get("status", ""))
        flash(f"Статус заявки №{booking_id} изменён.", "success")
    except ValueError:
        flash("Недопустимый статус.", "danger")
    return redirect(url_for("admin", status=request.args.get("status", "")))

@app.route("/admin/booking/<int:booking_id>/delete", methods=["POST"])
@admin_required
def admin_delete(booking_id):
    bookings.delete(booking_id)
    flash(f"Заявка №{booking_id} удалена.", "success")
    return redirect(url_for("admin"))

if __name__ == "__main__":
    app.run(debug=True)
