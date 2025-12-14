import streamlit as st
import requests

# *****************************************************************
# RECUERDA: PEGAR TU URL DEL WEBHOOK DE N8N AQUÍ
# *****************************************************************
N8N_WEBHOOK_URL = "https://gabiregali.app.n8n.cloud/webhook/24a20510-8c87-47fb-b4f9-5b7360df0328/chat" 

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


# --- Función para Conectarse a n8n ---

def call_n8n_webhook(prompt):
    try:
        payload = {"prompt": prompt}
        response = requests.post(N8N_WEBHOOK_URL, json=payload)
        response.raise_for_status() 

        try:
            response_json = response.json()
            # Ajusta esta clave 'response' si tu nodo final en n8n usa otro nombre
            return response_json.get('response', 'Error: n8n respondió, pero la clave JSON es incorrecta.') 
        except requests.exceptions.JSONDecodeError:
            return response.text

    except requests.exceptions.RequestException as e:
        return f"Error de conexión con n8n. Detalle: {e}"


# --- Lógica de la Interfaz ---

if prompt := st.chat_input("Escribe tu pregunta aquí..."):

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.spinner("🤖 El chatbot está buscando la información..."):
        full_response = call_n8n_webhook(prompt)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.chat_message("assistant").write(full_response)