from flask import Flask, render_template, request, session
from faq_data import faq
import spacy
import unicodedata
import string

app = Flask(__name__)
app.secret_key = "sua_chave_secreta_super_segura"

# Carrega o modelo spaCy grande
nlp = spacy.load("pt_core_news_lg")

def normalizar_texto(texto):
    texto = texto.lower().strip()
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    texto = texto.translate(str.maketrans('', '', string.punctuation))
    return texto

def encontrar_resposta(pergunta_usuario):
    pergunta_usuario = normalizar_texto(pergunta_usuario)
    doc_usuario = nlp(pergunta_usuario)
    respostas_encontradas = []

    for pergunta, info in faq.items():
        melhor_similaridade = 0
        for tag in info["tags"]:
            tag_doc = nlp(normalizar_texto(tag))
            similaridade = doc_usuario.similarity(tag_doc)
            if similaridade > melhor_similaridade:
                melhor_similaridade = similaridade

        respostas_encontradas.append({
            "pergunta": pergunta,
            "resposta": info["resposta"],
            "similaridade": melhor_similaridade
        })

    respostas_encontradas.sort(key=lambda x: x["similaridade"], reverse=True)
    melhor_resposta = respostas_encontradas[0]

    # Se a similaridade for alta, retorna a resposta normalmente
    if melhor_resposta["similaridade"] >= 0.75:
        return melhor_resposta["resposta"]
    
    # Se for moderada, responde com empatia e sugestão
    elif 0.60 <= melhor_resposta["similaridade"] < 0.75:
        return (
            f"Não tenho certeza, mas talvez esteja a perguntar sobre: "
            f"\"{melhor_resposta['pergunta']}\". {melhor_resposta['resposta']}"
        )
    
    # Se for muito baixa, sugere reformular
    else:
        return (
            "Desculpe, ainda não sei responder a essa pergunta. "
            "Você pode tentar reformular ou me perguntar algo sobre pagamentos, agentes ou contas."
        )

@app.route("/", methods=["GET", "POST"])
def index():
    if "historico" not in session:
        session["historico"] = []

    if request.method == "POST":
        pergunta = request.form["pergunta"]
        resposta = encontrar_resposta(pergunta)

        session["historico"].append({"pergunta": pergunta, "resposta": resposta})
        session.modified = True  # Atualiza o histórico na sessão

    return render_template("index.html", historico=session["historico"])

if __name__ == "__main__":
    app.run(debug=True)
