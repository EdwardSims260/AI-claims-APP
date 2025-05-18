import streamlit as st
from PIL import Image, ImageDraw
from fpdf import FPDF
import datetime
import hashlib
import uuid
import os

# Initialize directories
os.makedirs("images", exist_ok=True)

# App Configuration
st.set_page_config(
    page_title="CAI Digital - Constatazione Amichevole",
    page_icon="🚗",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .section {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
    }
    .header {
        color: #2E86C1;
        margin-bottom: 30px;
    }
    .required:after {
        content: " *";
        color: red;
    }
    .reference-box {
        background-color: #f0f8ff;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

def create_vehicle_template():
    """Create placeholder vehicle image"""
    img = Image.new('RGB', (300, 200), color=(240, 240, 240))
    d = ImageDraw.Draw(img)
    d.rectangle([50, 50, 250, 150], outline='black', width=2)
    d.text((100, 80), "VEHICLE TEMPLATE", fill='black')
    return img

def load_vehicle_image():
    """Load or create vehicle template image"""
    try:
        return Image.open("images/vehicle_template.png")
    except FileNotFoundError:
        return create_vehicle_template()

def generate_reference_number():
    """Generate unique reference number"""
    timestamp = str(datetime.datetime.now().timestamp())
    unique_id = str(uuid.uuid4())
    return hashlib.sha256((timestamp + unique_id).encode()).hexdigest()[:12].upper()

# Initialize session state
if 'form_data' not in st.session_state:
    st.session_state.form_data = {}
    st.session_state.reference_number = None
    st.session_state.reference_locked = False

# Main App
st.title("📝 CAI Digital - Constatazione Amichevole")
st.markdown("Compila il modulo digitale e genera il documento pronto per l'assicurazione")

# Reference Number Section
with st.container():
    st.subheader("Numero di Riferimento Condiviso")
    
    if not st.session_state.reference_locked:
        col1, col2 = st.columns([3,1])
        with col1:
            reference_action = st.radio("Scegli opzione riferimento:",
                                      ["Genera nuovo numero", "Inserisci numero esistente"])
            
            if reference_action == "Genera nuovo numero":
                if st.button("Genera Numero"):
                    st.session_state.reference_number = generate_reference_number()
                    st.session_state.reference_locked = True
                    st.rerun()
                    
            else:
                existing_ref = st.text_input("Inserisci numero riferimento esistente", 
                                           max_chars=12).strip().upper()
                if existing_ref:
                    if len(existing_ref) == 12 and all(c.isalnum() for c in existing_ref):
                        if st.button("Conferma Numero"):
                            st.session_state.reference_number = existing_ref
                            st.session_state.reference_locked = True
                            st.rerun()
                    else:
                        st.warning("Il numero di riferimento deve essere di 12 caratteri alfanumerici")
    
    if st.session_state.reference_number:
        st.markdown(f"""
        <div class="reference-box">
            <h4>Numero di Riferimento:</h4>
            <h2>{st.session_state.reference_number}</h2>
            <p>Condividi questo numero con l'altro conducente per collegare i vostri rapporti.</p>
            <p><strong>Questo numero può essere utilizzato solo da 2 parti.</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔓 Sblocca e modifica numero"):
            st.session_state.reference_locked = False
            st.rerun()

# Main Form
if st.session_state.reference_number:
    # Section 1: Basic Incident Information
    with st.expander("1. Informazioni Base sull'Incidente", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.form_data['data_incidente'] = st.date_input("Data incidente", datetime.date.today())
            st.session_state.form_data['luogo_comune'] = st.text_input("Comune")
            st.session_state.form_data['luogo_provincia'] = st.text_input("Provincia")
            st.session_state.form_data['luogo_via'] = st.text_input("Via e numero")
        
        with col2:
            st.session_state.form_data['feriti'] = st.radio("Feriti (anche lievi)", ["No", "Sì"])
            st.session_state.form_data['danni_veicoli_extra'] = st.radio("Danni ad altri veicoli", ["No", "Sì"])
            st.session_state.form_data['danni_oggetti'] = st.radio("Danni ad oggetti", ["No", "Sì"])

    # Section 2: Vehicle Information
    with st.expander("2. Informazioni sul tuo Veicolo"):
        st.subheader("Proprietario/Assicurato")
        st.session_state.form_data['cognome'] = st.text_input("Cognome (stampatello)")
        st.session_state.form_data['nome'] = st.text_input("Nome")
        st.session_state.form_data['cf'] = st.text_input("Codice Fiscale/Partita IVA")
        
        st.subheader("Veicolo")
        st.session_state.form_data['marca'] = st.text_input("Marca/Tipo")
        st.session_state.form_data['targa'] = st.text_input("Numero di targa/telaio")
        
        st.subheader("Assicurazione")
        st.session_state.form_data['compagnia'] = st.text_input("Compagnia assicurativa")
        st.session_state.form_data['polizza'] = st.text_input("Numero polizza")

    # Section 3: Other Vehicle Information
    with st.expander("3. Informazioni sull'Altro Veicolo"):
        st.session_state.form_data['altro_cognome'] = st.text_input("Cognome conducente (stampatello)", key="altro_cognome")
        st.session_state.form_data['altro_nome'] = st.text_input("Nome conducente", key="altro_nome")
        st.session_state.form_data['altro_marca'] = st.text_input("Marca/Tipo veicolo", key="altro_marca")
        st.session_state.form_data['altro_targa'] = st.text_input("Numero di targa/telaio", key="altro_targa")
        st.session_state.form_data['altro_compagnia'] = st.text_input("Compagnia assicurativa", key="altro_compagnia")

    # Section 4: Accident Details
    with st.expander("4. Dettagli Incidente"):
        st.subheader("Punti di urto")
        col1, col2 = st.columns(2)
        
        vehicle_img = load_vehicle_image()
        
        with col1:
            st.image(vehicle_img, caption="Il tuo veicolo", width=300)
            st.session_state.form_data['danni'] = st.text_area("Danni visibili al tuo veicolo")
        
        with col2:
            st.image(vehicle_img, caption="Altro veicolo", width=300)
            st.session_state.form_data['altro_danni'] = st.text_area("Danni visibili all'altro veicolo")
        
        st.subheader("Circostanze")
        options = [
            "Riparte dopo sosta", "Apre una portiera", "Stava parcheggiando",
            "Usciva da parcheggio", "Entrava in parcheggio", "Tamponamento",
            "Cambio di corsia", "Sorpasso", "Girava a destra", "Girava a sinistra"
        ]
        st.session_state.form_data['circostanze'] = st.multiselect("Seleziona le circostanze applicabili", options)

    # Section 5: Photo Upload
    with st.expander("5. Foto dell'Incidente"):
        uploaded_files = st.file_uploader("Carica foto dell'incidente (max 5)", 
                                        type=["jpg", "png", "jpeg"],
                                        accept_multiple_files=True)
        
        if uploaded_files:
            st.session_state.form_data['foto'] = []
            cols = st.columns(min(3, len(uploaded_files)))
            for i, uploaded_file in enumerate(uploaded_files):
                with cols[i % 3]:
                    img = Image.open(uploaded_file)
                    st.image(img, caption=f"Foto {i+1}", use_column_width=True)
                    st.session_state.form_data['foto'].append(img)

    # Section 6: Generate PDF
    if st.button("🖨️ Genera Documento CAI Completo"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        
        # Add content to PDF
        pdf.cell(200, 10, txt=f"RIFERIMENTO: {st.session_state.reference_number}", ln=1, align='C')
        pdf.cell(200, 10, txt="CONSTATAZIONE AMICHEVOLE DI INCIDENTE", ln=1, align='C')
        
        # Add form data
        pdf.cell(200, 10, txt=f"Data incidente: {st.session_state.form_data['data_incidente']}", ln=1)
        pdf.cell(200, 10, txt=f"Luogo: {st.session_state.form_data['luogo_via']}, {st.session_state.form_data['luogo_comune']} ({st.session_state.form_data['luogo_provincia']})", ln=1)
        
        # Add vehicle info
        pdf.cell(200, 10, txt="Veicolo 1:", ln=1)
        pdf.cell(200, 10, txt=f"Proprietario: {st.session_state.form_data['cognome']} {st.session_state.form_data['nome']}", ln=1)
        pdf.cell(200, 10, txt=f"Veicolo: {st.session_state.form_data['marca']} - {st.session_state.form_data['targa']}", ln=1)
        
        pdf.cell(200, 10, txt="Veicolo 2:", ln=1)
        pdf.cell(200, 10, txt=f"Conducente: {st.session_state.form_data['altro_cognome']} {st.session_state.form_data['altro_nome']}", ln=1)
        pdf.cell(200, 10, txt=f"Veicolo: {st.session_state.form_data['altro_marca']} - {st.session_state.form_data['altro_targa']}", ln=1)
        
        # Add photos (first 3 only)
        if 'foto' in st.session_state.form_data and st.session_state.form_data['foto']:
            pdf.add_page()
            pdf.cell(200, 10, txt="Foto dell'incidente:", ln=1)
            for i, img in enumerate(st.session_state.form_data['foto'][:3]):
                img_path = f"temp_img_{i}.jpg"
                img.save(img_path)
                pdf.image(img_path, x=10, y=20+i*60, w=180)
                os.remove(img_path)  # Clean up temp file
        
        # Download button
        pdf_bytes = pdf.output(dest='S').encode('latin1')
        st.download_button(
            label="📥 Scarica CAI Completo",
            data=pdf_bytes,
            file_name=f"CAI_{st.session_state.reference_number}.pdf",
            mime="application/pdf"
        )
        st.success("Documento generato con successo!")
else:
    st.warning("Per continuare, genera o inserisci un numero di riferimento")
