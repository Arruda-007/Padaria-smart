# Importa as bibliotecas necessárias
from flask import Flask, jsonify, Response, send_from_directory, request
from flask_cors import CORS     # Permite que o frontend acesse o backend
import random                   # Gera dados aleatórios
import datetime                 # Manipula datas e horas
import csv                      # Gera arquivos CSV
import io                       # Manipula dados em memória
import os                       # Manipula caminhos de arquivos/pastas

# Configura o Flask
app = Flask(__name__)
CORS(app)  # permite chamadas do frontend em outra porta

# Define a pasta onde os arquivos CSV vão ser salvos (/data)
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)

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

# Endpoint que gera CSV, salva em /data/ e retorna JSON com caminho/arquivo
@app.route("/api/generate_report", methods=["GET", "POST"])
def generate_report():
    # aceita parâmetro opcional ?n=50 para número de linhas
    try:
        n = int(request.args.get("n", 50))
    except:
        n = 50

    # Cria um nome de arquivo único com data/hora
    dados = [gerar_dados() for _ in range(n)]
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"padaria_dados_{timestamp}.csv"
    fullpath = os.path.join(DATA_DIR, filename)

    # salva arquivo timestamped
    with open(fullpath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=dados[0].keys())
        writer.writeheader()
        writer.writerows(dados)

    # também grava/atualiza um arquivo fixo "padaria_dados.csv"
    latest_path = os.path.join(DATA_DIR, "padaria_dados.csv")
    with open(latest_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=dados[0].keys())
        writer.writeheader()
        writer.writerows(dados)

    return jsonify({
        "status": "OK",
        "filename": filename,
        "path": f"/data/{filename}",
        "message": f"CSV salvo em {fullpath}"
    }), 200

# (Opcional) endpoint para download/visualizar arquivos em /data
@app.route("/data/<path:filename>")
def serve_data(filename):
    return send_from_directory(DATA_DIR, filename, as_attachment=False)

# Endpoint que retorna CSV diretamente (download) — mantido se quiser
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

if __name__ == "__main__":
    app.run(debug=True)
   # Executa o Flask em modo debug (auto-reinicia se mudar o código)