import os
from dotenv import load_dotenv
from flask import Flask, request, render_template
from groq import Groq
from datetime import datetime

# Charger les variables d'environnement depuis .env
load_dotenv()


# Récupération de la clé
API_KEY = os.environ.get("GROQ_API_KEY")

# Si non trouvée → erreur immédiate
if not API_KEY:
    raise ValueError("La clé API Groq (GROQ_API_KEY) n'a pas été trouvée dans le fichier .env")

# Initialiser Groq
client = Groq(api_key=API_KEY)

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("formulaire.html")

@app.route("/analyse", methods=["POST"])
def analyse():
    texte_avis = request.form.get("texte_avis", "").strip()
    suggestion = request.form.get("suggestion", "").strip()

    if not texte_avis:
        return "Le champ Avis est obligatoire."

    try:
        # Résumé avis + sentiment
        prompt_avis = f"Résume le texte suivant et indique aussi le sentiment (positif, négatif, neutre) :\n\n{texte_avis}"
        response_avis = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt_avis}],
            model="openai/gpt-oss-20b"
        )
        resume_avis = response_avis.choices[0].message.content

        # Résumé suggestion
        if suggestion:
            prompt_suggestion = f"Résume la suggestion suivante :\n\n{suggestion}"
            response_suggestion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt_suggestion}],
                model="openai/gpt-oss-20b"
            )
            resume_suggestion = response_suggestion.choices[0].message.content
        else:
            resume_suggestion = "Pas de suggestion fournie."

        # Affichage dans terminal
        print(f"\n=== Analyse ({datetime.now()}) ===")
        print("--- Résumé Avis + Sentiment ---")
        print(resume_avis)
        print("--- Résumé Suggestion ---")
        print(resume_suggestion)
        print("===============================")

    except Exception as e:
        print(f"Erreur analyse IA : {str(e)}")

    return "Merci pour votre avis !"

if __name__ == "__main__":
    app.run(debug=True)
