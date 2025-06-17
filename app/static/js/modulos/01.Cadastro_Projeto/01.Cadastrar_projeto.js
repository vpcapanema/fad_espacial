// ==================== FORMULÁRIO DE CADASTRO DE PROJETO ====================
// Script focado apenas na interface/UX - Todo processamento é feito no backend

document.addEventListener("DOMContentLoaded", function () {
  console.log("✅ Módulo de Cadastro de Projeto carregado");
  
  // Inicializa componentes
  inicializarFormulario();
  configurarEventListeners();
  atualizarPainelConferencia();
});

// ==================== FUNÇÕES DE INICIALIZAÇÃO ====================

function inicializarFormulario() {
  // Configuração inicial do formulário
  const formElement = document.getElementById('formCadastroProjeto');
  if (formElement) {
    formElement.addEventListener('submit', handleFormSubmit);
  }
  
  // Inicializa estado dos botões
  setFormState(true);
}

function configurarEventListeners() {
  // Campos do formulário principal
  const campos = ['tipo_projeto', 'interessado_id', 'representante_id', 'tipo_elemento_rodoviario', 'elemento_rodoviario_id'];
  
  campos.forEach(id => {
    const elemento = document.getElementById(id);
    if (elemento) {
      elemento.addEventListener('change', () => {
        atualizarPainelConferencia();
        validarFormulario();
      });
    }
  });

  // Arquivo ZIP
  const arquivoZip = document.getElementById('arquivo_zip');
  if (arquivoZip) {
    arquivoZip.addEventListener('change', atualizarPainelConferencia);
  }

  // Botões de ação
  configurarBotoes();
  
  // Elementos rodoviários dinâmicos
  configurarElementosRodoviarios();
}

function configurarBotoes() {
  // Validar Geometria
  const btnValidar = document.getElementById('btnValidarGeometria');
  if (btnValidar) {
    btnValidar.addEventListener('click', handleValidarGeometria);
  }

  // Gerar Croqui
  const btnCroqui = document.getElementById('btnGerarCroqui');
  if (btnCroqui) {
    btnCroqui.addEventListener('click', handleGerarCroqui);
  }

  // Gravar Projeto
  const btnGravar = document.getElementById('btnGravarProjeto');
  if (btnGravar) {
    btnGravar.addEventListener('click', handleGravarProjeto);
  }

  // Finalizar/Editar
  const btnFinalizar = document.getElementById('btnFinalizarProjeto');
  const btnEditar = document.getElementById('btnEditarProjeto');
  
  if (btnFinalizar) btnFinalizar.addEventListener('click', () => handleFinalizarProjeto());
  if (btnEditar) btnEditar.addEventListener('click', () => handleEditarProjeto());
}

// ==================== HANDLERS DOS BOTÕES (BACKEND PROCESSING) ====================

// ==================== HANDLER DE VALIDAÇÃO DE GEOMETRIA (NOVO FLUXO) ====================

