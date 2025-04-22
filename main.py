from flask import Flask, render_template, send_file, request, jsonify
from flask import Flask, send_from_directory
from flask_login import LoginManager, UserMixin, login_required, current_user
from flask_cors import CORS
import os
import json
import smtplib
from email.message import EmailMessage
from datetime import datetime

app = Flask(__name__, static_url_path='', static_folder='static')
CORS(app)

# Configuration
MESSAGES_FILE = "messages.json"
MAIL_ADDRESS = "fivepack70@gmail.com"
MAIL_PASSWORD = "gome gvwk tshn ztwg"

app.secret_key = '01928734OAZDSGF029384701Y24GH1ZF°19URF]@\^~#@'
SECRET_TOKEN = '5f4dcc3b5aa765d61d8327deb882cf99'

# Configuration de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/"  # Route à rediriger si non authentifié

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    # Ici vous implémenteriez la logique pour charger un utilisateur depuis votre base de données
    return User(user_id)

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

@app.route('/admin')
def admin():
    return render_template('admin.html', secret_token=SECRET_TOKEN)

@app.route('/api/config')
def get_config():
    token = request.headers.get("X-Secret-Token")
    if token != SECRET_TOKEN:
        return render_template('Interdit'), 403

    try:
        with open('instance/config.json', 'r') as f:
            config = json.load(f)
        return jsonify(config)
    except Exception as e:
        app.logger.error(f"Erreur: {str(e)}")
        return jsonify({"error": "Erreur serveur"}), 500

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

    # 🔐 Adresse IP
    user_ip = request.remote_addr

    # Sauvegarde message dans messages.json
    if os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, "r") as f:
            messages = json.load(f)
    else:
        messages = []

    messages.append(data)
    with open(MESSAGES_FILE, "w") as f:
        json.dump(messages, f, indent=2)

    log_entry = {
        "ip": request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip(),
        "email": data["email"],
        "name": data["name"],
        "message": data["message"],
        "date": data["date"]
    }

    if os.path.exists("logs.json"):
        with open("logs.json", "r") as f:
            logs = json.load(f)
    else:
        logs = []

    logs.append(log_entry)
    with open("logs.json", "w") as f:
        json.dump(logs, f, indent=2)

    # Envoi email à l'admin
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
