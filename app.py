from flask import Flask, render_template, request, redirect, url_for, jsonify
from sqlalchemy import create_engine, text

app = Flask(__name__)

# Cấu hình cơ sở dữ liệu PostgreSQL
app.config['POSTGRES_USER'] = 'kami'
app.config['POSTGRES_PASSWORD'] = '123'
app.config['POSTGRES_HOST'] = '192.168.1.200'
app.config['POSTGRES_PORT'] = '5432'
app.config['POSTGRES_DB'] = 'phongdev'

# Kết nối cơ sở dữ liệu PostgreSQL
engine = create_engine(
    f"postgresql://{app.config['POSTGRES_USER']}:{app.config['POSTGRES_PASSWORD']}@{app.config['POSTGRES_HOST']}:{app.config['POSTGRES_PORT']}/{app.config['POSTGRES_DB']}"
)

# Các hàm xử lý dữ liệu
def get_random_sample():
    global phone_number

    with engine.connect() as conn:
        query = text("SELECT * FROM instruction_dataset_mt WHERE status = :status LIMIT 1;")
        result = conn.execute(query, status=f"{phone_number} repairing").fetchone()

        if result:
            return result
        else:
            query = text("SELECT * FROM instruction_dataset_mt TABLESAMPLE BERNOULLI(1) LIMIT 1;")
            result = conn.execute(query).fetchone()

            if result:
                sample_id = result.id
                update_status_query = text("UPDATE instruction_dataset_mt SET status = :status WHERE id = :id;")
                conn.execute(update_status_query, status=f"{phone_number} repairing", id=sample_id)

            return result


def update_sample_data(sample_id, instruction_vi, input_vi, output_vi):
    with engine.connect() as conn:
        query = text("UPDATE instruction_dataset_mt SET instruction_vi=:insv, input_vi=:inpv, output_vi=:outv, status=:status WHERE id=:id;")
        if not instruction_vi:
            instruction_vi = ""  # Cung cấp giá trị mặc định nếu instruction_vi rỗng
        if not input_vi:
            input_vi = ""  # Cung cấp giá trị mặc định nếu input_vi rỗng
        if not output_vi:
            output_vi = ""  # Cung cấp giá trị mặc định nếu output_vi rỗng
        conn.execute(query, insv=instruction_vi, inpv=input_vi, outv=output_vi, status=f"{phone_number} submited", id=sample_id)


logged_in = False
phone_number = ""


@app.route("/log", methods=["GET", "POST"])
def log():
    global logged_in, phone_number

    if not logged_in:
        return redirect(url_for('login'))

    with engine.connect() as conn:
        query = text("SELECT * FROM instruction_dataset_mt WHERE status LIKE :status;")
        logs = conn.execute(query, status="%submited%").fetchall()

    return render_template("log.html", logs=logs, logged_in=logged_in, phone_number=phone_number)


@app.route("/", methods=["GET", "POST"])
def main():
    global logged_in, phone_number

    if not logged_in:
        return redirect(url_for('login'))

    if request.method == "POST":
        instruction_vi = request.form["instruction_vi"]
        input_vi = request.form["input_vi"]
        output_vi = request.form["output_vi"]
        sample_id = int(request.form["id"])
        update_sample_data(sample_id, instruction_vi, input_vi, output_vi)

    sample = get_random_sample()
    return render_template("main.html", sample=sample, logged_in=logged_in, phone_number=phone_number)


@app.route("/login", methods=["GET", "POST"])
def login():
    global logged_in, phone_number

    if logged_in:
        return redirect(url_for('main'))

    if request.method == "POST":
        logged_in = True
        phone_number = request.form["phoneNumber"]
        return redirect(url_for('main'))

    return render_template("login.html")


@app.route("/logout")
def logout():
    global logged_in, phone_number
    logged_in = False
    phone_number = ""
    return redirect(url_for('login'))


@app.route("/edit_log/<int:id>", methods=["POST"])
def edit_log(id):
    global phone_number

    if request.method == "POST":
        data_instruction = request.form.get("instruction_vi")
        data_input = request.form.get("input_vi")
        data_output = request.form.get("output_vi")

        if data_instruction is not None or data_input is not None or data_output is not None:
            update_sample_data(id, data_instruction, data_input, data_output)
            return jsonify({"message": "Edit successful!"})
        else:
            return jsonify({"error": "No data to update."}), 400

    return jsonify({"error": "Invalid request."}), 400

if __name__ == "__main__":
    app.run(debug=True)