async function handleValidarGeometria() {
  const btnValidar = document.getElementById('btnValidarGeometria');
  const statusValidacao = document.getElementById('statusValidacao');
  
  // UI feedback
  btnValidar.disabled = true;
  btnValidar.textContent = 'Validando...';
  statusValidacao.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Validando ZIP e geometria...';
  
  try {
    const formData = new FormData();
    const arquivoZip = document.getElementById('arquivo_zip').files[0];
    
    if (!arquivoZip) {
      throw new Error('Selecione um arquivo ZIP');
    }
    
    formData.append('arquivo_zip', arquivoZip);
    
    // ETAPA 2: Validação ZIP + Geometria
    const response = await fetch('/api/projeto/validar-geometria', {
      method: 'POST',
      body: formData
    });
    
    const result = await response.json();
    
    if (result.status === 'sucesso') {
      // Sucesso - geometria validada
      statusValidacao.innerHTML = `
        <div class="alert alert-success">
          <i class="fas fa-check"></i> ${result.mensagem}
          <br><a href="${result.pdf_relatorio}" target="_blank" class="btn btn-sm btn-outline-success mt-2">
            <i class="fas fa-file-pdf"></i> Baixar Relatório PDF
          </a>
        </div>
      `;
      
      // Armazenar dados para próximas etapas
      window.projetoTempId = result.projeto_temp_id;
      window.geometriaDados = result.geometria_dados;
      
      // ETAPA 3: Carregar mapa com geometria e malha DER
      await carregarGeometriaNoMapa(result.projeto_temp_id);
      
      // Mostrar card do croqui
      document.getElementById('cardCroqui').style.display = 'block';
      
    } else {
      // Erro - mostrar relatório de erro
      statusValidacao.innerHTML = `
        <div class="alert alert-danger">
          <i class="fas fa-times"></i> ${result.mensagem}
          <br><strong>Fluxo interrompido.</strong>
          <br><a href="${result.pdf_erro_path}" target="_blank" class="btn btn-sm btn-outline-danger mt-2">
            <i class="fas fa-file-pdf"></i> Baixar Relatório de Erros
          </a>
        </div>
      `;
    }
    
  } catch (error) {
    statusValidacao.innerHTML = `
      <div class="alert alert-danger">
        <i class="fas fa-exclamation-triangle"></i> Erro inesperado: ${error.message}
      </div>
    `;
  } finally {
    btnValidar.disabled = false;
    btnValidar.textContent = 'Validar Geometria';
    atualizarPainelConferencia();
  }
}

// ==================== CARREGAR GEOMETRIA NO MAPA (ETAPA 3) ====================

async function carregarGeometriaNoMapa(projetoTempId) {
  try {
    const response = await fetch(`/api/projeto/geometria-mapa/${projetoTempId}`);
    const result = await response.json();
    
    if (result.status === 'sucesso') {
      // Obter instância do mapa
      const map = getMapInstance();
      if (!map) {
        console.error('Mapa não inicializado');
        return;
      }
      
      // Carregar malha DER como camada base
      window.malhaDerLayer = L.layerGroup();
      result.malha_der.forEach(rodovia => {
        try {
          // Converter WKT para GeoJSON (simplificado)
          const feature = L.geoJSON(convertWktToGeoJson(rodovia.wkt), {
            style: {
              color: '#FFA500',
              weight: 3,
              opacity: 0.7
            }
          }).bindTooltip(`${rodovia.codigo} - ${rodovia.nome}`);
          
          window.malhaDerLayer.addLayer(feature);
        } catch (e) {
          console.warn('Erro ao carregar rodovia:', rodovia.codigo, e);
        }
      });
      
      // Adicionar malha DER ao mapa
      window.malhaDerLayer.addTo(map);
      
      // Carregar geometria do projeto
      window.geometriaProjetoLayer = L.geoJSON(convertWktToGeoJson(result.geometria_projeto.wkt), {
        style: {
          color: '#FF0000',
          weight: 4,
          opacity: 0.9,
          fillColor: '#FF0000',
          fillOpacity: 0.3
        }
      }).bindTooltip('Geometria do Projeto');
      
      window.geometriaProjetoLayer.addTo(map);
      
      // Ajustar zoom para mostrar a geometria
      const bbox = result.geometria_projeto.bbox;
      map.fitBounds([
        [bbox.min_y, bbox.min_x],
        [bbox.max_y, bbox.max_x]
      ], { padding: [20, 20] });
      
      // Habilitar geração de croqui
      document.getElementById('btnGerarCroqui').disabled = false;
      
    } else {
      console.error('Erro ao carregar geometria:', result.mensagem);
    }
    
  } catch (error) {
    console.error('Erro ao carregar geometria no mapa:', error);
  }
}

