"""Репозитории отделяют SQL-запросы от маршрутов Flask."""
from werkzeug.security import generate_password_hash, check_password_hash

class UserRepository:
    def __init__(self, db): self.db = db
    def login_exists(self, login):
        return self.db.fetch_one("SELECT id FROM users WHERE login=%s", (login,)) is not None
    def create(self, login, password, full_name, phone, email, role="user"):
        self.db.execute("""INSERT INTO users(login,password_hash,full_name,phone,email,role)
                           VALUES(%s,%s,%s,%s,%s,%s)""",
                        (login, generate_password_hash(password), full_name, phone, email, role))
    def authenticate(self, login, password):
        user = self.db.fetch_one("SELECT * FROM users WHERE login=%s", (login,))
        return user if user and check_password_hash(user["password_hash"], password) else None

class RoomRepository:
    def __init__(self, db): self.db = db
    def all(self):
        return self.db.fetch_all("SELECT * FROM rooms ORDER BY id")
    def find_by_name(self, name):
        return self.db.fetch_one("SELECT * FROM rooms WHERE LOWER(name)=LOWER(%s)", (name,))

class BookingRepository:
    STATUSES = ("Новая", "Мероприятие назначено", "Завершено")
    PAYMENT_METHODS = ("При очном посещении", "Перевод по СБП")
    def __init__(self, db): self.db = db
    def create(self, user_id, room_id, start_date, payment_method):
        self.db.execute("""INSERT INTO bookings(user_id,room_id,start_date,payment_method)
                           VALUES(%s,%s,%s,%s)""", (user_id, room_id, start_date, payment_method))
    def get_for_user(self, booking_id, user_id):
        return self.db.fetch_one("SELECT * FROM bookings WHERE id=%s AND user_id=%s",
                                 (booking_id, user_id))
    def for_user(self, user_id):
        return self.db.fetch_all("""SELECT b.*, TO_CHAR(b.start_date,'DD.MM.YYYY') AS start_date_text,
                                    r.name AS room_name, rv.text AS review_text
                                    FROM bookings b JOIN rooms r ON r.id=b.room_id
                                    LEFT JOIN reviews rv ON rv.booking_id=b.id
                                    WHERE b.user_id=%s ORDER BY b.created_at DESC""", (user_id,))
    def all(self, status=None):
        sql = """SELECT b.*, TO_CHAR(b.start_date,'DD.MM.YYYY') AS start_date_text,
                 r.name AS room_name,u.full_name,u.phone,u.email
                 FROM bookings b JOIN rooms r ON r.id=b.room_id
                 JOIN users u ON u.id=b.user_id """
        params = ()
        if status:
            sql += "WHERE b.status=%s "
            params = (status,)
        return self.db.fetch_all(sql + "ORDER BY b.created_at DESC", params)
    def update_status(self, booking_id, status):
        if status not in self.STATUSES:
            raise ValueError("Недопустимый статус")
        self.db.execute("UPDATE bookings SET status=%s WHERE id=%s", (status, booking_id))
    def delete(self, booking_id):
        self.db.execute("DELETE FROM bookings WHERE id=%s", (booking_id,))
    def delete_for_user(self, booking_id, user_id):
        self.db.execute("DELETE FROM bookings WHERE id=%s AND user_id=%s AND status='Новая'",
                        (booking_id, user_id))

class ReviewRepository:
    def __init__(self, db): self.db = db
    def create(self, booking_id, text):
        self.db.execute("INSERT INTO reviews(booking_id,text) VALUES(%s,%s)", (booking_id,text))
