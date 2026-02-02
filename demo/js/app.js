// Ecomarine API Demo - JavaScript Application
// Handles all interactive functionality for the demo

// Global configuration
const CONFIG = {
    // API Base URL - Update this with your actual API URL when deployed
    API_BASE_URL: 'http://localhost:8000', // Change this to your deployed API URL
    // RapidAPI specific settings
    RAPIDAPI_HOST: 'your-api-host.rapidapi.com', // Update with your RapidAPI host
    // Map settings
    DEFAULT_CENTER: [20, 0],
    DEFAULT_ZOOM: 2,
    ECA_ZONES: {
        'North Sea SECA': { color: '#e74c3c', fillColor: '#e74c3c', fillOpacity: 0.2 },
        'Baltic Sea SECA': { color: '#3498db', fillColor: '#3498db', fillOpacity: 0.2 },
        'Mediterranean ECA': { color: '#2ecc71', fillColor: '#2ecc71', fillOpacity: 0.2 },
        'United States Caribbean ECA': { color: '#f39c12', fillColor: '#f39c12', fillOpacity: 0.2 },
        'North American ECA 1': { color: '#9b59b6', fillColor: '#9b59b6', fillOpacity: 0.2 },
        'North American ECA 2': { color: '#1abc9c', fillColor: '#1abc9c', fillOpacity: 0.2 },
        'North American ECA 3': { color: '#e67e22', fillColor: '#e67e22', fillOpacity: 0.2 }
    }
};

// Global state
let apiKey = localStorage.getItem('ecomarine_api_key') || '';
let maps = {};
let markers = {};
let polylines = {};
let zonePolygons = {};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initApiKeyManager();
    initCodeTabs();
    initNavigation();
});

// API Key Management
function initApiKeyManager() {
    const apiKeyInput = document.getElementById('api-key');
    const saveButton = document.getElementById('save-api-key');
    const statusIndicator = document.getElementById('api-status');
    
    if (apiKeyInput) {
        apiKeyInput.value = apiKey;
        updateApiStatus();
    }
    
    if (saveButton) {
        saveButton.addEventListener('click', function() {
            apiKey = apiKeyInput.value.trim();
            localStorage.setItem('ecomarine_api_key', apiKey);
            updateApiStatus();
            showMessage('API key saved successfully!', 'success');
        });
    }
    
    function updateApiStatus() {
        if (statusIndicator) {
            if (apiKey) {
                statusIndicator.classList.add('active');
                statusIndicator.title = 'API Key Configured';
            } else {
                statusIndicator.classList.remove('active');
                statusIndicator.title = 'API Key Not Set';
            }
        }
    }
}

// Code Tabs
function initCodeTabs() {
    document.querySelectorAll('.code-tabs').forEach(tabContainer => {
        const buttons = tabContainer.querySelectorAll('.tab-btn');
        const content = tabContainer.nextElementSibling;
        
        buttons.forEach(button => {
            button.addEventListener('click', function() {
                const tabName = this.getAttribute('data-tab');
                
                // Update buttons
                buttons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');
                
                // Update content
                if (content) {
                    content.querySelectorAll('.code-block').forEach(block => {
                        block.classList.remove('active');
                    });
                    const targetBlock = content.querySelector(`#${tabName}-code`);
                    if (targetBlock) {
                        targetBlock.classList.add('active');
                    }
                }
            });
        });
    });
}

// Navigation
function initNavigation() {
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPage) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

// Copy Code Function
function copyCode(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        const text = element.textContent;
        navigator.clipboard.writeText(text).then(() => {
            showMessage('Copied to clipboard!', 'success');
        }).catch(() => {
            showMessage('Failed to copy', 'error');
        });
    }
}

// Show Message
function showMessage(message, type = 'info') {
    // Remove existing messages
    document.querySelectorAll('.message').forEach(msg => msg.remove());
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = message;
    
    const container = document.querySelector('.demo-content');
    if (container) {
        container.insertBefore(messageDiv, container.firstChild);
        
        setTimeout(() => {
            messageDiv.remove();
        }, 3000);
    }
}