async function handleGerarCroqui() {
  const btnCroqui = document.getElementById('btnGerarCroqui');
  const previewCroqui = document.getElementById('previewCroqui');
  
  btnCroqui.disabled = true;
  btnCroqui.textContent = 'Gerando...';
  
  try {
    // Capturar estado atual do mapa
    const map = getMapInstance();
    if (!map) {
      throw new Error('Mapa não encontrado');
    }
    
    // Obter dados do mapa
    const basemapSelect = document.getElementById('basemapSelect');
    const dadosMapa = {
      basemap_selecionado: basemapSelect.value,
      zoom: map.getZoom(),
      centro: {
        lat: map.getCenter().lat,
        lon: map.getCenter().lng
      }
    };
    
    // Capturar screenshot do mapa (simulação)
    const imagemBase64 = await capturarScreenshotMapa();
    dadosMapa.imagem_base64 = imagemBase64;
    
    // Enviar para backend
    const response = await fetch('/api/projeto/gerar-croqui', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        projeto_temp_id: window.projetoTempId,
        dados_mapa: dadosMapa
      })
    });
    
    const result = await response.json();
    
    if (result.status === 'sucesso') {
      previewCroqui.innerHTML = `
        <div class="alert alert-success">
          <h5><i class="fas fa-check"></i> Croqui gerado com sucesso!</h5>
          <img src="${result.caminho_croqui}" class="img-fluid border rounded mt-2" alt="Croqui de Localização">
        </div>
      `;
      
      // Armazenar dados do croqui
      window.caminhosCroqui = result.caminho_croqui;
      window.metadadosCroqui = result.metadados;
      
      // Habilitar finalização
      document.getElementById('btnFinalizarProjeto').disabled = false;
      
    } else {
      previewCroqui.innerHTML = `
        <div class="alert alert-danger">
          <i class="fas fa-times"></i> ${result.mensagem}
        </div>
      `;
    }
    
  } catch (error) {
    previewCroqui.innerHTML = `
      <div class="alert alert-danger">
        <i class="fas fa-exclamation-triangle"></i> Erro: ${error.message}
      </div>
    `;
  } finally {
    btnCroqui.disabled = false;
    btnCroqui.textContent = 'Gerar Croqui';
  }
}

async function capturarScreenshotMapa() {
  // Simulação de captura de screenshot
  // Em produção, usar html2canvas ou leaflet-image
  
  return new Promise((resolve) => {
    // Gerar uma imagem base64 simples como placeholder
    const canvas = document.createElement('canvas');
    canvas.width = 800;
    canvas.height = 600;
    const ctx = canvas.getContext('2d');
    
    // Fundo azul claro (simulando mapa)
    ctx.fillStyle = '#E3F2FD';
    ctx.fillRect(0, 0, 800, 600);
    
    // Texto indicativo
    ctx.fillStyle = '#1976D2';
    ctx.font = '24px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Croqui de Localização', 400, 300);
    ctx.fillText('Geometria + Malha DER', 400, 340);
    
    // Converter para base64
    const base64 = canvas.toDataURL('image/png');
    resolve(base64);
  });
}

// ==================== UTILITÁRIOS GEOESPACIAIS ====================

function convertWktToGeoJson(wkt) {
  // Conversão simplificada WKT para GeoJSON
  // Em produção, usar biblioteca como Wicket ou similar
  
  try {
    if (wkt.startsWith('POINT')) {
      const coords = wkt.match(/POINT\s*\(\s*([^)]+)\)/)[1].split(' ');
      return {
        type: 'Feature',
        geometry: {
          type: 'Point',
          coordinates: [parseFloat(coords[0]), parseFloat(coords[1])]
        }
      };
    }
    
    if (wkt.startsWith('LINESTRING')) {
      const coordsStr = wkt.match(/LINESTRING\s*\(\s*([^)]+)\)/)[1];
      const coords = coordsStr.split(',').map(pair => {
        const [x, y] = pair.trim().split(' ');
        return [parseFloat(x), parseFloat(y)];
      });
      
      return {
        type: 'Feature',
        geometry: {
          type: 'LineString',
          coordinates: coords
        }
      };
    }
    
    if (wkt.startsWith('POLYGON')) {
      const coordsStr = wkt.match(/POLYGON\s*\(\s*\(([^)]+)\)\s*\)/)[1];
      const coords = coordsStr.split(',').map(pair => {
        const [x, y] = pair.trim().split(' ');
        return [parseFloat(x), parseFloat(y)];
      });
      
      return {
        type: 'Feature',
        geometry: {
          type: 'Polygon',
          coordinates: [coords]
        }
      };
    }
    
    // Fallback para tipos não suportados
    console.warn('Tipo WKT não suportado:', wkt.substring(0, 20));
    return null;
    
  } catch (error) {
    console.error('Erro ao converter WKT:', error);
    return null;
  }
}

