from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
import json
import os 
from datetime import date 

from schemas import ProductCreate, ProductRead
from models import Product, Child, ScanHistory 
from db.database import get_db

# --- IMPORTATION DU SERVICE GEMINI CORRIGÉE ---
from google import genai

# Récupération sécurisée de ta clé d'API
GEMINI_API_KEY = "AIzaSyCPgVTXC00bnqkchi-RygJ1eF-BruZPjXg"
client = genai.Client(api_key=GEMINI_API_KEY)

# --- FONCTION DE GÉNÉRATION DE RÉCOMPENSE UNIQUE (OPTIMISÉE QUOTA) ---
async def generate_reward(child_name: str, product_name: str, child_age: int, product_category: str) -> dict:
    prompt = f"""
    Tu es un assistant pour enfants. Crée deux éléments distincts pour un enfant de {child_age} ans nommé {child_name}.
    Le thème est le produit scanné : {product_name} (Catégorie: {product_category}).

    1. HISTOIRE : Écris une histoire courte (150-200 mots) dont {child_name} est le héros. Le scan du produit déclenche une aventure magique. Le ton est bienveillant, éducatif, et n'incite pas à la surconsommation.
    2. QUIZ : Génère un quiz de 3 questions simples (A, B, C) avec la réponse indiquée.

    Tu dois ABSOLUMENT séparer l'histoire et le quiz avec la balise exacte [SEPARATEUR] sur une nouvelle ligne.
    """
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=prompt
    )
    
    texte_complet = response.text
    story = texte_complet
    quiz = ""
    
    if "[SEPARATEUR]" in texte_complet:
        parties = texte_complet.split("[SEPARATEUR]")
        story = parties[0].strip()
        quiz = parties[1].strip()
        
    return {"story": story, "quiz": quiz}

# --- IMPORTATION DU CERVEAU DEPUIS MAIN ---
from main import nutri_db 

router = APIRouter(prefix='/products', tags=["Products"])

# --- FONCTION D'ANALYSE PANDOO ---
def generer_analyse_pandoo(product, age_enfant: int):
    if age_enfant <= 3: tranche = "1-3_ans"
    elif age_enfant <= 6: tranche = "4-6_ans"
    else: tranche = "7-10_ans"
    
    seuils = nutri_db.get("anc_enfants", {}).get(tranche, {})
    dictionnaire = nutri_db.get("dictionnaire_pedagogique", {})
    
    analyse = {
        "pandoo_advice": "Analyse terminée !",
        "tips": [],
        "alerts": []
    }

    cal_val = product.calcium if product.calcium else 0
    if cal_val >= dictionnaire.get("calcium", {}).get("seuil_riche", 0.12):
        msg = seuils.get("labels", {}).get("calcium", "C'est bon pour tes os !")
        analyse["tips"].append(f"{msg}")

    glu_val = product.glucides if product.glucides else 0
    if glu_val >= dictionnaire.get("sucres", {}).get("seuil_alerte", 15.0):
        analyse["alerts"].append(f"{dictionnaire.get('sucres', {}).get('explication', '')}")
    
    return analyse

