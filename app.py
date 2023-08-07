from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine, text

app = Flask(__name__)

app.config['POSTGRES_USER'] = 'kami'
app.config['POSTGRES_PASSWORD'] = '123'
app.config['POSTGRES_HOST'] = '192.168.1.200'
app.config['POSTGRES_PORT'] = '5432'
app.config['POSTGRES_DB'] = 'phongdev'

# Kết nối cơ sở dữ liệu PostgreSQL
engine = create_engine(
    f"postgresql://{app.config['POSTGRES_USER']}:{app.config['POSTGRES_PASSWORD']}@{app.config['POSTGRES_HOST']}:{app.config['POSTGRES_PORT']}/{app.config['POSTGRES_DB']}"
)


def get_random_sample():
    global phone_number

    with engine.connect() as conn:
        query = text("SELECT * FROM instruction_dataset WHERE status = :status LIMIT 1;")
        result = conn.execute(query, status=f"{phone_number} repairing").fetchone()

        if result:
            return result
        else:
            query = text("SELECT * FROM instruction_dataset TABLESAMPLE BERNOULLI(1) LIMIT 1;")
            result = conn.execute(query).fetchone()

            if result:
                sample_id = result.id
                update_status_query = text("UPDATE instruction_dataset SET status = :status WHERE id = :id;")
                conn.execute(update_status_query, status=f"{phone_number} repairing", id=sample_id)

            return result


def update_sample_data(sample_id, instruction, input_data, output, instruction_vi, input_vi, output_vi):
    with engine.connect() as conn:
        query = text("UPDATE instruction_dataset SET instruction=:ins, input=:inp, output=:out, instruction_vi=:insv, input_vi=:inpv, output_vi=:outv, status=:status WHERE id=:id;")
        conn.execute(query, ins=instruction, inp=input_data, out=output, insv=instruction_vi, inpv=input_vi, outv=output_vi, status=f"{phone_number} submited", id=sample_id)



logged_in = False
phone_number = ""


@app.route("/log", methods=["GET", "POST"])
def log():
    global logged_in, phone_number

    if not logged_in:
        return redirect(url_for('login'))

    with engine.connect() as conn:
        query = text("SELECT * FROM instruction_dataset WHERE status LIKE :status;")
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
        # Handle the data edit here and save it to the database
        instruction = request.form["instruction"]
        input_data = request.form["input"]
        output = request.form["output"]
        instruction_vi = request.form["instruction_vi"]
        input_vi = request.form["input_vi"]
        output_vi = request.form["output_vi"]

        # Update the data in the database with all required parameters
        update_sample_data(id, instruction, input_data, output, instruction_vi, input_vi, output_vi)

    return "Edit successful!"



if __name__ == "__main__":
    app.run(debug=True)
