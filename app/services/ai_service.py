from google import genai
from app.core.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

async def generate_story(child_name: str, product_name: str, child_age: int, product_category: str) -> str:
    prompt = f"""
    Écris une histoire courte pour un enfant de {child_age} ans dont il est le héros.
    Le prénom de l'enfant est {child_name}.
    Le thème est : {product_category}.
    
    L'histoire commence par le scan de {product_name} dans le monde réel qui devient magique.
    L'histoire doit durer environ 1 minute à la lecture (entre 150 et 200 mots, adapte selon l'âge {child_age} ans).
    Le ton doit être ludique, éducatif et bienveillant.
    Si le produit est sucré, évite de promouvoir la surconsommation.
    {child_name} doit être le héros de l'aventure.
    """
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=prompt
    )
    return response.text

async def generate_quiz(product_name: str, child_age: int) -> str:
    prompt = f"""
    Génère un quiz de 3 questions simples et amusantes pour un enfant de {child_age} ans.
    Le quiz doit porter sur le produit : {product_name} et sur la nutrition en général.
    Chaque question doit avoir 3 choix de réponses (A, B, C) avec la bonne réponse indiquée.
    Adapte le vocabulaire à l'âge de l'enfant.
    Maximum 150 mots.
    """
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=prompt
    )
    return response.text