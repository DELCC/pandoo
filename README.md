# Pandoo Backend

Backend de l’application Pandoo développé avec **FastAPI**, **SQLAlchemy** et **SQLite**.

Il gère :

* Les utilisateurs
* L’authentification JWT
* Les profils enfants
* Les produits scannés
* La récupération de données OpenFoodFacts
* Les histoires audio générées par IA
* La persistance des données dans une base SQLite

---

# Arborescence

```text
backend/
├── core/
│   └── security.py
├── db/
│   ├── __init__.py
│   ├── database.py
│   └── pandoo.db
├── routers/
│   ├── children.py
│   ├── products.py
│   ├── stories.py
│   └── users.py
├── services/
│   ├── stories_audio/
│   ├── api.py
│   ├── api_test.py
│   ├── test_ollama.py
│   └── testllm.py
├── .gitignore
├── __init__.py
├── main.py
├── models.py
├── requirements.txt
├── schemas.py
└── testAPI.py
```

---

# Fichiers principaux

## `main.py`

Point d’entrée de l’API FastAPI.

### Responsabilités

* Création de l’application FastAPI
* Configuration du CORS
* Enregistrement des routers
* Vérification du bon fonctionnement de l’API
* Test de connexion à la base de données

### Routes

```http
GET /
GET /test-db
```

---

## `models.py`

Définit les modèles SQLAlchemy représentant les tables de la base de données.

### Modèle `User`

Table : `utilisateurs`

#### Champs

* id
* name
* email
* password_hash
* google_id

#### Relations

* Un utilisateur possède plusieurs enfants

---

### Modèle `Child`

Table : `enfants`

#### Champs

* id
* name
* birthdate
* allergenes
* id_parent

#### Relations

* Appartient à un utilisateur
* Possède plusieurs produits
* Possède plusieurs histoires

---

### Modèle `Product`

Table : `produits`

#### Champs

* id
* barcode
* type
* name
* brand
* calories
* calcium
* proteins
* lipids
* salt
* id_child

#### Relations

* Appartient à un enfant

---

### Modèle `Story`

Table : `histoires`

#### Champs

* id
* url_mp3
* script
* id_child

#### Relations

* Appartient à un enfant

---

## `schemas.py`

Contient les schémas Pydantic utilisés pour la validation des données.

### Utilisateurs

* `UserCreate`
* `UserRead`
* `UserLogin`
* `Token`
* `TokenData`
* `FirebaseTokenRequest`

### Enfants

* `ChildCreate`
* `ChildRead`

### Produits

* `ProductCreate`
* `ProductRead`
* `ProductScan`

### Histoires

* `StoryCreate`
* `StoryRead`

⚠️ Les schémas des histoires sont actuellement incomplets.

---

## `requirements.txt`

Liste des dépendances Python.

### Principales bibliothèques

* fastapi
* uvicorn
* SQLAlchemy
* pydantic
* python-jose
* passlib
* argon2-cffi
* openfoodfacts
* openai
* elevenlabs
* firebase_admin
* python-dotenv
* httpx
* aiofiles
* requests

### Installation

```bash
pip install -r requirements.txt
```

---

## `.gitignore`

Permet d’exclure :

* environnements virtuels
* caches Python
* fichiers temporaires
* secrets

---

## `__init__.py`

Transforme le dossier backend en package Python.

---

## `testAPI.py`

Script de test manuel destiné à vérifier certaines fonctionnalités de l’API.

---

# Dossier `core`

## `core/security.py`

Gestion de l’authentification et de la sécurité.

### Fonctions principales

#### `normalize_password(password)`

Pré-hash SHA-256 du mot de passe.

#### `hash_password(password)`

Hash du mot de passe avec Argon2.

#### `verify_password(plain_password, hashed_password)`

Validation du mot de passe.

#### `create_access_token(subject, expires_delta=60)`

Création d’un token JWT contenant :

* sub
* exp
* type

#### `get_current_user()`

Permet :

1. De récupérer le token JWT
2. De le décoder
3. De retrouver l’utilisateur
4. De sécuriser les routes privées

---

# Dossier `db`

## `db/database.py`

Configuration SQLAlchemy.

### Responsabilités

* Création du moteur SQLite
* Création des sessions
* Création automatique des tables
* Fourniture de la dépendance `get_db()`

### Base utilisée

```text
backend/db/pandoo.db
```

---

## `db/pandoo.db`

Base SQLite locale.

Contient :

* utilisateurs
* enfants
* produits
* histoires

---

## `db/__init__.py`

