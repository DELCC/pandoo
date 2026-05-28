from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from schemas import ProductCreate, ProductRead, ProductScan
from models import Product, Child, User
from db.database import get_db
from core.security import get_current_user # Import de la dépendance
import openfoodfacts

router = APIRouter(prefix='/products', tags=["Products"])

api = openfoodfacts.API(user_agent="MonAppPython/1.0")

@router.post("/", response_model=ProductRead)
def add_products(
    id_child: int, 
    product: ProductCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # On récupère l'utilisateur connecté
):
    """
    Ajoute un produit pour un enfant, après avoir vérifié 
    que l'enfant appartient bien à l'utilisateur connecté.
    """
    
    # 1. On cherche l'enfant MAIS on filtre par l'ID du parent connecté
    child = db.query(Child).filter(
        Child.id == id_child, 
        Child.id_parent == current_user.id
    ).first()

    # Si l'enfant n'existe pas ou n'appartient pas au parent, on bloque
    if not child:
        raise HTTPException(
            status_code=404,
            detail="Enfant non trouvé ou vous n'avez pas l'autorisation pour cet enfant"
        )

    # 2. Création du produit lié à l'enfant validé
    new_product = Product(
        barcode=product.barcode,
        type=product.type,
        name=product.name,
        brand=product.brand,
        calories=product.calories,
        calcium=product.calcium,
        proteins=product.proteins,
        lipids=product.lipids,
        salt=product.salt,
        id_child=child.id
    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product

@router.get("/child/{id_child}", response_model=list[ProductRead])
def get_child_products(
    id_child: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Récupère les produits d'un enfant seulement si le parent est propriétaire
    """
    # Vérification de la propriété de l'enfant
    child = db.query(Child).filter(
        Child.id == id_child, 
        Child.id_parent == current_user.id
    ).first()

    if not child:
        raise HTTPException(status_code=404, detail="Accès refusé ou enfant introuvable")

    return db.query(Product).filter(Product.id_child == id_child).all()

@router.post("/scan", response_model=ProductScan)
def scan_product(barcode: str):
    try:
        product = api.product.get(
            barcode,
            fields=[
                "code",
                "product_name",
                "brands",
                "categories_tags",
                "nutriments",
            ],
        )
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Impossible d'atteindre l'API Open Food Facts"
        )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Produit non trouvé"
        )

    nutriments = product.get("nutriments", {})
    categories = product.get("categories_tags") or []

    return {
        "barcode": product.get("code") or barcode,
        "type": categories[0] if categories else None,
        "name": product.get("product_name"),
        "brand": product.get("brands"),
        "calories": nutriments.get("energy-kcal_100g"),
        "calcium": nutriments.get("calcium_100g"),
        "proteins": nutriments.get("proteins_100g"),
        "lipids": nutriments.get("fat_100g"),
        "salt": nutriments.get("salt_100g"),
    }