// ==================== FUNÇÕES AUXILIARES ====================

function coletarDadosFormulario() {
  return {
    tipo_projeto: getValue('tipo_projeto'),
    interessado_id: getValue('interessado_id'),
    representante_id: getValue('representante_id'),
    tipo_elemento_rodoviario: getValue('tipo_elemento_rodoviario'),
    elemento_rodoviario_id: getValue('elemento_rodoviario_id')
  };
}

function getValue(elementId) {
  const element = document.getElementById(elementId);
  return element ? element.value : '';
}

function getProjetoId() {
  // Retorna o ID do projeto em edição ou null para novo projeto
  return window.projetoId || null;
}

function validarFormulario() {
  const dados = coletarDadosFormulario();
  const isValid = dados.tipo_projeto && dados.interessado_id && dados.representante_id;
  
  const btnGravar = document.getElementById('btnGravarProjeto');
  if (btnGravar) {
    btnGravar.disabled = !isValid;
  }
  
  return isValid;
}

function setFormState(editavel) {
  const form = document.getElementById('formCadastroProjeto');
  if (form) {
    Array.from(form.elements).forEach(el => {
      if (el.type !== 'button') el.disabled = !editavel;
    });
  }
  
  // Controle dos botões
  const btnGravar = document.getElementById('btnGravarProjeto');
  const btnFinalizar = document.getElementById('btnFinalizarProjeto');
  const btnEditar = document.getElementById('btnEditarProjeto');
  
  if (btnGravar) btnGravar.disabled = !editavel;
  if (btnFinalizar) btnFinalizar.disabled = editavel;
  if (btnEditar) btnEditar.disabled = editavel;
}

function atualizarPainelConferencia() {
  const updates = {
    'confTipoProjeto': getSelectedText('tipo_projeto'),
    'confInteressado': getSelectedText('interessado_id'),
    'confRepresentante': getSelectedText('representante_id'),
    'confElemento': getElementoRodoviarioText(),
    'confZip': getFileNameText('arquivo_zip'),
    'confGeom': getGeometriaValidadaText(),
    'confRelatorio': getRelatorioText()
  };
  
  Object.entries(updates).forEach(([id, text]) => {
    const element = document.getElementById(id);
    if (element) element.textContent = text || '-';
  });
}

function getSelectedText(selectId) {
  const select = document.getElementById(selectId);
  return select && select.selectedOptions[0] ? select.selectedOptions[0].text : '';
}

function getElementoRodoviarioText() {
  const tipoElement = document.getElementById('tipo_elemento_rodoviario');
  const elementoElement = document.getElementById('elemento_rodoviario_id');
  
  if (tipoElement && tipoElement.value) {
    let texto = getSelectedText('tipo_elemento_rodoviario');
    if (elementoElement && elementoElement.value) {
      texto += ' - ' + getSelectedText('elemento_rodoviario_id');
    }
    return texto;
  }
  return '';
}

function getFileNameText(inputId) {
  const input = document.getElementById(inputId);
  return input && input.files.length ? input.files[0].name : '';
}

function getGeometriaValidadaText() {
  const status = document.getElementById('statusValidacao');
  return status && status.textContent.includes('sucesso') ? 'Sim' : 'Não';
}

function getRelatorioText() {
  const status = document.getElementById('statusValidacao');
  return status ? status.textContent : '';
}

// ==================== FUNÇÕES DE FEEDBACK ====================

function showSuccessMessage(message) {
  showMessage(message, 'success');
}

function showErrorMessage(message) {
  showMessage(message, 'danger');
}

function showInfoMessage(message) {
  showMessage(message, 'info');
}

