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

async function handleValidarGeometria() {
  const btnValidar = document.getElementById('btnValidarGeometria');
  const statusValidacao = document.getElementById('statusValidacao');
  
  // UI feedback
  btnValidar.disabled = true;
  btnValidar.textContent = 'Validando...';
  statusValidacao.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Validando geometria...';
  
  try {
    const formData = new FormData();
    const arquivoZip = document.getElementById('arquivo_zip').files[0];
    
    if (!arquivoZip) {
      throw new Error('Selecione um arquivo ZIP');
    }
    
    formData.append('arquivo_zip', arquivoZip);
    
    // Chama endpoint do backend
    const response = await fetch('/api/projeto/validar-geometria', {
      method: 'POST',
      body: formData
    });
    
    const result = await response.json();
    
    if (result.status === 'sucesso') {
      statusValidacao.innerHTML = `<span class="text-success"><i class="fas fa-check"></i> ${result.mensagem}</span>`;
      document.getElementById('cardCroqui').style.display = 'block';
    } else {
      statusValidacao.innerHTML = `<span class="text-danger"><i class="fas fa-times"></i> ${result.mensagem}</span>`;
    }
    
  } catch (error) {
    statusValidacao.innerHTML = `<span class="text-danger"><i class="fas fa-exclamation-triangle"></i> Erro: ${error.message}</span>`;
  } finally {
    btnValidar.disabled = false;
    btnValidar.textContent = 'Validar Geometria';
    atualizarPainelConferencia();
  }
}

async function handleGerarCroqui() {
  const btnCroqui = document.getElementById('btnGerarCroqui');
  const previewCroqui = document.getElementById('previewCroqui');
  
  btnCroqui.disabled = true;
  btnCroqui.textContent = 'Gerando...';
  
  try {
    const response = await fetch('/api/projeto/gerar-croqui', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        projeto_id: getProjetoId() 
      })
    });
    
    const result = await response.json();
    
    if (result.status === 'sucesso') {
      previewCroqui.innerHTML = `<img src="${result.caminho_croqui}" class="img-fluid border rounded" alt="Croqui de Localização">`;
      document.getElementById('btnGravarProjeto').disabled = false;
    } else {
      previewCroqui.innerHTML = `<div class="alert alert-danger">${result.mensagem}</div>`;
    }
    
  } catch (error) {
    previewCroqui.innerHTML = `<div class="alert alert-danger">Erro ao gerar croqui: ${error.message}</div>`;
  } finally {
    btnCroqui.disabled = false;
    btnCroqui.textContent = 'Gerar Croqui';
  }
}

async function handleGravarProjeto() {
  const btnGravar = document.getElementById('btnGravarProjeto');
  
  btnGravar.disabled = true;
  btnGravar.textContent = 'Gravando...';
  
  try {
    const dados = coletarDadosFormulario();
    
    const response = await fetch('/api/projeto/gravar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(dados)
    });
    
    const result = await response.json();
    
    if (result.status === 'sucesso') {
      showSuccessMessage('Projeto gravado com sucesso!');
      setFormState(false);
    } else {
      showErrorMessage(result.mensagem || 'Erro ao gravar projeto');
    }
    
  } catch (error) {
    showErrorMessage('Erro ao comunicar com servidor: ' + error.message);
  } finally {
    btnGravar.disabled = false;
    btnGravar.textContent = 'Gravar';
    atualizarPainelConferencia();
  }
}

function handleFinalizarProjeto() {
  if (confirm('Deseja finalizar o projeto? Esta ação não pode ser desfeita.')) {
    setFormState(false);
    showSuccessMessage('Projeto finalizado com sucesso!');
  }
}

function handleEditarProjeto() {
  setFormState(true);
  showInfoMessage('Projeto liberado para edição.');
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
  
  const btnCadastrarElemento = document.getElementById('btnCadastrarElemento');
  if (btnCadastrarElemento) {
    btnCadastrarElemento.addEventListener('click', handleCadastrarElemento);
  }
}