Initialisation du package base de données.

---

# Dossier `routers`

## `routers/users.py`

Gestion des utilisateurs et de l’authentification.

### Routes

```http
POST /users/signup
POST /users/signin
GET /users/
GET /users/me
```

### `/users/signup`

Création d’un utilisateur :

1. Vérification de l’email
2. Hash du mot de passe
3. Création utilisateur
4. Génération JWT

### `/users/signin`

Connexion :

1. Vérification email
2. Vérification mot de passe
3. Retour du JWT

### `/users/`

Liste des utilisateurs.

⚠️ Non protégée actuellement.

### `/users/me`

Retourne l’utilisateur connecté.

---

## `routers/children.py`

Gestion des enfants.

### Routes

```http
POST /children/
GET /children/
PUT /children/{child_id}
DELETE /children/{child_id}
```

### Fonctionnalités

* Création d’un enfant
* Consultation des enfants du parent connecté
* Modification
* Suppression

⚠️ Bug identifié :

Le code modifie `child.age` alors que le modèle utilise `birthdate`.

---

## `routers/products.py`

Gestion des produits.

### Routes

```http
POST /products/
GET /products/child/{id_child}
POST /products/scan
```

### `/products/scan`

Récupération OpenFoodFacts.

Données retournées :

* barcode
* type
* name
* brand
* calories
* calcium
* proteins
* lipids
* salt

### `/products/`

Ajout d’un produit associé à un enfant.

### `/products/child/{id_child}`

Liste des produits d’un enfant.

---

## `routers/stories.py`

Gestion des histoires.

### Routes

```http
POST /stories/{id_child}
GET /stories/{id_child}
```

### Fonctionnalités

* Création d’une histoire
* Consultation des histoires d’un enfant

⚠️ Les schémas Pydantic associés sont encore incomplets.

---

# Dossier `services`

## `services/api.py`

Service de génération d’histoire via Ollama.

### Fonctionnement

1. Génération d’un texte avec Llama 3
2. Conversion en audio via gTTS
3. Sauvegarde dans `stories_audio`
4. Retour du chemin du fichier

### Fonction principale

```python
generate_story()
```

---

## `services/api_test.py`

Version expérimentale utilisant OpenAI.

### Fonctionnement

* GPT-4.1-mini pour le texte
* GPT-4o-audio-preview pour l’audio
* Sauvegarde MP3

### Fonction

```python
generate_story(id_child, voice="alloy")
```

⚠️ Ce fichier agit actuellement comme un script de test.

---

## `services/test_ollama.py`

Tests de génération de texte avec Ollama.

---

## `services/testllm.py`

Tests expérimentaux de modèles de langage.

---

## `services/stories_audio/`

Contient les fichiers audio générés.

Exemples :

```text
stories_audio/
├── story_1.mp3
├── story_2.mp3
└── ...
```

---

# Fonctionnement global

```text
Utilisateur
    │
    ▼
Inscription / Connexion
    │
    ▼
JWT
    │
    ▼
Création d'enfants
    │
    ▼
Scan produit
    │
    ▼
OpenFoodFacts
    │
    ▼
Analyse nutritionnelle
    │
    ▼
Enregistrement du produit
    │
    ▼
Génération d'histoire IA
    │
    ▼
Sauvegarde SQLite
```

---

# Lancement du projet

## Création de l’environnement

```bash
python -m venv .venv
```

## Activation

### Linux / macOS

```bash
source .venv/bin/activate
```

### Windows

```bash
.venv\Scripts\activate
```

## Installation

```bash
pip install -r requirements.txt
```

## Démarrage

```bash
uvicorn main:app --reload
```

API :

```text
http://127.0.0.1:8000
```

Documentation Swagger :

```text
http://127.0.0.1:8000/docs
```

---

# Variables d’environnement

Créer un fichier `.env` :

```env
SECRET_KEY=change-me
API_KEY_OPEN_AI=your-openai-api-key
```

---

# Améliorations recommandées

* Sécuriser `/users/`
* Compléter `StoryCreate`
* Compléter `StoryRead`
* Corriger la gestion de `birthdate`
* Ajouter Alembic
* Ajouter PostgreSQL
* Ajouter des tests Pytest
* Ajouter un `.env.example`
* Ignorer les fichiers audio générés
* Ignorer la base SQLite en production

---

# Technologies utilisées

* Python
* FastAPI
* SQLAlchemy
* SQLite
* Pydantic
* JWT
* Argon2
* OpenFoodFacts
* OpenAI
* Ollama
* gTTS
* Uvicorn
