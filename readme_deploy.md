# Word Remaker - Décomposition Phonétique Française

API qui décompose un texte français en phonétique et trouve des mots alternatifs pour créer des phrases exotiques.

## 📋 Prérequis

1. Un compte GitHub
2. Un compte Render.com (gratuit)
3. Le fichier `mots_francais.txt` (dictionnaire français)

## 🚀 Déploiement sur Render.com

### Étape 1 : Préparation des fichiers

1. **Télécharge le dictionnaire français** :
   - Va sur : https://raw.githubusercontent.com/chrplr/openlexicon/master/datasets-info/Liste-de-mots-francais-Gutenberg/liste.de.mots.francais.frgut.txt
   - Sauvegarde le fichier sous le nom `mots_francais.txt`

2. **Crée un dépôt GitHub** :
   - Va sur GitHub et crée un nouveau repository (ex: `word-remaker`)
   - Clone-le sur ton PC

3. **Ajoute tous les fichiers dans le repo** :
   ```
   word-remaker/
   ├── app.py
   ├── phonetic_engine.py
   ├── requirements.txt
   ├── mots_francais.txt
   └── README.md
   ```

4. **Commit et push** :
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

### Étape 2 : Déploiement sur Render

1. **Va sur [Render.com](https://render.com)** et connecte-toi

2. **Crée un nouveau Web Service** :
   - Clique sur "New +" → "Web Service"
   - Connecte ton compte GitHub
   - Sélectionne le repo `word-remaker`

3. **Configure le service** :
   - **Name** : `word-remaker` (ou ce que tu veux)
   - **Environment** : `Python 3`
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `gunicorn app:app`
   - **Plan** : Free

4. **Ajoute une variable d'environnement** (important pour espeak-ng) :
   - Dans "Environment", clique sur "Add Environment Variable"
   - **Key** : `APT_PACKAGES`
   - **Value** : `espeak-ng`

5. **Déploie** :
   - Clique sur "Create Web Service"
   - Attends 5-10 minutes que le déploiement se termine

### Étape 3 : Test de l'API

Une fois déployé, tu auras une URL comme : `https://word-remaker.onrender.com`

**Test avec curl** :
```bash
curl -X POST https://word-remaker.onrender.com/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "je t'\''aime", "top_n": 3}'
```

**Test avec ton navigateur** :
Va sur : `https://word-remaker.onrender.com/health`

## 📡 Endpoints de l'API

### `GET /`
Informations sur l'API

### `GET /health`
Vérifie que le service fonctionne
```json
{
  "status": "healthy",
  "dictionary_loaded": true,
  "total_words": 336000
}
```

### `POST /analyze`
Analyse un texte et retourne les décompositions

**Request** :
```json
{
  "text": "je t'aime",
  "top_n": 3
}
```

**Response** :
```json
{
  "success": true,
  "data": {
    "solutions": [
      {
        "text": "jeux thème",
        "words": ["jeux", "thème"],
        "exotic_score": 45.2
      }
    ],
    "input_text": "je t'aime",
    "phonetic": "ʒətɛm",
    "processing_time": 0.5,
    "total_solutions": 12
  }
}
```

### `POST /phonetic`
Convertit un texte en phonétique

**Request** :
```json
{
  "text": "bonjour"
}
```

**Response** :
```json
{
  "success": true,
  "text": "bonjour",
  "phonetic": "bɔ̃ʒuʁ"
}
```

## ⚙️ Variables configurables

Dans `app.py`, tu peux modifier :
- `top_n` : Nombre de solutions à retourner (1-10)

Dans `phonetic_engine.py`, tu peux modifier :
- `batch_size` : Taille des batchs pour la phonétisation (défaut: 1000)
- Les règles de scoring pour l'exotisme

## 🐛 Dépannage

**Problème : "espeak not installed"**
- Vérifie que la variable d'environnement `APT_PACKAGES=espeak-ng` est bien définie dans Render

**Problème : Le déploiement prend trop de temps**
- Normal pour le premier déploiement (chargement du dictionnaire)
- Les déploiements suivants seront plus rapides

**Problème : L'API est lente**
- Le plan gratuit de Render a des limitations de CPU
- Pour de meilleures performances, upgrade vers un plan payant

## 📊 Performances estimées (plan gratuit Render)

- Chargement du dictionnaire : ~30-60 secondes au démarrage
- Analyse d'une phrase courte (3-5 mots) : ~0.5-2 secondes
- Analyse d'une phrase longue (10+ mots) : ~2-10 secondes

## 🔄 Prochaines étapes

Une fois que le backend fonctionne, on pourra créer l'interface web (frontend) !