// ========== ROUTE CALCULATOR ==========
function initRouteCalculator() {
    const map = initMap('route-map');
    maps.route = map;
    
    let originMarker = null;
    let destMarker = null;
    let routeLine = null;
    let clickMode = null; // 'origin' or 'dest'
    
    // Port selection handlers
    document.getElementById('origin-port')?.addEventListener('change', function() {
        if (this.value) {
            const [lat, lon] = this.value.split(',');
            document.getElementById('origin-lat').value = lat;
            document.getElementById('origin-lon').value = lon;
            setOriginMarker(parseFloat(lat), parseFloat(lon));
        }
    });
    
    document.getElementById('dest-port')?.addEventListener('change', function() {
        if (this.value) {
            const [lat, lon] = this.value.split(',');
            document.getElementById('dest-lat').value = lat;
            document.getElementById('dest-lon').value = lon;
            setDestMarker(parseFloat(lat), parseFloat(lon));
        }
    });
    
    // Map click handlers
    document.getElementById('set-origin-map')?.addEventListener('click', function() {
        clickMode = 'origin';
        showMessage('Click on the map to set origin', 'info');
        map.getContainer().style.cursor = 'crosshair';
    });
    
    document.getElementById('set-dest-map')?.addEventListener('click', function() {
        clickMode = 'dest';
        showMessage('Click on the map to set destination', 'info');
        map.getContainer().style.cursor = 'crosshair';
    });
    
    map.on('click', function(e) {
        if (clickMode === 'origin') {
            const lat = e.latlng.lat.toFixed(4);
            const lon = e.latlng.lng.toFixed(4);
            document.getElementById('origin-lat').value = lat;
            document.getElementById('origin-lon').value = lon;
            setOriginMarker(parseFloat(lat), parseFloat(lon));
            clickMode = null;
            map.getContainer().style.cursor = '';
        } else if (clickMode === 'dest') {
            const lat = e.latlng.lat.toFixed(4);
            const lon = e.latlng.lng.toFixed(4);
            document.getElementById('dest-lat').value = lat;
            document.getElementById('dest-lon').value = lon;
            setDestMarker(parseFloat(lat), parseFloat(lon));
            clickMode = null;
            map.getContainer().style.cursor = '';
        }
    });
    
    function setOriginMarker(lat, lon) {
        if (originMarker) map.removeLayer(originMarker);
        originMarker = L.marker([lat, lon], {
            icon: createCustomIcon('🟢', 'origin')
        }).addTo(map);
        originMarker.bindPopup('<b>Origin</b><br>Lat: ' + lat + '<br>Lon: ' + lon).openPopup();
        markers.origin = originMarker;
    }
    
    function setDestMarker(lat, lon) {
        if (destMarker) map.removeLayer(destMarker);
        destMarker = L.marker([lat, lon], {
            icon: createCustomIcon('🔴', 'dest')
        }).addTo(map);
        destMarker.bindPopup('<b>Destination</b><br>Lat: ' + lat + '<br>Lon: ' + lon).openPopup();
        markers.dest = destMarker;
    }
    
    // Calculate route
    document.getElementById('calculate-route')?.addEventListener('click', calculateRoute);
    
    async function calculateRoute() {
        const originLat = parseFloat(document.getElementById('origin-lat').value);
        const originLon = parseFloat(document.getElementById('origin-lon').value);
        const destLat = parseFloat(document.getElementById('dest-lat').value);
        const destLon = parseFloat(document.getElementById('dest-lon').value);
        
        if (!originLat || !originLon || !destLat || !destLon) {
            showMessage('Please enter both origin and destination coordinates', 'error');
            return;
        }
        
        // Get restrictions
        const restrictions = [];
        document.querySelectorAll('.checkbox-group input:checked').forEach(cb => {
            restrictions.push(cb.value);
        });
        
        const requestBody = {
            origin: [originLat, originLon],
            destination: [destLat, destLon],
            restrictions: restrictions,
            include_explanation: false
        };
        
        // Display request
        updateCodeDisplay('request', JSON.stringify(requestBody, null, 2));
        
        // Build curl command
        const curlCmd = `curl -X POST "${CONFIG.API_BASE_URL}/calculate_route" \\
-H "Content-Type: application/json" \\
-H "X-RapidAPI-Key: ${apiKey || 'YOUR_API_KEY'}" \\
-H "X-RapidAPI-Host: ${CONFIG.RAPIDAPI_HOST}" \\
-d '${JSON.stringify(requestBody)}'`;
        updateCodeDisplay('curl', curlCmd);
        
        try {
            showMessage('Calculating route...', 'info');
            
            const headers = {
                'Content-Type': 'application/json'
            };
            
            if (apiKey) {
                headers['X-RapidAPI-Key'] = apiKey;
                headers['X-RapidAPI-Host'] = CONFIG.RAPIDAPI_HOST;
            }
            
            const response = await fetch(`${CONFIG.API_BASE_URL}/calculate_route`, {
                method: 'POST',
                headers: headers,
                body: JSON.stringify(requestBody)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Display response
            updateCodeDisplay('response', JSON.stringify(data, null, 2));
            
            // Update results
            displayRouteResults(data);
            
            // Draw route on map
            drawRoute(data.waypoints);
            
            showMessage('Route calculated successfully!', 'success');
            
        } catch (error) {
            showMessage('Error: ' + error.message, 'error');
            updateCodeDisplay('response', `Error: ${error.message}`);
        }
    }
    
    function displayRouteResults(data) {
        const resultsContainer = document.getElementById('route-results');
        if (resultsContainer) {
            resultsContainer.style.display = 'block';
            
            document.getElementById('total-distance').textContent = data.distance_nm?.toFixed(2) || '-';
            document.getElementById('eca-distance').textContent = data.eca_distance_nm?.toFixed(2) || '0';
            document.getElementById('traversed-passage').textContent = data.traversed_passage || 'None';
            
            // Calculate percentage
            const percentage = data.distance_nm > 0 
                ? ((data.eca_distance_nm || 0) / data.distance_nm * 100).toFixed(1)
                : 0;
            document.getElementById('eca-percentage').textContent = percentage;
            
            // Update progress bar
            const progressBar = document.getElementById('eca-progress');
            const barText = document.getElementById('eca-bar-text');
            if (progressBar) {
                progressBar.style.width = percentage + '%';
            }
            if (barText) {
                barText.textContent = percentage + '% in ECA zones';
            }
            
            // Scroll to results
            resultsContainer.scrollIntoView({ behavior: 'smooth' });
        }
    }
    
    function drawRoute(waypoints) {
        if (routeLine) map.removeLayer(routeLine);
        
        if (waypoints && waypoints.length > 0) {
            routeLine = L.polyline(waypoints, {
                color: '#3182ce',
                weight: 4,
                opacity: 0.8
            }).addTo(map);
            
            map.fitBounds(routeLine.getBounds(), { padding: [50, 50] });
        }
    }
    
    // Clear route
    document.getElementById('clear-route')?.addEventListener('click', function() {
        if (routeLine) map.removeLayer(routeLine);
        if (originMarker) map.removeLayer(originMarker);
        if (destMarker) map.removeLayer(destMarker);
        
        document.getElementById('origin-lat').value = '';
        document.getElementById('origin-lon').value = '';
        document.getElementById('dest-lat').value = '';
        document.getElementById('dest-lon').value = '';
        document.getElementById('origin-port').value = '';
        document.getElementById('dest-port').value = '';
        document.querySelectorAll('.checkbox-group input:checked').forEach(cb => cb.checked = false);
        
        document.getElementById('route-results').style.display = 'none';
        
        map.setView(CONFIG.DEFAULT_CENTER, CONFIG.DEFAULT_ZOOM);
        
        showMessage('Route cleared', 'info');
    });
    
    // Fit bounds
    document.getElementById('fit-bounds')?.addEventListener('click', function() {
        if (routeLine) {
            map.fitBounds(routeLine.getBounds(), { padding: [50, 50] });
        } else if (originMarker && destMarker) {
            const group = new L.featureGroup([originMarker, destMarker]);
            map.fitBounds(group.getBounds(), { padding: [50, 50] });
        }
    });
}

// ========== ZONE CHECKER ==========
function initZoneChecker() {
    const map = initMap('zone-map');
    maps.zone = map;
    
    let checkMarker = null;
    
    // Preset buttons
    document.querySelectorAll('.preset-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const lat = this.getAttribute('data-lat');
            const lon = this.getAttribute('data-lon');
            document.getElementById('check-lat').value = lat;
            document.getElementById('check-lon').value = lon;
            checkPoint();
        });
    });
    
    // Check button
    document.getElementById('check-point')?.addEventListener('click', checkPoint);
    
    // Map click
    map.on('click', function(e) {
        const lat = e.latlng.lat.toFixed(4);
        const lon = e.latlng.lng.toFixed(4);
        document.getElementById('check-lat').value = lat;
        document.getElementById('check-lon').value = lon;
        checkPoint();
    });
    
    async function checkPoint() {
        const lat = parseFloat(document.getElementById('check-lat').value);
        const lon = parseFloat(document.getElementById('check-lon').value);
        
        if (isNaN(lat) || isNaN(lon)) {
            showMessage('Please enter valid coordinates', 'error');
            return;
        }
        
        // Update marker
        if (checkMarker) map.removeLayer(checkMarker);
        checkMarker = L.marker([lat, lon]).addTo(map);
        checkMarker.bindPopup('Checking...').openPopup();
        
        // Build URL
        const url = `${CONFIG.API_BASE_URL}/check-point?latitude=${lat}&longitude=${lon}`;
        
        // Display request
        updateCodeDisplay('request', `GET ${url}`);
        
        // Build curl command
        const curlCmd = `curl "${url}" \\
-H "X-RapidAPI-Key: ${apiKey || 'YOUR_API_KEY'}" \\
-H "X-RapidAPI-Host: ${CONFIG.RAPIDAPI_HOST}"`;
        updateCodeDisplay('curl', curlCmd);
        
        try {
            const headers = {};
            if (apiKey) {
                headers['X-RapidAPI-Key'] = apiKey;
                headers['X-RapidAPI-Host'] = CONFIG.RAPIDAPI_HOST;
            }
            
            const response = await fetch(url, { headers });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Display response
            updateCodeDisplay('response', JSON.stringify(data, null, 2));
            
            // Update UI
            displayZoneResult(data, lat, lon);
            
        } catch (error) {
            showMessage('Error: ' + error.message, 'error');
            updateCodeDisplay('response', `Error: ${error.message}`);
        }
    }
    
    function displayZoneResult(data, lat, lon) {
        const resultPanel = document.getElementById('zone-result');
        const insideEca = document.getElementById('inside-eca');
        const outsideEca = document.getElementById('outside-eca');
        const zoneDetails = document.getElementById('zone-details');
        
        if (resultPanel) {
            resultPanel.style.display = 'block';
            
            if (data.inside_eca) {
                insideEca.style.display = 'flex';
                outsideEca.style.display = 'none';
                zoneDetails.style.display = 'block';
                
                // Update details
                document.getElementById('zone-name').textContent = data.zone_name || '-';
                document.getElementById('zone-type').textContent = data.zone_type || '-';
                document.getElementById('sulphur-limit').textContent = data.required_sulphur || '-';
                document.getElementById('regulation').textContent = data.regulation || '-';
                document.getElementById('territory').textContent = data.territory || '-';
                
                // Update marker popup
                checkMarker.setPopupContent(`
                    <b>${data.zone_name}</b><br>
                    Type: ${data.zone_type}<br>
                    Sulphur: ${data.required_sulphur}
                `);
                
                // Add zone color to marker
                const zoneStyle = CONFIG.ECA_ZONES[data.zone_name];
                if (zoneStyle) {
                    checkMarker.setIcon(createColoredMarkerIcon(zoneStyle.color));
                }
                
            } else {
                insideEca.style.display = 'none';
                outsideEca.style.display = 'flex';
                zoneDetails.style.display = 'none';
                
                checkMarker.setPopupContent('<b>Outside all ECA zones</b>');
            }
            
            resultPanel.scrollIntoView({ behavior: 'smooth' });
        }
    }
    
    // Clear markers
    document.getElementById('clear-markers')?.addEventListener('click', function() {
        if (checkMarker) map.removeLayer(checkMarker);
        checkMarker = null;
        document.getElementById('zone-result').style.display = 'none';
        document.getElementById('check-lat').value = '';
        document.getElementById('check-lon').value = '';
    });
    
    // Show all zones (simplified bounding boxes)
    document.getElementById('show-all-zones')?.addEventListener('click', function() {
        showAllEcaZones(map);
    });
}