function handleTipoElementoChange() {
  const tipoSelecionado = getValue('tipo_elemento_rodoviario');
  const containerFormulario = document.getElementById('container_formulario_elemento');
  
  if (tipoSelecionado) {
    containerFormulario.style.display = 'block';
    carregarElementosDoTipo(tipoSelecionado);
  } else {
    containerFormulario.style.display = 'none';
  }
  
  atualizarPainelConferencia();
}

async function carregarElementosDoTipo(tipo) {
  const elementoSelect = document.getElementById('elemento_rodoviario_id');
  if (!elementoSelect) return;
  
  try {
    elementoSelect.innerHTML = '<option value="">Carregando...</option>';
    
    const response = await fetch(`/api/cd/${tipo.replace('_', '-')}/listar`);
    const elementos = await response.json();
    
    elementoSelect.innerHTML = '<option value="">Selecione o elemento...</option>';
    
    elementos.forEach(elemento => {
      const option = document.createElement('option');
      option.value = elemento.id;
      option.textContent = formatarNomeElemento(elemento, tipo);
      elementoSelect.appendChild(option);
    });
    
  } catch (error) {
    elementoSelect.innerHTML = '<option value="">Erro ao carregar elementos</option>';
    console.error('Erro ao carregar elementos:', error);
  }
}

function formatarNomeElemento(elemento, tipo) {
  switch(tipo) {
    case 'trecho_rodoviario':
      return `${elemento.codigo || elemento.id} - ${elemento.denominacao || elemento.nome}`;
    case 'rodovia':
      return `${elemento.codigo || elemento.id} - ${elemento.nome}`;
    case 'dispositivo':
      return `${elemento.nome} - ${elemento.tipo || 'Dispositivo'}`;
    case 'obra_arte':
      return `${elemento.nome} - ${elemento.tipo || 'Obra de Arte'}`;
    default:
      return elemento.nome || elemento.codigo || `Elemento ${elemento.id}`;
  }
}

function handleCadastrarElemento() {
  const tipoSelecionado = getValue('tipo_elemento_rodoviario');
  
  if (!tipoSelecionado) {
    showErrorMessage('Selecione primeiro o tipo de elemento rodoviário!');
    return;
  }
  
  const urls = {
    'trecho_rodoviario': '/cadastrar-trecho-rodoviario',
    'rodovia': '/cadastrar-rodovia',
    'dispositivo': '/cadastrar-dispositivo',
    'obra_arte': '/cadastrar-obra-arte'
  };
  
  if (urls[tipoSelecionado]) {
    window.open(urls[tipoSelecionado], '_blank');
  }
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
  const match = texto.match(/^(\w+)\s*-\s*(.*?) \((.*?)\)$/);

  const codigo = match ? match[1] : "";
  const denominacao = match ? match[2] : texto;
  const municipio = match ? match[3] : "";

  document.getElementById("trechoResumoTipo").textContent = tipoSelecionado;
  document.getElementById("trechoResumoCodigo").textContent = codigo;
  document.getElementById("trechoResumoDenominacao").textContent = denominacao;
  document.getElementById("trechoResumoMunicipio").textContent = municipio;

  document.getElementById("trechoInputFinal").value = select.value;
  document.getElementById("boxTrecho").classList.add("hidden");
  document.getElementById("resumoTrecho").classList.remove("hidden");

  verificarGravacao();
}

// ==================== VERIFICAÇÃO FINAL DE GRAVAÇÃO ====================

// Habilita ou desabilita botão Gravar Projeto
function verificarGravacao() {
  const nome = document.querySelector("input[name='nome']")?.value.trim();
  const pfOk = document.getElementById("pfInputFinal")?.value;
  const pjOk = document.getElementById("pjInputFinal")?.value;
  const trechoOk = document.getElementById("trechoInputFinal")?.value;
  const botao = document.getElementById("btnGravarProjeto");

  if (!botao) return; // evita erro se o botão não existir

  const pronto = nome && pfOk && pjOk && trechoOk;
  if (pronto) {
    botao.classList.add("ativo");
    botao.disabled = false;
  } else {
    botao.classList.remove("ativo");
    botao.disabled = true;
  }
}
