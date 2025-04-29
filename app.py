from flask import Flask, render_template, request, session
from faq_data import faq

app = Flask(__name__)
app.secret_key = "sua_chave_secreta_super_segura"  # importante para usar sessão

def encontrar_resposta(pergunta_usuario):
    pergunta_usuario = pergunta_usuario.lower()
    palavras_chave = pergunta_usuario.split()

    respostas_encontradas = []

    for pergunta, info in faq.items():
        tags = info["tags"]
        tags_em_comum = [tag for tag in tags if tag in palavras_chave]

        if len(tags_em_comum) >= 2:
            respostas_encontradas.append(info["resposta"])

    if respostas_encontradas:
        return " ".join(respostas_encontradas)
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
        session.modified = True

    return render_template("index.html", historico=session["historico"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
