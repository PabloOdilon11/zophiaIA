from pathlib import Path
import base64
import html
import time

import pandas as pd
import streamlit as st

st.set_page_config(page_title='Zophia Lite', page_icon='🧠', layout='wide')

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_PATH = BASE_DIR / 'dataset' / 'mental_health_social_media_posts.csv'
OUTPUTS_DIR = BASE_DIR / 'outputs'
LOGO_PATH = BASE_DIR / 'assets' / 'zophia_logo.png'

st.markdown('''
<style>
.stApp{background:radial-gradient(circle at 5% 5%,rgba(236,72,153,.10),transparent 25%),radial-gradient(circle at 95% 5%,rgba(124,58,237,.12),transparent 28%),#f8fafc}
.block-container{max-width:1250px;padding-top:1.5rem;padding-bottom:3rem}
.hero{background:linear-gradient(135deg,#5b21b6 0%,#7c3aed 45%,#db2777 100%);border-radius:26px;padding:1.6rem 2rem;color:white;box-shadow:0 18px 50px rgba(91,33,182,.24);margin-bottom:1.3rem}
.hero-grid{display:flex;align-items:center;gap:1.5rem}.hero-logo{width:180px;max-width:28vw;border-radius:18px;box-shadow:0 10px 30px rgba(0,0,0,.18)}
.hero h1{color:white;margin:0;font-size:3rem}.hero p{color:rgba(255,255,255,.92);font-size:1.12rem;margin:.65rem 0 0}.hero-badge{display:inline-block;margin-top:.8rem;padding:.38rem .8rem;border-radius:999px;background:rgba(255,255,255,.18);font-size:.82rem;font-weight:700}
.metric-card,.content-card{background:white;border:1px solid #e5e7eb;border-radius:18px;box-shadow:0 8px 28px rgba(15,23,42,.055)}
.metric-card{min-height:120px;padding:1.1rem}.metric-title{color:#64748b;font-size:.78rem;font-weight:700;text-transform:uppercase}.metric-number{color:#1e293b;font-size:2rem;font-weight:800;margin-top:.2rem}.metric-description{color:#64748b;font-size:.85rem}
.content-card{padding:1.3rem;margin-bottom:1rem}.content-card h3{color:#312e81;margin:0 0 .7rem;font-size:1.15rem}.content-card p{color:#334155;line-height:1.65;margin:0}.content-card ul{color:#334155;line-height:1.65;margin:.2rem 0 0 1.2rem;padding:0}.content-card li{margin-bottom:.35rem}
.source-tag{display:inline-block;background:#f3e8ff;color:#6b21a8;border:1px solid #e9d5ff;border-radius:999px;padding:.42rem .78rem;margin:.2rem .25rem .2rem 0;font-size:.88rem;font-weight:700}
.safety-warning{background:#fff7ed;color:#7c2d12;border:1px solid #fed7aa;border-left:6px solid #f97316;padding:1rem 1.2rem;border-radius:14px;margin-top:1.2rem;line-height:1.6}
.risk-warning{background:#fef2f2;color:#991b1b;border:1px solid #fecaca;border-left:6px solid #dc2626;padding:1rem 1.2rem;border-radius:14px;margin-bottom:1.2rem;line-height:1.6}
div.stButton>button{width:100%;border:none;border-radius:13px;padding:.82rem 1.1rem;font-weight:800;font-size:1rem;background:linear-gradient(90deg,#7c3aed,#db2777);color:white}
[data-testid='stSidebar']{background:linear-gradient(180deg,#111827 0%,#1e1b4b 100%)}[data-testid='stSidebar'] *{color:#f8fafc}#MainMenu,footer{visibility:hidden}
</style>
''', unsafe_allow_html=True)

@st.cache_data
def load_dataset():
    if not DATASET_PATH.exists():
        return None
    try:
        return pd.read_csv(DATASET_PATH)
    except Exception:
        return None

def detect_signs(text):
    t = text.lower()
    signs = []

    groups = {
        "Alterações no sono": ["sleep", "insomnia", "dormir", "sono", "insônia"],
        "Tristeza ou desânimo": [
            "sad", "sadness", "triste", "tristeza", "despair",
            "desespero", "vazio", "vazia"
        ],
        "Sinais relacionados à ansiedade": [
            "anxiety", "anxious", "ansiedade", "ansioso",
            "ansiosa", "panic", "pânico"
        ],
        "Redução de energia ou motivation": [
            "energy", "energia", "motivation", "motivação",
            "bed", "cama", "tired", "cansado", "cansada"
        ],
        "Dificuldade de concentração": [
            "focus", "concentrate", "concentração",
            "concentrar", "attention", "atenção"
        ],
    }

    for sign, keys in groups.items():
        if any(key in t for key in keys):
            signs.append(sign)

    return signs


