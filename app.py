from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine, text
import random

app = Flask(__name__)

app.config['POSTGRES_USER'] = 'kami'
app.config['POSTGRES_PASSWORD'] = '123'
app.config['POSTGRES_HOST'] = '192.168.1.200'
app.config['POSTGRES_PORT'] = '5432'
app.config['POSTGRES_DB'] = 'phongdev'

# Kết nối cơ sở dữ liệu PostgreSQL
engine = create_engine(f"postgresql://{app.config['POSTGRES_USER']}:{app.config['POSTGRES_PASSWORD']}@{app.config['POSTGRES_HOST']}:{app.config['POSTGRES_PORT']}/{app.config['POSTGRES_DB']}")

# # Kết nối cơ sở dữ liệu PostgreSQL
# engine = create_engine(
#     "postgresql://kami:123@192.168.1.200:5432/phongdev"
# )

# Hàm lấy ngẫu nhiên một mẫu từ bảng instruction_dataset
def get_random_sample():
    query = text("SELECT * FROM instruction_dataset TABLESAMPLE BERNOULLI(1) LIMIT 1;")
    with engine.connect() as conn:
        result = conn.execute(query)
        return result.fetchone()

# Hàm cập nhật dữ liệu vào cơ sở dữ liệu
def update_sample_data(sample_id, instruction_vi, input_vi, output_vi):
    with engine.connect() as conn:
        query = text("UPDATE instruction_dataset SET instruction_vi=:insv, input_vi=:inpv, output_vi=:outv WHERE id=:id;")
        conn.execute(query, insv=instruction_vi, inpv=input_vi, outv=output_vi, id=sample_id)

# Biến lưu trữ trạng thái đăng nhập, ban đầu là False (chưa đăng nhập)
logged_in = False
phone_number = ""  # Biến lưu trữ số điện thoại người dùng đã đăng nhập

@app.route("/", methods=["GET", "POST"])
def main():
    global logged_in, phone_number
    # Kiểm tra trạng thái đăng nhập, nếu chưa đăng nhập, chuyển hướng đến trang login
    if not logged_in:
        return redirect(url_for('login'))

    if request.method == "POST":
        # Xử lý nút "Save" và các thao tác liên quan đến main.html
        instruction_vi = request.form["instruction_vi"]
        input_vi = request.form["input_vi"]
        output_vi = request.form["output_vi"]
        sample_id = int(request.form["id"])

        # Thực hiện câu truy vấn cập nhật vào cơ sở dữ liệu
        update_sample_data(sample_id, instruction_vi, input_vi, output_vi)

    # Lấy một mẫu ngẫu nhiên từ cơ sở dữ liệu
    sample = get_random_sample()

    # Render template và truyền dữ liệu để hiển thị trên giao diện web
    return render_template("main.html", sample=sample, logged_in=logged_in, phone_number=phone_number)

@app.route("/login", methods=["GET", "POST"])
def login():
    global logged_in, phone_number
    # Kiểm tra trạng thái đăng nhập, nếu đã đăng nhập, chuyển hướng đến trang main
    if logged_in:
        return redirect(url_for('main'))

    if request.method == "POST":
        # Xử lý đăng nhập ở đây
        # Kiểm tra thông tin đăng nhập từ form
        # Nếu thông tin đúng, đặt logged_in thành True và chuyển hướng đến trang main
        # Nếu thông tin sai, hiển thị thông báo lỗi

        # Ví dụ đơn giản: Mã đăng nhập thành công cho mọi giá trị nhập vào
        logged_in = True
        phone_number = request.form["phoneNumber"]
        return redirect(url_for('main'))

    return render_template("login.html")

@app.route("/logout")
def logout():
    global logged_in, phone_number
    # Xử lý đăng xuất ở đây
    # Đặt logged_in về False và xoá thông tin người dùng
    logged_in = False
    phone_number = ""
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