// ========== SUPPORTED ZONES ==========
function initSupportedZones() {
    const map = initMap('zones-map');
    maps.zones = map;
    
    // Load zones on page load
    loadSupportedZones();
    
    // Refresh button
    document.getElementById('refresh-zones')?.addEventListener('click', loadSupportedZones);
    
    async function loadSupportedZones() {
        const url = `${CONFIG.API_BASE_URL}/supported-zones`;
        
        // Display request
        updateCodeDisplay('request', `GET ${url}`);
        
        // Build curl command
        const curlCmd = `curl "${url}" \\
-H "X-RapidAPI-Key: ${apiKey || 'YOUR_API_KEY'}" \\
-H "X-RapidAPI-Host: ${CONFIG.RAPIDAPI_HOST}"`;
        updateCodeDisplay('curl', curlCmd);
        
        try {
            const headers = {};
            if (apiKey) {
                headers['X-RapidAPI-Key'] = apiKey;
                headers['X-RapidAPI-Host'] = CONFIG.RAPIDAPI_HOST;
            }
            
            const response = await fetch(url, { headers });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Display response
            updateCodeDisplay('response', JSON.stringify(data, null, 2));
            
            // Update UI
            displayZonesTable(data.zones);
            displayZonesOnMap(data.zones, map);
            
            // Update stats
            document.getElementById('total-zones').textContent = data.count || 0;
            document.getElementById('active-zones').textContent = data.count || 0;
            
        } catch (error) {
            showMessage('Error loading zones: ' + error.message, 'error');
            updateCodeDisplay('response', `Error: ${error.message}`);
        }
    }
    
    function displayZonesTable(zones) {
        const tbody = document.getElementById('zones-tbody');
        if (!tbody) return;
        
        tbody.innerHTML = '';
        
        if (!zones || zones.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="loading">No zones available</td></tr>';
            return;
        }
        
        zones.forEach(zone => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td><strong>${zone.name}</strong></td>
                <td><span class="sulphur-badge ${zone.type === 'seca' ? 'low' : 'medium'}">${zone.type}</span></td>
                <td>${zone.required_sulphur || '-'}</td>
                <td>${zone.regulation || '-'}</td>
                <td>${zone.territory || '-'}</td>
                <td>${zone.year_established || '-'}</td>
            `;
            
            row.addEventListener('click', () => showZoneDetail(zone));
            tbody.appendChild(row);
        });
    }
    
    function showZoneDetail(zone) {
        const detailCard = document.getElementById('zone-detail-card');
        if (!detailCard) return;
        
        detailCard.style.display = 'block';
        
        document.getElementById('detail-name').textContent = zone.name;
        document.getElementById('detail-type').textContent = zone.type || '-';
        document.getElementById('detail-sulphur').textContent = zone.required_sulphur || '-';
        document.getElementById('detail-regulation').textContent = zone.regulation || '-';
        document.getElementById('detail-territory').textContent = zone.territory || '-';
        document.getElementById('detail-year').textContent = zone.year_established || '-';
        document.getElementById('detail-status').textContent = zone.status || 'active';
        
        if (zone.bounding_box) {
            document.getElementById('bbox-min-lat').textContent = zone.bounding_box.min_lat || '-';
            document.getElementById('bbox-max-lat').textContent = zone.bounding_box.max_lat || '-';
            document.getElementById('bbox-min-lon').textContent = zone.bounding_box.min_lon || '-';
            document.getElementById('bbox-max-lon').textContent = zone.bounding_box.max_lon || '-';
        }
        
        detailCard.scrollIntoView({ behavior: 'smooth' });
    }
}

// ========== HELPER FUNCTIONS ==========

function initMap(mapId) {
    const mapElement = document.getElementById(mapId);
    if (!mapElement) return null;
    
    const map = L.map(mapId).setView(CONFIG.DEFAULT_CENTER, CONFIG.DEFAULT_ZOOM);
    
    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 18
    }).addTo(map);
    
    return map;
}

function createCustomIcon(emoji, type) {
    return L.divIcon({
        className: 'custom-marker',
        html: `<div style="font-size: 24px; filter: drop-shadow(2px 2px 2px rgba(0,0,0,0.3));">${emoji}</div>`,
        iconSize: [30, 30],
        iconAnchor: [15, 15]
    });
}

function createColoredMarkerIcon(color) {
    return L.divIcon({
        className: 'colored-marker',
        html: `<div style="width: 20px; height: 20px; background: ${color}; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.3);"></div>`,
        iconSize: [20, 20],
        iconAnchor: [10, 10]
    });
}

function updateCodeDisplay(type, content) {
    const codeBlock = document.getElementById(`${type}-code`);
    if (codeBlock) {
        const codeElement = codeBlock.querySelector('code') || codeBlock;
        codeElement.textContent = content;
    }
}

function showAllEcaZones(map) {
    // Clear existing polygons
    Object.values(zonePolygons).forEach(polygon => map.removeLayer(polygon));
    zonePolygons = {};
    
    // Simplified ECA zone bounding boxes for visualization
    const zoneBoundaries = {
        'North Sea SECA': [[50, -5], [50, 10], [62, 10], [62, -5]],
        'Baltic Sea SECA': [[53, 9], [53, 30], [66, 30], [66, 9]],
        'Mediterranean ECA': [[30, -6], [30, 37], [46, 37], [46, -6]],
        'United States Caribbean ECA': [[16, -90], [16, -58], [24, -58], [24, -90]],
        'North American ECA 1': [[24, -82], [24, -60], [46, -60], [46, -82]],
        'North American ECA 2': [[32, -130], [32, -116], [50, -116], [50, -130]],
        'North American ECA 3': [[24, -98], [24, -80], [31, -80], [31, -98]]
    };
    
    Object.entries(zoneBoundaries).forEach(([name, bounds]) => {
        const style = CONFIG.ECA_ZONES[name];
        if (style) {
            const polygon = L.polygon(bounds, {
                color: style.color,
                fillColor: style.fillColor,
                fillOpacity: style.fillOpacity,
                weight: 2
            }).addTo(map);
            
            polygon.bindPopup(`<b>${name}</b>`);
            zonePolygons[name] = polygon;
        }
    });
    
    showMessage('ECA zones displayed on map', 'success');
}

function displayZonesOnMap(zones, map) {
    // Clear existing
    Object.values(zonePolygons).forEach(polygon => map.removeLayer(polygon));
    zonePolygons = {};
    
    if (!zones) return;
    
    zones.forEach(zone => {
        if (zone.bounding_box) {
            const bb = zone.bounding_box;
            const bounds = [
                [bb.min_lat, bb.min_lon],
                [bb.min_lat, bb.max_lon],
                [bb.max_lat, bb.max_lon],
                [bb.max_lat, bb.min_lon]
            ];
            
            const style = CONFIG.ECA_ZONES[zone.name] || { color: '#999', fillColor: '#999', fillOpacity: 0.2 };
            
            const polygon = L.polygon(bounds, {
                color: style.color,
                fillColor: style.fillColor,
                fillOpacity: style.fillOpacity,
                weight: 2
            }).addTo(map);
            
            polygon.bindPopup(`
                <b>${zone.name}</b><br>
                Type: ${zone.type}<br>
                Sulphur: ${zone.required_sulphur}
            `);
            
            zonePolygons[zone.name] = polygon;
        }
    });
}

// Expose functions globally for onclick handlers
window.copyCode = copyCode;
window.initRouteCalculator = initRouteCalculator;
window.initZoneChecker = initZoneChecker;
window.initSupportedZones = initSupportedZones;