def detect_positive(text):
    t = text.lower()
    aspects = []

    groups = {
        "Emoções positivas": [
            "feliz", "alegre", "contente", "animado", "animada",
            "happy", "great", "ótimo", "otimo", "incrível", "incrivel"
        ],
        "Sentimento de realização": [
            "consegui", "passei", "ganhei", "conquista", "conquistei",
            "aprovado", "aprovada", "emprego", "estágio", "estagio"
        ],
        "Esperança e motivação": [
            "esperança", "esperanca", "motivado", "motivada",
            "confiante", "empolgado", "empolgada"
        ],
        "Gratidão": [
            "grato", "grata", "gratidão", "gratidao",
            "agradecido", "agradecida"
        ],
    }

    for aspect, keys in groups.items():
        if any(key in t for key in keys):
            aspects.append(aspect)

    return aspects


def detect_risk(text):
    t = text.lower()
    terms = [
        "suicidal", "suicide", "kill myself", "end my life",
        "me matar", "tirar minha vida", "não quero viver",
        "nao quero viver", "acabar com minha vida"
    ]
    return any(term in t for term in terms)


def classify_report(text):
    if detect_risk(text):
        return "risk"

    positive = detect_positive(text)
    negative = detect_signs(text)

    if positive and not negative:
        return "positive"

    if negative:
        return "distress"

    return "neutral"


def render_metric(icon,title,number,desc):
    st.markdown(f"<div class='metric-card'><div style='font-size:1.4rem'>{icon}</div><div class='metric-title'>{title}</div><div class='metric-number'>{number}</div><div class='metric-description'>{desc}</div></div>",unsafe_allow_html=True)

def render_card(title,body):
    st.markdown(f"<div class='content-card'><h3>{title}</h3>{body}</div>",unsafe_allow_html=True)

df=load_dataset()
records=len(df) if df is not None else 0
cats=int(df['tag'].nunique()) if df is not None else 0
missing=int(df.isnull().sum().sum()) if df is not None else 0
avg=round(df['post_content'].astype(str).str.len().mean(),2) if df is not None else 0

with st.sidebar:
    if LOGO_PATH.exists(): st.image(str(LOGO_PATH),width='stretch')
    st.success('Semana 1 concluída')
    st.divider()
    if df is not None:
        st.markdown('### Categorias')
        for cat,count in df['tag'].value_counts().items(): st.write(f'**{cat}:** {int(count)}')
    st.divider(); st.markdown('### Base documental')
    for doc in ['WHO mhGAP','NICE — Depressão','NICE — Ansiedade','Ministério da Saúde','Material do CVV','DSM-5-TR autorizado']:
        st.write(f'✓ {doc}')

logo_html=''
if LOGO_PATH.exists():
    encoded=base64.b64encode(LOGO_PATH.read_bytes()).decode()
    logo_html=f"<img class='hero-logo' src='data:image/png;base64,{encoded}'>"
st.markdown(f"<div class='hero'><div class='hero-grid'>{logo_html}<div><h1>Zophia Lite</h1><p>Assistente inteligente de apoio educacional em saúde mental, planejado com LLM e RAG.</p><span class='hero-badge'>Protótipo funcional • Semana 1</span></div></div></div>",unsafe_allow_html=True)
st.info('Esta ferramenta possui finalidade exclusivamente educacional e não substitui atendimento psicológico, psiquiátrico ou médico.')

st.markdown('## Visão geral do projeto')
a,b,c,d=st.columns(4)
with a: render_metric('📝','Relatos',records,'Registros disponíveis')
with b: render_metric('🏷️','Categorias',cats,'Classes do dataset')
with c: render_metric('✅','Valores ausentes',missing,'Campos incompletos')
with d: render_metric('📏','Tamanho médio',avg,'Caracteres por relato')

analysis_tab,dataset_tab,project_tab=st.tabs(['🔍 Analisar relato','📊 Exploração dos dados','📘 Sobre o projeto'])

