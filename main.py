from flask import Flask, render_template, send_file, request, jsonify
from flask_cors import CORS
import os
import json
import smtplib
from email.message import EmailMessage
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuration
MESSAGES_FILE = "messages.json"
MAIL_ADDRESS = "fivepack70@gmail.com"
MAIL_PASSWORD = "gome gvwk tshn ztwg"

# --- PAGES PRINCIPALES ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download')
def download():
    return render_template('soon.html')
    # return send_file('yapasencorewoula.zip', as_attachment=True)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/discord')
def discord():
    return render_template('discord.html')

@app.route('/adminnnnnnnnnnnnnnnnnn1234567gagagagagagagagaggagagagqsdqsldkqhsdzaeouiayze')
def admin():
    return render_template('admin.html')


# --- API MESSAGES ---

@app.route("/api/messages", methods=["GET"])
def get_messages():
    if not os.path.exists(MESSAGES_FILE):
        return jsonify([])
    with open(MESSAGES_FILE, "r") as f:
        return jsonify(json.load(f)[::-1])

@app.route("/api/contact", methods=["POST"])
def receive_message():
    data = request.json
    data["date"] = datetime.now().isoformat()

    if os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, "r") as f:
            messages = json.load(f)
    else:
        messages = []

    messages.append(data)
    with open(MESSAGES_FILE, "w") as f:
        json.dump(messages, f, indent=2)

    send_email(
        subject=f"Nouveau message de {data['name']}",
        content=data["message"],
        from_email=data["email"],
        to_email=MAIL_ADDRESS
    )

    return jsonify({"message": "Message reçu"}), 200

@app.route("/api/reply", methods=["POST"])
def reply_message():
    data = request.json
    reply_text = data.get("reply")
    index = data.get("index")

    if not reply_text or index is None:
        return jsonify({"error": "Requête invalide"}), 400

    # Envoi de l'email
    send_email(
        subject="Réponse de FIVEPACK",
        content=reply_text,
        from_email=MAIL_ADDRESS,
        to_email=data["to"]
    )

    # Suppression du message
    if os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, "r") as f:
            messages = json.load(f)

        if 0 <= index < len(messages):
            del messages[-(index + 1)]  # car la liste est inversée à l'affichage

            with open(MESSAGES_FILE, "w") as f:
                json.dump(messages, f, indent=2)

    return jsonify({"message": "Réponse envoyée et message supprimé"}), 200


# --- ENVOI MAIL ---

def send_email(subject, content, from_email, to_email):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email
    msg.set_content(content)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(MAIL_ADDRESS, MAIL_PASSWORD)
        smtp.send_message(msg)


# --- DÉMARRAGE DU SERVEUR ---

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
