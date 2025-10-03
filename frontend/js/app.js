// Mostrar módulos (se quiser trocar telas depois)
function mostrarModulo(id) {
  document.querySelectorAll('.modulo').forEach(sec => sec.classList.remove('ativo'));
  document.getElementById(id).classList.add('ativo');
}

let grafico = null;

// Cria gráfico ao carregar página
document.addEventListener('DOMContentLoaded', () => {
  const ctx = document.getElementById("graficoSensores").getContext('2d');
  grafico = new Chart(ctx, {
    type: "line",
    data: {
      labels: [],
      datasets: [{
        label: "Temperatura do Forno (°C)",
        data: [],
        borderWidth: 2,
        borderColor: "orange",
        tension: 0.3
      }]
    },
    options: {
      animation: false,
      scales: { x: { display: true }, y: { beginAtZero: false } }
    }
  });
  setInterval(atualizarSensores, 2000);
});

async function atualizarSensores() {
  if (!grafico) return;
  try {
    let resp = await fetch("http://127.0.0.1:5000/api/sensors");
    let dados = await resp.json();
    grafico.data.labels.push(dados.timestamp);
    grafico.data.datasets[0].data.push(dados.temperatura_forno);
    if (grafico.data.labels.length > 20) {
      grafico.data.labels.shift();
      grafico.data.datasets[0].data.shift();
    }
    grafico.update();
  } catch (e) {
    console.error("Erro sensores", e);
  }
}

async function gerarRelatorio() {
  try {
   let resp = await fetch("http://127.0.0.1:5000/api/generate_report");
    let dados = await resp.json();
    document.getElementById("saidaRelatorio").textContent =
      `📂 Arquivo: ${dados.filename}\n` +
      `Mensagem: ${dados.message}\n\n` +
      `📝 Relatório:\n${dados.relatorio}`;
    let linkId = "linkCsv";
    let existing = document.getElementById(linkId);
    const baseUrl = "http://127.0.0.1:5000";
    if (!existing) {
      const a = document.createElement("a");
      a.id = linkId;
      a.href = baseUrl + dados.path;
      a.target = "_blank";
      a.textContent = "📊 Abrir CSV gerado";
      document.getElementById("relatorios").appendChild(a);
    } else {
      existing.href = baseUrl + dados.path;
    }
  } catch (e) {
    document.getElementById("saidaRelatorio").textContent = "❌ Erro ao gerar relatório: " + e.message;
  }
}