with analysis_tab:
    mode=st.radio('Escolha a forma de entrada:',['Digitar um relato','Selecionar um relato do dataset'],horizontal=True)
    text=''
    if mode=='Digitar um relato':
        text=st.text_area('Digite o relato',height=210,placeholder='Conte como você está se sentindo...')
    elif df is None:
        st.error('O dataset não pôde ser carregado.')
    else:
        category=st.selectbox('Filtrar por categoria',['Todas',*sorted(df['tag'].astype(str).unique().tolist())])
        filtered=df if category=='Todas' else df[df['tag']==category]
        idx=st.selectbox('Selecione um relato',filtered.index.tolist(),format_func=lambda i:f"#{df.loc[i,'id']} — {str(df.loc[i,'post_content'])[:75]}...")
        text=str(df.loc[idx,'post_content'])
        st.text_area('Relato selecionado',value=text,height=180,disabled=True)
    analyze=st.button('✨ Analisar relato',width='stretch')

    st.write("")
    inf1,inf2,inf3=st.columns(3,gap='large')
    with inf1:
        render_card('💡 Como funciona nesta etapa','<p>O protótipo identifica palavras-chave e monta uma resposta simulada.</p>')
    with inf2:
        render_card('🔄 Fluxo futuro','<p>Relato → embedding → busca vetorial → documentos → prompt → LLM → resposta.</p>')
    with inf3:
        render_card('🔒 Segurança','<p>O sistema não realiza diagnóstico e não substitui profissionais.</p>')
    if analyze:
        if not text.strip(): st.warning('Digite ou selecione um relato antes de analisar.')
        else:
            p=st.progress(0); msg=st.empty()
            for i,s in enumerate(['Recebendo o relato...','Validando o texto...','Identificando sinais...','Organizando a resposta...','Finalizando...']):
                msg.info(s); p.progress((i+1)*20); time.sleep(.2)
            msg.empty(); p.empty()
            report_type = classify_report(text)
            signs = detect_signs(text)
            positive_aspects = detect_positive(text)
            risk = report_type == "risk"

            st.divider()
            st.markdown("## Resultado da análise simulada")

            if risk:
                st.markdown(
                    "<div class='risk-warning'><strong>🚨 Atenção:</strong> "
                    "o relato contém expressões que podem indicar sofrimento intenso. "
                    "Em uma situação real, busque apoio imediato de uma pessoa de confiança "
                    "e de um serviço de saúde ou emergência.</div>",
                    unsafe_allow_html=True,
                )

            c1, c2 = st.columns(2, gap="large")

            with c1:
                if report_type == "positive":
                    render_card(
                        "😊 Acolhimento positivo",
                        "<p>Que bom saber que você está vivendo um momento positivo. "
                        "Obrigado por compartilhar essa experiência!</p>",
                    )
                elif report_type == "neutral":
                    render_card(
                        "🤝 Acolhimento",
                        "<p>Obrigado por compartilhar seu relato. Caso deseje, você pode "
                        "contar um pouco mais sobre como essa situação fez você se sentir.</p>",
                    )
                else:
                    render_card(
                        "🤝 Acolhimento",
                        "<p>Obrigado por compartilhar o que você está sentindo. "
                        "Você merece ser ouvido com respeito.</p>",
                    )

            with c2:
                if report_type == "positive":
                    summary = (
                        "O relato demonstra emoções positivas, satisfação e sinais "
                        "de bem-estar relacionados à experiência compartilhada."
                    )
                elif report_type == "neutral":
                    summary = (
                        "O relato não apresenta elementos suficientes para identificar "
                        "uma emoção predominante ou sinais claros de sofrimento."
                    )
                else:
                    summary = (
                        "O relato indica um momento de sofrimento emocional que merece "
                        "atenção e acolhimento."
                    )

                render_card("📝 Resumo do relato", f"<p>{summary}</p>")

            c3, c4 = st.columns(2, gap="large")

            with c3:
                if report_type == "positive":
                    items = positive_aspects or ["Bem-estar emocional"]
                    title = "✨ Aspectos positivos identificados"
                elif report_type == "neutral":
                    items = ["Contexto emocional insuficiente"]
                    title = "🔎 Aspectos observados"
                else:
                    items = signs or ["Possível sofrimento emocional"]
                    title = "🔍 Sinais observados"

                items_html = "<ul>" + "".join(
                    f"<li>{html.escape(item)}</li>" for item in items
                ) + "</ul>"
                render_card(title, items_html)

            with c4:
                if report_type == "positive":
                    text_info = (
                        "<p>Reconhecer conquistas e emoções agradáveis pode contribuir "
                        "para o bem-estar emocional e fortalecer hábitos saudáveis.</p>"
                    )
                elif report_type == "neutral":
                    text_info = (
                        "<p>Relatos breves podem não apresentar informações emocionais "
                        "suficientes. Uma análise mais completa depende de contexto.</p>"
                    )
                else:
                    text_info = (
                        "<p>Esses sinais podem aparecer em diferentes situações. "
                        "Um relato isolado não permite estabelecer diagnóstico clínico.</p>"
                    )

                render_card("💡 Informações educativas", text_info)

            c5, c6 = st.columns(2, gap="large")

            with c5:
                if report_type == "positive":
                    render_card(
                        "🌱 Sugestões para preservar o bem-estar",
                        "<ul>"
                        "<li>Valorizar e registrar suas conquistas.</li>"
                        "<li>Compartilhar o momento com pessoas importantes.</li>"
                        "<li>Manter hábitos que favoreçam o bem-estar.</li>"
                        "</ul>",
                    )
                elif report_type == "neutral":
                    render_card(
                        "🧭 Próximos passos sugeridos",
                        "<ul>"
                        "<li>Refletir sobre como a situação fez você se sentir.</li>"
                        "<li>Compartilhar mais detalhes, caso se sinta confortável.</li>"
                        "<li>Observar mudanças de humor, sono e energia.</li>"
                        "</ul>",
                    )
                else:
                    render_card(
                        "❤️ Cuidados sugeridos",
                        "<ul>"
                        "<li>Conversar com alguém de confiança.</li>"
                        "<li>Observar a evolução dos sentimentos.</li>"
                        "<li>Buscar apoio psicológico.</li>"
                        "<li>Manter rotina básica de sono e descanso.</li>"
                        "</ul>",
                    )

            with c6:
                if report_type == "risk":
                    render_card(
                        "🚨 Quando buscar ajuda imediatamente",
                        "<p>Caso exista risco imediato ou intenção de se machucar, "
                        "procure uma pessoa de confiança e um serviço de emergência.</p>",
                    )
                elif report_type == "distress":
                    render_card(
                        "🩺 Quando procurar ajuda profissional",
                        "<p>Procure um profissional quando os sintomas persistirem, "
                        "se intensificarem ou prejudicarem sua rotina.</p>",
                    )
                elif report_type == "positive":
                    render_card(
                        "💜 Cuidado contínuo",
                        "<p>Mesmo em períodos positivos, cuidar da saúde mental e manter "
                        "relações de apoio continua sendo importante.</p>",
                    )
                else:
                    render_card(
                        "💬 Quando compartilhar mais",
                        "<p>Caso exista algum desconforto não mencionado, você pode "
                        "descrever melhor seus sentimentos ou conversar com alguém de confiança.</p>",
                    )

            st.markdown('### 📚 Fontes previstas')
            st.markdown("<span class='source-tag'>WHO mhGAP</span><span class='source-tag'>NICE Guidelines</span><span class='source-tag'>Ministério da Saúde</span><span class='source-tag'>CVV</span><span class='source-tag'>DSM-5-TR autorizado</span>",unsafe_allow_html=True)
            st.markdown("<div class='safety-warning'><strong>⚠️ Aviso:</strong> esta resposta é simulada, educacional e não substitui atendimento profissional.</div>",unsafe_allow_html=True)

