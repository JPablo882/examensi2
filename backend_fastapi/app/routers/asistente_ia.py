from fastapi import APIRouter, Query
import httpx
import os
router = APIRouter(prefix="/api/asistente", tags=["Asistente IA"])

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

@router.get("/consultar")
async def consultar_asistente(mensaje: str = Query(...)):
    print(f"📨 Mensaje: {mensaje}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                GROQ_URL,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": "Eres un asistente útil de EmergAuto. Responde en español."},
                        {"role": "user", "content": mensaje}
                    ],
                    "max_tokens": 300
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                respuesta = data["choices"][0]["message"]["content"]
            else:
                respuesta = f"Error: {response.status_code}"
    except Exception as e:
        print(f"Error: {e}")
        respuesta = "Lo siento, no pude procesar tu consulta."
    
    return {"respuesta": respuesta}