function showMessage(message, type) {
  // Remove mensagens anteriores
  const existingAlert = document.querySelector('.alert-temporary');
  if (existingAlert) existingAlert.remove();
  
  // Cria nova mensagem
  const alert = document.createElement('div');
  alert.className = `alert alert-${type} alert-temporary`;
  alert.innerHTML = `<i class="fas fa-info-circle"></i> ${message}`;
  
  // Insere no início do formulário
  const container = document.querySelector('.container-fluid');
  if (container) {
    container.insertBefore(alert, container.firstChild);
    
    // Remove automaticamente após 5 segundos
    setTimeout(() => {
      if (alert.parentNode) alert.remove();
    }, 5000);
  }
}

// ==================== ELEMENTOS RODOVIÁRIOS DINÂMICOS ====================

function configurarElementosRodoviarios() {
  const tipoElemento = document.getElementById('tipo_elemento_rodoviario');
  if (tipoElemento) {
    tipoElemento.addEventListener('change', handleTipoElementoChange);
  }
}

function handleTipoElementoChange() {
  const tipoSelecionado = getValue('tipo_elemento_rodoviario');
  const containerElemento = document.getElementById('container_elemento_especifico');
  
  if (tipoSelecionado) {
    containerElemento.style.display = 'block';
    carregarElementosDoTipo(tipoSelecionado);
  } else {
    containerElemento.style.display = 'none';
    // Limpa o select
    const elementoSelect = document.getElementById('elemento_rodoviario_id');
    if (elementoSelect) {
      elementoSelect.innerHTML = '<option value="">Selecione o elemento...</option>';
    }
  }
  
  atualizarPainelConferencia();
}

async function carregarElementosDoTipo(tipo) {
  const elementoSelect = document.getElementById('elemento_rodoviario_id');
  if (!elementoSelect) return;
  
  try {
    elementoSelect.innerHTML = '<option value="">Carregando...</option>';
    
    // Mapeia os tipos para os endpoints corretos
    const endpointMap = {
      'trecho_rodoviario': '/api/cd/trecho-rodoviario/listar',
      'rodovia': '/api/cd/rodovia/listar', 
      'dispositivo': '/api/cd/dispositivo/listar',
      'obra_arte': '/api/cd/obra-arte/listar'
    };
    
    const endpoint = endpointMap[tipo];
    if (!endpoint) {
      elementoSelect.innerHTML = '<option value="">Tipo não suportado</option>';
      return;
    }
    
    const response = await fetch(endpoint);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const result = await response.json();
    
    // Verifica se é um array ou se tem propriedade com array
    let elementos = [];
    if (Array.isArray(result)) {
      elementos = result;
    } else if (result.data && Array.isArray(result.data)) {
      elementos = result.data;
    } else if (result.elementos && Array.isArray(result.elementos)) {
      elementos = result.elementos;
    } else {
      console.warn('Resposta não contém array de elementos:', result);
      elementos = [];
    }
    
    elementoSelect.innerHTML = '<option value="">Selecione o elemento...</option>';
    
    if (elementos.length === 0) {
      elementoSelect.innerHTML += '<option value="">Nenhum elemento encontrado</option>';
      return;
    }
    
    elementos.forEach(elemento => {
      const option = document.createElement('option');
      option.value = elemento.id;
      option.textContent = formatarNomeElemento(elemento, tipo);
      elementoSelect.appendChild(option);
    });
    
  } catch (error) {
    elementoSelect.innerHTML = '<option value="">Erro ao carregar elementos</option>';
    console.error('Erro ao carregar elementos:', error);
    showErrorMessage('Erro ao carregar lista de elementos: ' + error.message);
  }
}

function formatarNomeElemento(elemento, tipo) {
  // Usa denominacao como campo principal, com fallback para nome
  const nome = elemento.denominacao || elemento.nome || `Elemento ${elemento.id}`;
  const codigo = elemento.codigo || elemento.id;
  const municipio = elemento.municipio || 'N/A';
  
  return `${codigo} - ${nome} (${municipio})`;
}

// ==================== FORMULÁRIO SUBMIT ====================

function handleFormSubmit(event) {
  event.preventDefault();
  
  if (!validarFormulario()) {
    showErrorMessage('Preencha todos os campos obrigatórios');
    return;
  }
  
  handleGravarProjeto();
}
