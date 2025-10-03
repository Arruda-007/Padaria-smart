import pandas as pd
import matplotlib.pyplot as plt
import requests

# Coletar dados simulados do backend
url = "http://127.0.0.1:5000/api/sensors"
dados = [requests.get(url).json() for _ in range(10)]

df = pd.DataFrame(dados)
print(df.head())

# Gráfico exemplo
plt.plot(df["timestamp"], df["temperatura_forno"])
plt.xticks(rotation=45)
plt.title("Evolução da Temperatura do Forno")
plt.show()
