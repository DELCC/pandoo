from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
import json
from datetime import date 

from schemas import ProductCreate, ProductRead
# Importation de ScanHistory en plus
from models import Product, Child, ScanHistory 
from db.database import get_db

# --- IMPORTATION DU CERVEAU DEPUIS MAIN ---
from main import nutri_db 

router = APIRouter(prefix='/products', tags=["Products"])

# --- FONCTION D'ANALYSE PANDOO ---
def generer_analyse_pandoo(product, age_enfant: int):
    # 1. Déterminer la tranche d'âge
    if age_enfant <= 3: tranche = "1-3_ans"
    elif age_enfant <= 6: tranche = "4-6_ans"
    else: tranche = "7-10_ans"
    
    # 2. Récupération des données du JSON
    seuils = nutri_db.get("anc_enfants", {}).get(tranche, {})
    dictionnaire = nutri_db.get("dictionnaire_pedagogique", {})
    
    analyse = {
        "pandoo_advice": "Analyse terminée !",
        "tips": [],
        "alerts": []
    }

    # Analyse du Calcium
    cal_val = product.calcium if product.calcium else 0
    if cal_val >= dictionnaire.get("calcium", {}).get("seuil_riche", 0.12):
        msg = seuils.get("labels", {}).get("calcium", "C'est bon pour tes os !")
        analyse["tips"].append(f"{msg}")

    # Analyse du Sucre (Glucides dans ton modèle)
    glu_val = product.glucides if product.glucides else 0
    if glu_val >= dictionnaire.get("sucres", {}).get("seuil_alerte", 15.0):
        analyse["alerts"].append(f"{dictionnaire.get('sucres', {}).get('explication', '')}")
    
    return analyse

# --- ROUTE POUR ENREGISTRER UN PRODUIT ---
@router.post("/", response_model=None)
def add_products(id_child: int, product: ProductCreate, db: Session = Depends(get_db)):
    # 1. Vérification si l'enfant existe
    child = db.query(Child).filter(Child.id == id_child).first()

    if not child:
        raise HTTPException(
            status_code=404,
            detail="Enfant non trouvé"
        )

    # --- CALCUL DE L'ÂGE DYNAMIQUE ---
    today = date.today()
    age_calcule = today.year - child.birthdate.year - ((today.month, today.day) < (child.birthdate.month, child.birthdate.day))

    try:
        # 2. LOGIQUE ANTI-DOUBLON DU PRODUIT GLOBAL (Par Code-barres)
        existing_product = db.query(Product).filter(
            Product.barcode == product.barcode
        ).first()

        if existing_product:
            print(f"⚠️ Produit global déjà existant : {product.name}")
            target_product = existing_product
        else:
            # Création du nouveau produit unique s'il n'existe pas dans le catalogue
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

        # 3. ENREGISTREMENT DU SCAN DANS L'HISTORIQUE (Lien Enfant/Parent)
        # On vérifie si cet enfant précis n'a pas déjà scanné ce produit aujourd'hui (Optionnel mais évite les doublons d'historique identiques)
        existing_scan = db.query(ScanHistory).filter(
            ScanHistory.id_child == id_child,
            ScanHistory.id_product == target_product.id,
            ScanHistory.scan_date == today
        ).first()

        if not existing_scan:
            new_scan = ScanHistory(
                id_parent=child.id_parent, # Récupéré de manière sécurisée via l'enfant
                id_child=id_child,
                id_product=target_product.id,
                scan_date=today
            )
            db.add(new_scan)
            db.commit()
            print(f"✅ Scan enregistré dans l'historique de l'enfant ID {id_child}")

        # --- GÉNÉRATION DE L'ANALYSE ---
        pandoo_result = generer_analyse_pandoo(target_product, age_calcule)
        
        return {
            "product": target_product,
            "analysis": pandoo_result
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur BDD : {str(e)}")

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
            "id_child": 0 # Renvoyé à 0 ou valeur par défaut car le produit est maintenant global
        })
    
    return JSONResponse(
        content=products_list,
        media_type="application/json; charset=utf-8"
    )

# --- VOIR LES PRODUITS D'UN ENFANT PRÉCIS ---
@router.get("/child/{id_child}", response_model=List[ProductRead])
def get_products_by_child(id_child: int, db: Session = Depends(get_db)):
    # On passe par la table ScanHistory pour récupérer uniquement les scans de cet enfant
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