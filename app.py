import os
import json
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, url_for
from groq import Groq

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
app = Flask(__name__)

DB_FILE = "base_analyses.json"

def charger_donnees():
    if not os.path.exists(DB_FILE): return []
    with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)

def sauvegarder_donnees(nouvelle_analyse):
    donnees = charger_donnees()
    donnees.insert(0, nouvelle_analyse)
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(donnees, f, indent=4, ensure_ascii=False)

@app.route("/")
def index():
    return render_template("formulaire.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", analyses=charger_donnees())

@app.route("/analyse", methods=["POST"])
def analyse():
    texte_avis = request.form.get("texte_avis", "").strip()
    suggestion = request.form.get("suggestion", "").strip()

    try:
        # Prompt optimisé pour se passer de l'original
        prompt_ia = (
            f"Agis en tant qu'expert en expérience client. Analyse le retour suivant et "
            f"fournis un rapport détaillé en JSON. L'avis original sera supprimé, donc ton explication "
            f"doit être complète. "
            f"Clés JSON : 'titre_resume' (un titre court), 'explication_complete' (le coeur de l'analyse), "
            f"'sentiment' (Positif/Négatif/Neutre), 'priorite' (1 à 5), 'action_recommandee'. "
            f"Retour : {texte_avis}. Suggestion : {suggestion}"
        )
        
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt_ia}],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"}
        )
        
        # On récupère uniquement le cerveau de l'IA
        rapport_ia = json.loads(response.choices[0].message.content)

        # On n'enregistre PAS l'avis original ici
        donnees_finales = {
            "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "rapport": rapport_ia
        }
        
        sauvegarder_donnees(donnees_finales)

        return """
        <h1>Merci !</h1>
        <p>Votre message a été envoyé avec succès. Nos équipes vont l'étudier.</p>
        <a href="/">Envoyer un autre avis</a>
        """

    except Exception as e:
        return f"Erreur : {str(e)}"

if __name__ == "__main__":
    app.run(debug=True)