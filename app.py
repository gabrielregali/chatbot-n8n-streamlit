import streamlit as st
import requests
import json # Agregamos esta importación por si hay que manejar errores específicos

# *****************************************************************
# RECUERDA: PEGAR TU URL DEL WEBHOOK DE N8N AQUÍ
# *****************************************************************
N8N_WEBHOOK_URL = "https://gabiregali.app.n8n.cloud/webhook/24a20510-8c87-47fb-b4f9-5b7360df0328/chat" 
# NOTA: Esta URL debe ser la misma que usaste y que funciona.

# --- Configuración y Título ---
st.set_page_config(page_title="Chatbot RAG con n8n", layout="centered")
st.title("🤖 Chatbot RAG")
st.caption("Conectado al workflow de n8n.")

# Inicializar historial de chat
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "¡Hola! ¿En qué puedo ayudarte? Mi información proviene de tus documentos."}]

# Mostrar mensajes anteriores
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])


# --- Función para Conectarse a n8n (Limpia) ---

def call_n8n_webhook(prompt):
    """Llama al webhook de n8n con el prompt del usuario."""
    try:
        # 1. Preparar y enviar la solicitud
        # Aseguramos que la clave 'prompt' coincida con la variable que el Agente AI está leyendo en n8n.
        payload = {"prompt": prompt}
        response = requests.post(N8N_WEBHOOK_URL, json=payload)
        response.raise_for_status() 

        # 2. Intentar parsear el JSON
        try:
            response_json = response.json()
            
            # Buscamos la clave 'response', que es la que configuramos en el Respond to Webhook
            if 'response' in response_json:
                return response_json['response']
            else:
                return f"Error: n8n respondió, pero no se encontró la clave 'response' en el JSON." 
                
        except json.JSONDecodeError:
            # Si n8n no responde con un JSON válido
            return f"Error: n8n no envió un JSON válido. Respuesta de texto: {response.text}"

    except requests.exceptions.RequestException as e:
        # Error de red o código de estado HTTP (4xx o 5xx)
        return f"Error de conexión con n8n. Detalle: {e}"


# --- Lógica de la Interfaz ---

if prompt := st.chat_input("Escribe tu pregunta aquí..."):

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.spinner("🤖 El chatbot está buscando la información..."):
        full_response = call_n8n_webhook(prompt)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.chat_message("assistant").write(full_response)