with dataset_tab:
    st.markdown('## Exploração do dataset')
    if df is None: st.error('O dataset não pôde ser carregado.')
    else:
        g1,g2=st.columns(2,gap='large')
        with g1:
            if (OUTPUTS_DIR/'categorias.png').exists(): st.image(str(OUTPUTS_DIR/'categorias.png'),width='stretch')
        with g2:
            if (OUTPUTS_DIR/'tamanho_relatos.png').exists(): st.image(str(OUTPUTS_DIR/'tamanho_relatos.png'),width='stretch')
        table=df['tag'].value_counts().rename_axis('Categoria').reset_index(name='Quantidade')
        table['Percentual']=(table['Quantidade']/len(df)*100).round(2)
        st.dataframe(table,width='stretch',hide_index=True)
        st.dataframe(df[['id','post_content','tag','timestamp']].head(15),width='stretch',hide_index=True)

with project_tab:
    st.markdown('<h2 style="margin-bottom: 2.2rem; margin-top: 0.5rem;">Sobre o Zophia Lite</h2>', unsafe_allow_html=True)
    
    with st.expander('Objetivo', expanded=True):
        st.markdown('Desenvolver um assistente conversacional com respostas acolhedoras, educativas e fundamentadas.')
        
    with st.expander('Base documental'):
        st.markdown('- WHO mhGAP\n- NICE\n- Ministério da Saúde\n- CVV\n- DSM-5-TR autorizado')
        
    with st.expander('Arquitetura'):
        st.markdown('Streamlit → pré-processamento → embeddings → FAISS → busca semântica → prompt → LLM.')
        
    with st.expander('Semana 1'):
        st.markdown('- EDA concluída.\n- Base documental selecionada.\n- Arquitetura definida.\n- Protótipo funcional.')