# --- ROUTE POUR ENREGISTRER UN PRODUIT ---
@router.post("/", response_model=None)
async def add_products(id_child: int, product: ProductCreate, db: Session = Depends(get_db)):
    child = db.query(Child).filter(Child.id == id_child).first()

    if not child:
        raise HTTPException(
            status_code=404,
            detail="Enfant non trouvé"
        )

    today = date.today()
    age_calcule = today.year - child.birthdate.year - ((today.month, today.day) < (child.birthdate.month, child.birthdate.day))

    try:
        existing_product = db.query(Product).filter(
            Product.barcode == product.barcode
        ).first()

        if existing_product:
            print(f"⚠️ Produit global déjà existant : {product.name}")
            target_product = existing_product
        else:
            target_product = Product(
                barcode=product.barcode,
                type=product.type,
                name=product.name,
                brand=product.brand,
                calories=product.calories,
                glucides=product.glucides, 
                calcium=product.calcium,
                proteins=product.proteins,
                lipids=product.lipids,
                salt=product.salt
            )
            db.add(target_product)
            db.commit()
            db.refresh(target_product)
            print(f"✨ Nouveau produit ajouté au catalogue : {target_product.name}")

        existing_scan = db.query(ScanHistory).filter(
            ScanHistory.id_child == id_child,
            ScanHistory.id_product == target_product.id,
            ScanHistory.scan_date == today
        ).first()

        if not existing_scan:
            new_scan = ScanHistory(
                id_parent=child.id_parent, 
                id_child=id_child,
                id_product=target_product.id,
                scan_date=today
            )
            db.add(new_scan)
            db.commit()
            print(f"✅ Scan enregistré dans l'historique de l'enfant ID {id_child}")

        total_scans = db.query(ScanHistory).filter(ScanHistory.id_child == id_child).count()
        print(f"📊 Nombre total de produits scannés par cet enfant : {total_scans}")

        pandoo_result = generer_analyse_pandoo(target_product, age_calcule)
        
        recompense_histoire = ""
        recompense_quiz = ""
        
        if total_scans > 0 and total_scans % 5 == 0:
            try:
                rewards = await generate_reward(
                    child_name=child.name,
                    product_name=target_product.name,
                    child_age=age_calcule,
                    product_category=target_product.type if target_product.type else "Aliment"
                )
                recompense_histoire = rewards["story"]
                recompense_quiz = rewards["quiz"]
            except Exception as gemini_err:
                print("⚠️ Quota épuisé ou Erreur Gemini. Utilisation de la récompense locale.")
                
                # Correction des chaînes de caractères pour éviter les bugs d'interprétation Python
                p_name = str(target_product.name)
                c_name = str(child.name)
                
                recompense_histoire = "Incroyable ! C'est le 5ème scan pour l'aventurier " + c_name + " ! En scannant " + p_name + ", une porte magique s'ouvre dans la cuisine. Pandoo le petit panda apparaît en faisant une roulade : Bravo ! Tu as exploré 5 aliments différents. Pour te récompenser, voici ton badge d'Explorateur en Herbe !"
                recompense_quiz = "Quiz Spécial 5 Scans pour " + c_name + " : \nQuestion 1 : Quel super-pouvoir donne le calcium trouvé dans certains de tes 5 aliments ?\nA) Voler dans les airs\nB) Rendre les os et les dents très forts\nC) Devenir invisible"
        else:
            scans_restants = 5 - (total_scans % 5)
            recompense_histoire = f"Encore {scans_restants} scan(s) avant de débloquer ta prochaine histoire magique et ton quiz !"
            recompense_quiz = ""
        
        # Formatage de retour propre en dictionnaire JSON pour FastAPI
        return JSONResponse(
            status_code=200,
            content={
                "product": {
                    "id": target_product.id,
                    "barcode": target_product.barcode,
                    "name": target_product.name,
                    "type": target_product.type,
                    "brand": target_product.brand,
                    "calories": target_product.calories,
                    "glucides": target_product.glucides,
                    "proteins": target_product.proteins,
                    "lipids": target_product.lipids,
                    "salt": target_product.salt,
                    "calcium": target_product.calcium
                },
                "analysis": pandoo_result,
                "reward": {
                    "story": recompense_histoire,
                    "quiz": recompense_quiz
                }
            }
        )
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erreur critique dans la route POST: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur interne : {str(e)}")

# --- VOIR TOUS LES PRODUITS ---
@router.get("/", response_model=List[ProductRead])
def get_all_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    
    products_list = []
    for p in products:
        products_list.append({
            "id": p.id,
            "barcode": p.barcode,
            "name": p.name,
            "type": p.type,
            "brand": p.brand,
            "calories": p.calories,
            "glucides": p.glucides,
            "proteins": p.proteins,
            "lipids": p.lipids,
            "salt": p.salt,
            "calcium": p.calcium,
            "id_child": 0 
        })
    
    return JSONResponse(
        content=products_list,
        media_type="application/json; charset=utf-8"
    )

# --- VOIR LES PRODUITS D'UN ENFANT PRÉCIS ---
@router.get("/child/{id_child}", response_model=List[ProductRead])
def get_products_by_child(id_child: int, db: Session = Depends(get_db)):
    scans = db.query(ScanHistory).filter(ScanHistory.id_child == id_child).all()
    
    products_data = []
    for scan in scans:
        p = scan.product
        products_data.append({
            "id": p.id, 
            "barcode": p.barcode, 
            "name": p.name, 
            "type": p.type, 
            "brand": p.brand, 
            "calories": p.calories,
            "glucides": p.glucides, 
            "proteins": p.proteins, 
            "salt": p.salt,
            "id_child": id_child
        })
    
    return JSONResponse(
        content=products_data,
        media_type="application/json; charset=utf-8"
    )