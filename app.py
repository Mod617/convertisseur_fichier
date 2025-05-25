import os
import mimetypes
from flask import Flask, render_template, url_for
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename
from PIL import Image, UnidentifiedImageError
from pdf2image import convert_from_path
from reportlab.pdfgen.canvas import Canvas
from form import ConversionForm

# ⛔ Désactiver la limite de pixels de sécurité pour grands fichiers
Image.MAX_IMAGE_PIXELS = None

# Configuration
UPLOAD_FOLDER = "uploads"
CONVERTED_FOLDER = os.path.join("static", "converted")
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
ALLOWED_MIME_TYPES = {
    'image/jpeg',
    'image/png',
    'application/pdf'
}

# Créer les dossiers si pas présents
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

# Initialiser Flask
app = Flask(__name__)

# 🔐 Clé secrète sécurisée (à personnaliser en prod)
app.config['SECRET_KEY'] = 'T7sj$Wp!1q9&Z@e0dPfY#mLxBnC34vXg'

# 📏 Limite de taille de fichier : 50 Mo
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CONVERTED_FOLDER'] = CONVERTED_FOLDER
app.static_folder = 'static'

# Activer protection CSRF
csrf = CSRFProtect(app)

# Vérifier le type MIME réel du fichier
def allowed_mime(filepath):
    mime, _ = mimetypes.guess_type(filepath)
    return mime in ALLOWED_MIME_TYPES

@app.route('/', methods=['GET', 'POST'])
def index():
    form = ConversionForm()
    if form.validate_on_submit():
        fichier = form.fichier.data
        largeur = form.largeur.data
        hauteur = form.hauteur.data
        unite = form.unite.data
        format_sortie = form.format.data
        dpi = form.dpi.data or 300

        # Conversion en points
        if unite == 'mm':
            largeur *= 2.83465
            hauteur *= 2.83465
        elif unite == 'cm':
            largeur *= 28.3465
            hauteur *= 28.3465
        elif unite == 'in':
            largeur *= 72
            hauteur *= 72

        filename = secure_filename(fichier.filename)
        chemin = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        fichier.save(chemin)

        # Vérification MIME
        if not allowed_mime(chemin):
            os.remove(chemin)
            return "❌ Type de fichier non autorisé.", 400

        # Nom du fichier final
        nom_sans_ext = os.path.splitext(filename)[0]
        sortie_nom = f"{nom_sans_ext}_converted.{format_sortie}"
        sortie_path = os.path.join(CONVERTED_FOLDER, sortie_nom)

        try:
            if filename.lower().endswith('.pdf'):
                images = convert_from_path(chemin, dpi=dpi)
                canvas = Canvas(sortie_path, pagesize=(largeur, hauteur))
                for i, img in enumerate(images):
                    img = img.resize((int(largeur), int(hauteur)), Image.LANCZOS)
                    temp_img = os.path.join(CONVERTED_FOLDER, f"temp_{i}.jpg")
                    img.save(temp_img)
                    canvas.drawImage(temp_img, 0, 0, width=largeur, height=hauteur)
                    canvas.showPage()
                    os.remove(temp_img)
                canvas.save()
            else:
                img = Image.open(chemin)
                img = img.resize((int(largeur), int(hauteur)), Image.LANCZOS)
                img.save(sortie_path, format=format_sortie.upper())
        except UnidentifiedImageError:
            os.remove(chemin)
            return "❌ Erreur : fichier image non valide.", 400

        return render_template('index.html', form=form, success=True, fichier_genere=sortie_nom)

    return render_template('index.html', form=form)

# 🔔 Gérer erreur 413 : fichier trop lourd
@app.errorhandler(413)
def file_too_large(e):
    return "❌ Le fichier est trop volumineux (max 50 Mo autorisés).", 413

if __name__ == '__main__':
    app.run(debug=True)
