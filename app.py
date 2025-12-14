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
            
            # === CÓDIGO DE DEBUGGING AÑADIDO ===
            # Muestra el JSON COMPLETO en la interfaz de Streamlit para el usuario
            st.warning("⚠️ DEBUG: Respuesta JSON COMPLETA de n8n:")
            st.json(response_json)
            # ==================================

            # Ajusta esta clave 'response' si tu nodo final en n8n usa otro nombre
            
            # --- Lógica de Retorno ---
            # 1. Intenta con la clave 'response'
            if 'response' in response_json:
                return response_json['response']
            
            # 2. Intenta con la clave 'answer' (si la primera falla)
            elif 'answer' in response_json:
                return response_json['answer']
                
            # 3. Intenta con la clave 'Output' (si las dos primeras fallan)
            elif 'Output' in response_json:
                return response_json['Output']

            # Si ninguna clave estándar funciona, muestra el error y el JSON completo arriba
            return 'ERROR: No se encontró la clave de respuesta esperada (response, answer o Output) en el JSON de n8n. Por favor, revisa el DEBUG INFO arriba.'
            
        except requests.exceptions.JSONDecodeError:
            # Si n8n no responde con un JSON válido
            st.error("Error: n8n respondió, pero el cuerpo no es un JSON válido.")
            return f"Respuesta de texto crudo: {response.text}"

    except requests.exceptions.RequestException as e:
        # Error de red o código de estado HTTP (ej: 404, 500)
        return f"Error de conexión con n8n. Detalle: {e}"


# --- Lógica de la Interfaz ---

if prompt := st.chat_input("Escribe tu pregunta aquí..."):

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.spinner("🤖 El chatbot está buscando la información..."):
        full_response = call_n8n_webhook(prompt)

    st.session_state.messages.append({"role": "assistant", "content": full_response})

    st.chat_message("assistant").write(full_response)
