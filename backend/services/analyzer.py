import html
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATASET_PATH = BASE_DIR / 'dataset' / 'mental_health_social_media_posts.csv'

def load_dataset():
    if not DATASET_PATH.exists():
        return None
    try:
        return pd.read_csv(DATASET_PATH)
    except Exception:
        return None

def detect_signs(text: str):
    t = text.lower()
    signs = []
    groups = {
        "Alterações no sono": ["sleep", "insomnia", "dormir", "sono", "insônia"],
        "Tristeza ou desânimo": ["sad", "sadness", "triste", "tristeza", "despair", "desespero", "vazio", "vazia"],
        "Sinais relacionados à ansiedade": ["anxiety", "anxious", "ansiedade", "ansioso", "ansiosa", "panic", "pânico"],
        "Redução de energia ou motivação": ["energy", "energia", "motivation", "motivação", "bed", "cama", "tired", "cansado", "cansada"],
        "Dificuldade de concentração": ["focus", "concentrate", "concentração", "concentrar", "attention", "atenção"],
    }
    for sign, keys in groups.items():
        if any(key in t for key in keys):
            signs.append(sign)
    return signs

def detect_positive(text: str):
    t = text.lower()
    aspects = []
    groups = {
        "Emoções positivas": ["feliz", "alegre", "contente", "animado", "animada", "happy", "great", "ótimo", "otimo", "incrível", "incrivel"],
        "Sentimento de realização": ["consegui", "passei", "ganhei", "conquista", "conquistei", "aprovado", "aprovada", "emprego", "estágio", "estagio"],
        "Esperança e motivação": ["esperança", "esperanca", "motivado", "motivada", "confiante", "empolgado", "empolgada"],
        "Gratidão": ["grato", "grata", "gratidão", "gratidao", "agradecido", "agradecida"],
    }
    for aspect, keys in groups.items():
        if any(key in t for key in keys):
            aspects.append(aspect)
    return aspects

def detect_risk(text: str):
    t = text.lower()
    terms = [
        "suicidal", "suicide", "kill myself", "end my life",
        "me matar", "tirar minha vida", "não quero viver",
        "nao quero viver", "acabar com minha vida"
    ]
    return any(term in t for term in terms)

def classify_report(text: str):
    if detect_risk(text):
        return "risk"
    positive = detect_positive(text)
    negative = detect_signs(text)
    if positive and not negative:
        return "positive"
    if negative:
        return "distress"
    return "neutral"

def analyze_report(text: str):
    report_type = classify_report(text)
    signs = detect_signs(text)
    positive_aspects = detect_positive(text)
    risk = (report_type == "risk")

    if report_type == "positive":
        welcoming_summary = "Que bom saber que você está vivendo um momento positivo! O seu relato demonstra sentimentos de satisfação e bem-estar em relação à experiência compartilhada."
        educational_info = "Reconhecer conquistas e momentos agradáveis fortalece a saúde emocional e amplia a resiliência diária."
        suggested_cares = [
            "Valorizar e registrar suas conquistas em um diário.",
            "Compartilhar essa alegria com pessoas de sua confiança.",
            "Manter hábitos saudáveis de descanso e lazer que favoreçam esse bem-estar."
        ]
        when_to_seek_help = "Mesmo em períodos positivos, manter o acompanhamento com profissionais de saúde mental ajuda na prevenção e no autoconhecimento contínuo."
    elif report_type == "neutral":
        welcoming_summary = "Obrigado por compartilhar o seu relato. A mensagem traz uma narrativa serena, sem indícios preponderantes de tensão ou sofrimento."
        educational_info = "Relatos mais neutros ou breves trazem pontos de reflexão geral sobre a rotina sem indicar quadro clínico específico."
        suggested_cares = [
            "Observar como a situação faz você se sentir ao longo do dia.",
            "Compartilhar mais detalhes com a Zophia caso deseje aprofundar pensamentos.",
            "Manter uma rotina equilibrada de sono, alimentação e pausa."
        ]
        when_to_seek_help = "Busque atendimento profissional caso perceba mudanças repentinas de humor, episódios frequentes de ansiedade ou dificuldades prolongadas para dormir."
    else:
        welcoming_summary = "Obrigado por confiar e compartilhar o que você está sentindo. Compreendo que este é um momento delicado e você merece ser ouvido com empatia e respeito."
        educational_info = "Os sinais identificados (como alterações de sono, ansiedade ou desânimo) são respostas comuns do organismo a períodos de sobrecarga ou estresse intenso. Esta análise tem finalidade educacional e não substitui diagnóstico clínico."
        suggested_cares = [
            "Conversar abertamente com uma pessoa de sua confiança.",
            "Manter a rotina básica de descanso e pausas na jornada diária.",
            "Praticar rotinas leves como exercícios de respiração 4-7-8.",
            "Considerar o agendamento de uma consulta de acolhimento psicológico."
        ]
        when_to_seek_help = "Procure ajuda profissional imediata ou atendimento especializado se os sintomas persistirem por semanas, se intensificarem ou prejudicarem suas atividades básicas de trabalho e convivência."

    sources = [
        "DSM-5-TR (Manual Diagnóstico e Estatístico de Transtornos Mentais)",
        "WHO mhGAP (Programa de Ação para Lacunas em Saúde Mental)",
        "NICE Guidelines (Diretrizes de Saúde Mental)",
        "Ministério da Saúde (Rede de Atenção Psicossocial - RAPS)",
        "Material Oficial CVV (Centro de Valorização da Vida)"
    ]

    safety_notice = "Ferramenta exclusivamente educacional de apoio conversacional. Em caso de sofrimento intenso ou crise, ligue 188 (CVV) ou procure atendimento de emergência."

    return {
        "report_type": report_type,
        "welcoming_summary": welcoming_summary,
        "signs": signs if report_type != "positive" else ["Sensação de bem-estar e realização"],
        "educational_info": educational_info,
        "suggested_cares": suggested_cares,
        "when_to_seek_help": when_to_seek_help,
        "sources": sources,
        "safety_notice": safety_notice,
        "risk_warning": risk
    }

def get_stats():
    df = load_dataset()
    if df is None:
        return {
            "records": 0,
            "categories_count": 0,
            "missing_values": 0,
            "average_length": 0.0,
            "categories": {}
        }
    
    return {
        "records": len(df),
        "categories_count": int(df['tag'].nunique()),
        "missing_values": int(df.isnull().sum().sum()),
        "average_length": round(float(df['post_content'].astype(str).str.len().mean()), 2),
        "categories": {cat: int(count) for cat, count in df['tag'].value_counts().items()}
    }
