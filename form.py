from flask_wtf import FlaskForm
from wtforms import FileField, FloatField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange, InputRequired
from flask_wtf.file import FileRequired, FileAllowed

class ConversionForm(FlaskForm):
    fichier = FileField('Fichier', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 'Fichiers autorisés : .jpg, .png, .pdf')
    ])

    largeur = FloatField('Largeur', validators=[
        InputRequired(), NumberRange(min=1, message="Valeur trop petite")
    ])

    hauteur = FloatField('Hauteur', validators=[
        InputRequired(), NumberRange(min=1, message="Valeur trop petite")
    ])

    unite = SelectField('Unité', choices=[
        ('mm', 'mm'), ('cm', 'cm'), ('in', 'pouces')
    ], validators=[DataRequired()])

    dpi = IntegerField('Résolution (DPI)', default=300, validators=[
        InputRequired(), NumberRange(min=72, max=1200)
    ])

    format = SelectField('Format de sortie', choices=[
        ('pdf', 'PDF'), ('png', 'PNG'), ('jpg', 'JPG')
    ], validators=[DataRequired()])

    submit = SubmitField('Générer')
