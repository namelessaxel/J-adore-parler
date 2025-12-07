"""
API Flask pour le service de décomposition phonétique
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from phonetic_engine import PhoneticEngine
import os

app = Flask(__name__)
CORS(app)  # Permet les requêtes cross-origin

# Initialisation du moteur phonétique au démarrage
print("Initialisation du moteur phonétique...")
engine = PhoneticEngine('mots_francais.txt')
print("Moteur prêt!")

@app.route('/', methods=['GET'])
def home():
    """Page d'accueil avec infos sur l'API"""
    return jsonify({
        'service': 'API de décomposition phonétique française',
        'version': '1.0',
        'endpoints': {
            '/analyze': 'POST - Analyse un texte et retourne les décompositions',
            '/health': 'GET - Vérifie que le service fonctionne'
        },
        'example': {
            'url': '/analyze',
            'method': 'POST',
            'body': {
                'text': 'je t\'aime',
                'top_n': 3
            }
        }
    })

@app.route('/health', methods=['GET'])
def health():
    """Endpoint de santé pour vérifier que le service fonctionne"""
    return jsonify({
        'status': 'healthy',
        'dictionary_loaded': len(engine.word_to_phonetic) > 0,
        'total_words': len(engine.word_to_phonetic)
    })

@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Analyse un texte et retourne les meilleures décompositions phonétiques
    
    Body JSON:
    {
        "text": "je t'aime",
        "top_n": 3  // optionnel, par défaut 3
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'error': 'Le champ "text" est requis'
            }), 400
        
        text = data['text'].strip()
        top_n = data.get('top_n', 3)
        
        if not text:
            return jsonify({
                'error': 'Le texte ne peut pas être vide'
            }), 400
        
        if not isinstance(top_n, int) or top_n < 1 or top_n > 10:
            return jsonify({
                'error': 'top_n doit être un entier entre 1 et 10'
            }), 400
        
        # Analyse du texte
        results = engine.find_best_decompositions(text, top_n=top_n)
        
        return jsonify({
            'success': True,
            'data': results
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/phonetic', methods=['POST'])
def get_phonetic():
    """
    Convertit un texte en phonétique (utile pour déboguer)
    
    Body JSON:
    {
        "text": "bonjour"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                'error': 'Le champ "text" est requis'
            }), 400
        
        text = data['text'].strip()
        phonetic = engine.text_to_phonetic(text)
        
        return jsonify({
            'success': True,
            'text': text,
            'phonetic': phonetic
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
