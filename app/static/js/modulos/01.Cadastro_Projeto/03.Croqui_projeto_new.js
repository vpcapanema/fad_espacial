// ==================== MÓDULO DO CROQUI DE LOCALIZAÇÃO ====================
// Gerencia o mapa Leaflet e funcionalidades do croqui

let map = null;
let baseLayers = {};
let graticule = null;
let scaleControl = null;

document.addEventListener("DOMContentLoaded", function () {
  console.log("✅ Módulo do Croqui carregado");
  inicializarMapa();
});

// ==================== INICIALIZAÇÃO DO MAPA ====================

function inicializarMapa() {
  // Inicializa o mapa Leaflet
  map = L.map('mapCroqui', {
    zoomControl: true,
    attributionControl: false
  }).setView([-23.5, -46.6], 13);

  // Configura camadas base
  configurarCamadasBase();
  
  // Configura controles
  configurarControles();
  
  // Eventos do mapa
  configurarEventosMapa();
}

function configurarCamadasBase() {
  baseLayers = {
    'osm': L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }),
    'sat': L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
      attribution: '© Esri'
    }),
    'opaco': L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      opacity: 0.5,
      attribution: '© OpenStreetMap contributors'
    })
  };
  
  // Adiciona camada padrão
  baseLayers['osm'].addTo(map);
  
  // Configura seletor de basemap
  const basemapSelect = document.getElementById('basemapSelect');
  if (basemapSelect) {
    basemapSelect.addEventListener('change', trocarBasemap);
  }
}

function configurarControles() {
  // Escala gráfica
  scaleControl = L.control.scale({
    imperial: false,
    position: 'bottomright'
  });
  
  // Adiciona controles quando o mapa estiver pronto
  map.whenReady(function() {
    scaleControl.addTo(map);
    updateGraticule();
    updateEscalaNumerica();
    moveLeafletScaleBar();
  });
}

function configurarEventosMapa() {
  // Eventos de zoom e movimento
  map.on('zoomend moveend', function() {
    updateGraticule();
    updateEscalaNumerica();
    moveLeafletScaleBar();
  });
  
  // Evento de redimensionamento da janela
  window.addEventListener('resize', function() {
    updateEscalaNumerica();
  });
}

// ==================== FUNÇÕES DO BASEMAP ====================

function trocarBasemap() {
  const basemapSelect = document.getElementById('basemapSelect');
  if (!basemapSelect || !map) return;
  
  // Remove camadas existentes
  for (let key in baseLayers) {
    if (baseLayers.hasOwnProperty(key) && map.hasLayer(baseLayers[key])) {
      map.removeLayer(baseLayers[key]);
    }
  }
  
  // Adiciona nova camada
  const selectedValue = basemapSelect.value;
  baseLayers[selectedValue].addTo(map);
  
  // Controla máscara de opacidade
  const mapMask = document.getElementById('mapMask');
  if (mapMask) {
    mapMask.style.display = (selectedValue === 'opaco') ? 'block' : 'none';
  }
}

// ==================== FUNÇÕES DO GRID/GRATÍCULA ====================

function updateGraticule() {
  if (!map) return;
  
  // Verifica se o plugin está disponível
  if (typeof L.graticule !== 'function') {
    console.warn("Leaflet Graticule plugin não está carregado");
    return;
  }
  
  // Remove gratícula existente
  if (graticule && map.hasLayer(graticule)) {
    map.removeLayer(graticule);
    graticule = null;
  }
  
  // Adiciona gratícula em zooms maiores
  if (map.getZoom() >= 6) {
    graticule = L.graticule({
      interval: 0.5,
      style: {
        color: '#b0b0b0',
        weight: 0.7,
        opacity: 0.7
      }
    }).addTo(map);
  }
}

// ==================== FUNÇÕES DA ESCALA ====================

function moveLeafletScaleBar() {
  if (!map) return;
  
  const scaleBarElement = document.querySelector('.leaflet-control-scale');
  const targetContainer = document.getElementById('leafletScaleBar');
  
  if (scaleBarElement && targetContainer) {
    if (targetContainer.childElementCount === 0) {
      targetContainer.appendChild(scaleBarElement);
    }
    scaleBarElement.style.display = 'block';
  }
}

function updateEscalaNumerica() {
  if (!map) return;
  
  const center = map.getCenter();
  const zoom = map.getZoom();
  const mapContainer = document.getElementById('mapCroqui');
  
  if (!mapContainer) return;
  
  const metersPerPixel = 156543.03392 * Math.cos(center.lat * Math.PI / 180) / Math.pow(2, zoom);
  const widthPx = mapContainer.offsetWidth;
  let escalaAprox = Math.round(metersPerPixel * widthPx) / (widthPx / 1000);
  
  // Arredonda para valores mais legíveis
  let escalaFinal;
  if (escalaAprox > 1000) {
    escalaFinal = Math.round(escalaAprox / 1000) * 1000;
  } else if (escalaAprox > 100) {
    escalaFinal = Math.round(escalaAprox / 100) * 100;
  } else if (escalaAprox > 10) {
    escalaFinal = Math.round(escalaAprox / 10) * 10;
  } else {
    escalaFinal = Math.round(escalaAprox);
  }
  
  const escalaNumericaEl = document.getElementById('escalaNumerica');
  if (escalaNumericaEl) {
    escalaNumericaEl.textContent = 'Escala 1:' + escalaFinal.toLocaleString('pt-BR');
  }
}

// ==================== FUNÇÕES PÚBLICAS PARA INTEGRAÇÃO ====================

function adicionarGeometriaAoMapa(geometriaData) {
  if (!map || !geometriaData) return;
  
  try {
    const layer = L.geoJSON(geometriaData, {
      style: {
        color: '#ff7800',
        weight: 3,
        opacity: 0.8
      }
    });
    
    layer.addTo(map);
    map.fitBounds(layer.getBounds());
    
    return layer;
  } catch (error) {
    console.error('Erro ao adicionar geometria ao mapa:', error);
    return null;
  }
}

function centralizarMapa(lat, lng, zoom = 13) {
  if (map) {
    map.setView([lat, lng], zoom);
  }
}

function obterBounds() {
  return map ? map.getBounds() : null;
}

// Exporta funções para uso global
window.MapaCroqui = {
  adicionarGeometria: adicionarGeometriaAoMapa,
  centralizar: centralizarMapa,
  obterBounds: obterBounds,
  mapa: () => map
};
