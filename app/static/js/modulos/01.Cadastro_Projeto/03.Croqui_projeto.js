// ==================== INICIALIZAÇÃO DO MAPA ====================
let map;
let baseLayers = {};

document.addEventListener('DOMContentLoaded', function() {
    initializeMap();
});

function initializeMap() {
    // Verificar se o elemento do mapa existe
    const mapElement = document.getElementById('mapCroqui');
    if (!mapElement) {
        console.warn('Elemento #mapCroqui não encontrado');
        return;
    }

    try {
        // Inicializar o mapa centrado no Brasil (São Paulo)
        map = L.map('mapCroqui').setView([-23.5505, -46.6333], 10);

        // Definir as camadas base
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

        // Adicionar a camada padrão
        baseLayers['osm'].addTo(map);

        // Configurar o seletor de basemap
        setupBasemapSelector();

        // Configurar controles do mapa
        setupMapControls();

        console.log('Mapa inicializado com sucesso');

    } catch (error) {
        console.error('Erro ao inicializar o mapa:', error);
    }
}

function setupBasemapSelector() {
    const basemapSelect = document.getElementById('basemapSelect');
    if (!basemapSelect) return;

    basemapSelect.addEventListener('change', function() {
        if (!map) return;

        // Remover a camada atual
        for (let key in baseLayers) {
            if (baseLayers.hasOwnProperty(key) && map.hasLayer(baseLayers[key])) {
                map.removeLayer(baseLayers[key]);
            }
        }

        // Adicionar a nova camada
        const selectedValue = this.value;
        if (baseLayers[selectedValue]) {
            baseLayers[selectedValue].addTo(map);
        }

        // Controlar a máscara de opacidade
        const mapMask = document.getElementById('mapMask');
        if (mapMask) {
            mapMask.style.display = (selectedValue === 'opaco') ? 'block' : 'none';
        }
    });
}

function setupMapControls() {
    if (!map) return;

    // Adicionar controle de escala
    const scaleControl = L.control.scale({
        imperial: false,
        position: 'bottomright'
    });    map.whenReady(function() {
        scaleControl.addTo(map);
        updateGraticule();
        updateEscalaNumerica();
        moveLeafletScaleBar();
    });

    // Eventos do mapa
    map.on('zoomend moveend', function() {
        updateGraticule();
        updateEscalaNumerica();
        moveLeafletScaleBar();
    });
}

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
    const escalaAprox = Math.round(metersPerPixel * widthPx) / (widthPx / 1000);
    
    let escalaFinal = escalaAprox;
    if (escalaAprox > 1000) escalaFinal = Math.round(escalaAprox/1000)*1000;
    else if (escalaAprox > 100) escalaFinal = Math.round(escalaAprox/100)*100;
    else if (escalaAprox > 10) escalaFinal = Math.round(escalaAprox/10)*10;
    else escalaFinal = Math.round(escalaFinal);
    
    const escalaNumericaEl = document.getElementById('escalaNumerica');
    if (escalaNumericaEl) {
        escalaNumericaEl.innerText = 'Escala 1:' + escalaFinal.toLocaleString('pt-BR');
    }
}

// Função para redimensionar o mapa quando necessário
window.addEventListener('resize', function(){
    if (map) {
        map.invalidateSize();
        updateEscalaNumerica();
    }
});

// ==================== FUNÇÕES AUXILIARES ====================

// Função para obter a instância do mapa (para uso em outros módulos)
function getMapInstance() {
    return map;
}

// Função para adicionar uma camada ao mapa
function addLayerToMap(layer) {
    if (map && layer) {
        layer.addTo(map);
    }
}

// Função para remover uma camada do mapa
function removeLayerFromMap(layer) {
    if (map && layer) {
        map.removeLayer(layer);
    }
}

// ==================== GRATICULE (GRID DE COORDENADAS) ====================
let graticule = null;

function updateGraticule() {
    if (!map) return;
    
    // Verificar se o plugin está disponível
    if (typeof L.graticule !== 'function') {
        console.warn("Leaflet Graticule plugin não está carregado.");
        return;
    }
    
    // Remover graticule existente
    if (graticule && map.hasLayer(graticule)) {
        map.removeLayer(graticule);
        graticule = null;
    }
    
    // Adicionar graticule apenas em zooms maiores
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
