# Importa as bibliotecas necessárias
from flask import Flask, jsonify, Response, send_from_directory, request
from flask_cors import CORS
import random
import datetime
import csv
import io
import os

# === Tenta importar OpenAI (opcional) ===
try:
    from openai import OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
except ImportError:
    client = None
    OPENAI_API_KEY = None

# Configura o Flask
app = Flask(__name__)
CORS(app)

# Pasta para armazenar os CSVs
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)

# ===================== Simulação de Sensores =====================
def gerar_dados():
    return {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "temperatura_forno": round(random.uniform(180, 250), 2),
        "estoque_farinha": random.randint(0, 100),
        "estoque_ovos": random.randint(0, 200),
        "estoque_leite": random.randint(0, 50),
        "clientes_hora": random.randint(0, 20),
        "consumo_energia": round(random.uniform(5.0, 15.0), 2)
    }

@app.route("/api/sensors")
def sensores():
    return jsonify(gerar_dados())

# ===================== Gerar Relatório =====================
@app.route("/api/generate_report", methods=["GET", "POST"])
def generate_report():
    # aceita parâmetro opcional ?n=50
    try:
        n = int(request.args.get("n", 50))
    except:
        n = 50

    # gera dados simulados
    dados = [gerar_dados() for _ in range(n)]
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"padaria_dados_{timestamp}.csv"
    fullpath = os.path.join(DATA_DIR, filename)

    # salva arquivo único
    with open(fullpath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=dados[0].keys())
        writer.writeheader()
        writer.writerows(dados)

    # sobrescreve sempre o mais recente
    latest_path = os.path.join(DATA_DIR, "padaria_dados.csv")
    with open(latest_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=dados[0].keys())
        writer.writeheader()
        writer.writerows(dados)

    # ========== Relatório em texto ==========
    if client:
        try:
            resumo = (
                f"Temperatura média do forno: {sum(d['temperatura_forno'] for d in dados)/len(dados):.1f} °C\n"
                f"Clientes médios por hora: {sum(d['clientes_hora'] for d in dados)/len(dados):.1f}\n"
                f"Menor estoque de farinha: {min(d['estoque_farinha'] for d in dados)}"
            )

            prompt = (
                "Você é um especialista em gestão de padarias.\n"
                "Com base nos dados abaixo, gere um relatório curto em português (4-6 frases), "
                "com resumo e recomendações práticas.\n\n"
                f"{resumo}"
            )

            resposta = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Você é um analista de dados de padarias."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )

            relatorio_texto = resposta.choices[0].message.content.strip()
        except Exception as e:
            relatorio_texto = f"[Fallback IA] Erro ao usar OpenAI: {e}"
    else:
        # Fallback simples
        temp_media = sum(d["temperatura_forno"] for d in dados) / len(dados)
        clientes_media = sum(d["clientes_hora"] for d in dados) / len(dados)
        estoque_min = min(d["estoque_farinha"] for d in dados)
        relatorio_texto = (
            f"📊 Relatório da Padaria\n\n"
            f"- Temperatura média do forno: {temp_media:.1f} °C\n"
            f"- Clientes por hora (média): {clientes_media:.1f}\n"
            f"- Menor nível de estoque de farinha: {estoque_min}\n\n"
            f"Conclusão: Produção estável, mas atenção ao estoque de farinha."
        )

    return jsonify({
        "status": "OK",
        "filename": filename,
        "path": f"/data/{filename}",
        "message": "Relatório gerado com sucesso.",
        "relatorio": relatorio_texto
    }), 200

# ===================== Rotas Extras =====================
@app.route("/data/<path:filename>")
def serve_data(filename):
    return send_from_directory(DATA_DIR, filename, as_attachment=False)

@app.route("/api/export_csv")
def export_csv():
    dados = [gerar_dados() for _ in range(20)]
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=dados[0].keys())
    writer.writeheader()
    writer.writerows(dados)
    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=padaria_dados.csv"
    return response

# ===================== Run =====================
if __name__ == "__main__":
    app.run(debug=True)
