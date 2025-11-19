from flask import Flask, render_template, request, session, redirect, url_for
import csv
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey123"

# -------------------
# Biogas Calculator Route
# -------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if "history" not in session:
        session["history"] = []

    if request.method == "POST":
        # Biogas simulation logic
        waste_type = request.form.get("waste_type", "").lower()
        mass = float(request.form.get("mass", 0))
        temperature = request.form.get("temperature")
        temperature = float(temperature) if temperature else 25

        if waste_type == "cowdung":
            yield_factor = 0.20
            tip = "Mix with water for better fermentation."
        elif waste_type == "food waste":
            yield_factor = 0.40
            tip = "Avoid oily food; chop waste finely."
        elif waste_type == "crop residue":
            yield_factor = 0.25
            tip = "Shred residues to increase surface area."
        else:
            yield_factor = 0.10
            tip = "General organic waste; results may vary."

        # Temperature adjustment
        if temperature < 25:
            yield_factor *= 0.95
        elif temperature > 25:
            yield_factor *= 1.05

        daily_output = mass * yield_factor
        cumulative_output = daily_output

        result = {
            "waste": waste_type.title(),
            "mass": mass,
            "temperature": temperature,
            "yield_factor": round(yield_factor, 2),
            "daily_output": round(daily_output, 2),
            "total_output": round(cumulative_output, 2),
            "tip": tip
        }

        # Save last 5 simulations
        history = session["history"]
        history.insert(0, result)
        session["history"] = history[:5]

        return render_template("result.html", result=result, history=session["history"])

    return render_template("index.html")

# -------------------
# Quote Form Submission Route with Timestamp
# -------------------
@app.route("/submit_quote", methods=["POST"])
def submit_quote():
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    service = request.form.get("service")
    message = request.form.get("message")

    # Get current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # CSV file path
    csv_file = os.path.join(os.getcwd(), 'quotes.csv')

    # Save to CSV
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            # Write header if file does not exist
            writer.writerow(['Timestamp', 'Name', 'Email', 'Phone', 'Service', 'Message'])
        writer.writerow([timestamp, name, email, phone, service, message])

    # Redirect back to home page
    return redirect(url_for('index'))

# -------------------
# Run Flask App
# -------------------
if __name__ == "__main__":
    app.run(debug=True)
