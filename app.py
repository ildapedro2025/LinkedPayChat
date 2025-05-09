from flask import Flask, render_template, request, session
from faq_data import faq
import spacy
import unicodedata
import string

app = Flask(__name__)
app.secret_key = "sua_chave_secreta_super_segura"

# Carrega o modelo spaCy
nlp = spacy.load("pt_core_news_md")  # use pt_core_news_lg se tiver

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
        tags = info["tags"]
        melhor_similaridade = 0

        for tag in tags:
            tag_doc = nlp(normalizar_texto(tag))
            similaridade = doc_usuario.similarity(tag_doc)
            if similaridade > melhor_similaridade:
                melhor_similaridade = similaridade

        if melhor_similaridade > 0.75:  # ajuste conforme necessário
            respostas_encontradas.append({
                "pergunta": pergunta,
                "resposta": info["resposta"],
                "similaridade": melhor_similaridade
            })

    if respostas_encontradas:
        respostas_encontradas.sort(key=lambda x: x["similaridade"], reverse=True)
        return respostas_encontradas[0]["resposta"]
    else:
        return "Desculpe, não encontrei uma resposta relacionada a isso."

@app.route("/", methods=["GET", "POST"])
def index():
    if "historico" not in session:
        session["historico"] = []

    if request.method == "POST":
        pergunta = request.form["pergunta"]
        resposta = encontrar_resposta(pergunta)

        session["historico"].append({"pergunta": pergunta, "resposta": resposta})
        session.modified = False

    return render_template("index.html", historico=session["historico"])

if __name__ == "__main__":
    app.run(debug=True)
