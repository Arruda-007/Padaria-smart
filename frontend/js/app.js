// app.js (frontend)

// Função que mostra apenas o módulo escolhido na tela
function mostrarModulo(id) {
  // Esconde todos os módulos
  document.querySelectorAll('.modulo').forEach(sec => sec.classList.remove('ativo'));
  // Mostra apenas o módulo que foi clicado/selecionado
  document.getElementById(id).classList.add('ativo');
}

// Variável global que vai armazenar o gráfico
let grafico = null;

// Executa quando todo o HTML já foi carregado
document.addEventListener('DOMContentLoaded', () => {
  // Pega o canvas do gráfico
  const canvas = document.getElementById("graficoSensores");
  const ctx = canvas.getContext('2d');

  // Cria o gráfico de linha usando a biblioteca Chart.js
  grafico = new Chart(ctx, {
    type: "line",
    data: {
      labels: [], // Eixo X (tempo)
      datasets: [{
        label: "Temperatura do Forno (°C)", // Nome da linha
        data: [], // Valores da temperatura
        borderWidth: 2,
        borderColor: "orange", // Cor da linha
        tension: 0.3 // Deixa a linha levemente curva
      }]
    },
    options: {
      animation: false, // Desativa animações (deixa mais rápido)
      scales: { 
        x: { display: true }, 
        y: { beginAtZero: false } // Eixo Y não começa do zero (ajusta à temperatura)
      }
    }
  });

  // Atualiza os dados a cada 2 segundos (2000ms)
  setInterval(atualizarSensores, 2000);
});

// Função que busca os dados dos sensores e atualiza o gráfico
async function atualizarSensores() {
  if (!grafico) return; // Se gráfico não existir, sai da função

  try {
    // Faz requisição para a API (backend)
    let resp = await fetch("http://127.0.0.1:5000/api/sensors");
    if (!resp.ok) throw new Error("HTTP " + resp.status);

    // Converte a resposta para JSON
    let dados = await resp.json();

    // Adiciona os novos valores no gráfico
    grafico.data.labels.push(dados.timestamp); // eixo X: horário
    grafico.data.datasets[0].data.push(dados.temperatura_forno); // eixo Y: temperatura

    // Atualiza o gráfico na tela
    grafico.update();

    // Mantém apenas os últimos 20 pontos no gráfico (para não ficar muito cheio)
    if (grafico.data.labels.length > 20) {
      grafico.data.labels.shift(); // remove o mais antigo
      grafico.data.datasets[0].data.shift(); // remove o dado mais antigo
    }
  } catch (e) {
    console.error("Erro ao buscar sensores", e);
  }
}

// Função para gerar relatório em CSV pelo backend
async function gerarRelatorio() {
  try {
    // Chama endpoint que gera e salva o CSV
    let resp = await fetch("http://127.0.0.1:5000/api/generate_report", { method: "POST" });
    if (!resp.ok) {
      const txt = await resp.text();
      throw new Error("Erro HTTP " + resp.status + " - " + txt);
    }

    // Pega a resposta do backend
    let dados = await resp.json();

    // Mostra no HTML as informações sobre o relatório
    const saida = document.getElementById("saidaRelatorio");
    saida.textContent = `Status: ${dados.status}\nArquivo: ${dados.filename}\nCaminho: ${dados.path}\nMensagem: ${dados.message}`;

    // Cria ou atualiza o link para abrir o CSV gerado
    let linkId = "linkCsv";
    let existing = document.getElementById(linkId);
    const baseUrl = "http://127.0.0.1:5000";

    if (!existing) {
      // Se o link ainda não existe, cria um novo
      const a = document.createElement("a");
      a.id = linkId;
      a.href = baseUrl + dados.path;
      a.target = "_blank"; // abre em nova aba
      a.textContent = "Abrir CSV gerado";
      a.style.display = "inline-block";
      a.style.marginTop = "10px";
      document.getElementById("relatorios").appendChild(a);
    } else {
      // Se já existe, só atualiza o caminho
      existing.href = baseUrl + dados.path;
    }
  } catch (e) {
    console.error(e);
    // Mostra erro no HTML caso algo dê errado
    document.getElementById("saidaRelatorio").textContent = "Erro ao gerar relatório: " + e.message;
  }
}
