/**
 * Mind Reader AI Dashboard JavaScript
 * Handles all dashboard interactions and API communication
 */

// Configuration
const API_BASE_URL = 'http://localhost:5000/api';
let authToken = localStorage.getItem('authToken');
let analysisHistory = [];

/**
 * Initialize dashboard on page load
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('🧠 Mind Reader AI Dashboard Initialized');
    
    // Check authentication
    if (!authToken) {
        authenticate();
    } else {
        initializeDashboard();
    }
});

/**
 * Authenticate user and get JWT token
 */
async function authenticate() {
    try {
        showSpinner('authentication');
        
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: 'dashboard_user'
            })
        });

        if (!response.ok) throw new Error('Authentication failed');

        const data = await response.json();
        authToken = data.access_token;
        localStorage.setItem('authToken', authToken);
        
        showToast('✅ Authentication successful', 'success');
        initializeDashboard();
    } catch (error) {
        console.error('❌ Authentication error:', error);
        showToast('❌ Authentication failed: ' + error.message, 'error');
    }
}

/**
 * Initialize dashboard after authentication
 */
function initializeDashboard() {
    console.log('✅ Dashboard ready');
    checkSystemHealth();
    loadHistory();
    refreshStats();
}

/**
 * Check system health
 */
async function checkSystemHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            const data = await response.json();
            console.log('🟢 System Health:', data);
            document.getElementById('systemStatus').textContent = 'Online';
        }
    } catch (error) {
        console.error('❌ Health check failed:', error);
        document.getElementById('systemStatus').textContent = 'Offline';
    }
}

/**
 * Analyze text based on selected type
 */
async function analyzeText() {
    const text = document.getElementById('analysisText').value.trim();
    const analysisType = document.getElementById('analysisType').value;

    if (!text) {
        showToast('⚠️ Please enter text to analyze', 'warning');
        return;
    }

    try {
        showSpinner('analysisSpinner');

        const endpoint = analysisType === 'comprehensive' 
            ? '/analyze/comprehensive' 
            : `/analyze/${analysisType}`;

        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ text })
        });

        if (!response.ok) throw new Error(`Analysis failed: ${response.statusText}`);

        const result = await response.json();
        hideSpinner('analysisSpinner');
        displayResults(result, 'analysisResults');
        
        showToast('✅ Analysis complete', 'success');
    } catch (error) {
        hideSpinner('analysisSpinner');
        console.error('❌ Analysis error:', error);
        showToast('❌ Analysis failed: ' + error.message, 'error');
    }
}

/**
 * Batch analyze multiple texts
 */
async function analyzeBatch() {
    let texts = document.getElementById('batchTexts').value.trim().split('\n');
    texts = texts.filter(t => t.trim().length > 0);

    if (texts.length === 0) {
        showToast('⚠️ Please enter texts to analyze', 'warning');
        return;
    }

    try {
        showSpinner('batchSpinner');

        const response = await fetch(`${API_BASE_URL}/batch/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                texts: texts,
                analysis_type: 'comprehensive'
            })
        });

        if (!response.ok) throw new Error('Batch analysis failed');

        const result = await response.json();
        hideSpinner('batchSpinner');
        displayBatchResults(result, 'batchResults');
        
        showToast(`✅ Analyzed ${result.batch_size} texts`, 'success');
    } catch (error) {
        hideSpinner('batchSpinner');
        console.error('❌ Batch analysis error:', error);
        showToast('❌ Batch analysis failed: ' + error.message, 'error');
    }
}

/**
 * Advanced analysis with multiple features
 */
async function analyzeAdvanced() {
    const text = document.getElementById('advancedText').value.trim();
    
    if (!text) {
        showToast('⚠️ Please enter text', 'warning');
        return;
    }

    try {
        showSpinner('advancedSpinner');

        const response = await fetch(`${API_BASE_URL}/analyze/comprehensive`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                text,
                metadata: {
                    includeAnomaly: document.getElementById('includeAnomaly').checked,
                    includeSentiment: document.getElementById('includeSentiment').checked,
                    includeComplexity: document.getElementById('includeComplexity').checked
                }
            })
        });

        if (!response.ok) throw new Error('Advanced analysis failed');

        const result = await response.json();
        hideSpinner('advancedSpinner');
        displayAdvancedResults(result, 'advancedResults');
        
        showToast('✅ Advanced analysis complete', 'success');
    } catch (error) {
        console.error('❌ Advanced analysis error:', error);
        showToast('❌ Analysis failed: ' + error.message, 'error');
    }
}

/**
 * Load analysis history
 */
async function loadHistory() {
    try {
        const response = await fetch(`${API_BASE_URL}/history?limit=25`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (!response.ok) throw new Error('Failed to load history');

        const data = await response.json();
        analysisHistory = data.history || [];
        
        displayHistory(analysisHistory);
    } catch (error) {
        console.error('❌ History load error:', error);
        showToast('❌ Could not load history: ' + error.message, 'error');
    }
}

/**
 * Refresh system statistics
 */
async function refreshStats() {
    try {
        // Get summary stats
        const statsResponse = await fetch(`${API_BASE_URL}/stats/summary`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (statsResponse.ok) {
            const statsData = await statsResponse.json();
            const stats = statsData.statistics || {};
            
            document.getElementById('totalAnalyses').textContent = 
                stats.total_analyses || '0';
        }

        // Get performance metrics
        const perfResponse = await fetch(`${API_BASE_URL}/stats/performance`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (perfResponse.ok) {
            const perfData = perfResponse.json();
            const metrics = perfData.metrics || {};
            
            document.getElementById('cacheHitRate').textContent = 
                ((metrics.cache_hit_rate || 0) * 100).toFixed(1) + '%';
            document.getElementById('avgResponseTime').textContent = 
                (metrics.avg_response_time || 0).toFixed(0) + 'ms';
        }

        showToast('✅ Statistics updated', 'success');
    } catch (error) {
        console.error('❌ Stats refresh error:', error);
        showToast('❌ Could not refresh stats: ' + error.message, 'error');
    }
}

/**
 * Display analysis results
 */
function displayResults(result, containerId) {
    const container = document.getElementById(containerId);
    
    if (result.status === 'success') {
        const analysis = result.analysis || result.emotion || result.personality || result.deception_analysis;
        
        let html = '<div class="result-box">';
        html += '<h6><i class="fas fa-check-circle"></i> Analysis Results</h6>';
        
        if (typeof analysis === 'object') {
            for (const [key, value] of Object.entries(analysis)) {
                html += `<div class="metric">`;
                html += `<span class="metric-label">${formatKey(key)}</span>`;
                html += `<span class="metric-value">${formatValue(value)}</span>`;
                html += `</div>`;
            }
        } else {
            html += `<p>${analysis}</p>`;
        }
        
        html += '</div>';
        container.innerHTML = html;
    } else {
        container.innerHTML = `<div class="alert alert-warning">
            <i class="fas fa-exclamation-triangle"></i> ${result.error || 'Analysis failed'}
        </div>`;
    }
}

/**
 * Display batch analysis results
 */
function displayBatchResults(result, containerId) {
    const container = document.getElementById(containerId);
    
    if (result.status === 'success') {
        const results = result.results || [];
        
        let html = '<div class="result-box">';
        html += `<h6><i class="fas fa-layer-group"></i> Batch Results (${results.length} items)</h6>`;
        html += '<div class="table-responsive">';
        html += '<table class="table table-sm">';
        html += '<thead><tr><th>Text</th><th>Emotion</th><th>Confidence</th></tr></thead>';
        html += '<tbody>';
        
        results.forEach((item, index) => {
            const text = item.text.substring(0, 40) + (item.text.length > 40 ? '...' : '');
            const result = item.result;
            html += `<tr>`;
            html += `<td>${text}</td>`;
            html += `<td>${formatValue(result)}</td>`;
            html += `<td><span class="badge bg-primary">100%</span></td>`;
            html += `</tr>`;
        });
        
        html += '</tbody></table></div></div>';
        container.innerHTML = html;
    }
}

/**
 * Display advanced analysis results
 */
function displayAdvancedResults(result, containerId) {
    const container = document.getElementById(containerId);
    
    if (result.status === 'success') {
        const analysis = result.analysis || {};
        
        let html = '<div class="result-box">';
        html += '<h6><i class="fas fa-cogs"></i> Advanced Analysis Results</h6>';
        
        for (const [key, value] of Object.entries(analysis)) {
            html += `<div class="metric">`;
            html += `<span class="metric-label"><i class="fas fa-arrow-right"></i> ${formatKey(key)}</span>`;
            html += `<span class="metric-value">${formatValue(value)}</span>`;
            html += `</div>`;
        }
        
        html += '</div>';
        container.innerHTML = html;
    }
}

/**
 * Display analysis history
 */
function displayHistory(history) {
    const tbody = document.getElementById('historyTable');
    
    if (history.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">No history yet</td></tr>';
        return;
    }

    tbody.innerHTML = history.map((item, index) => `
        <tr>
            <td><small>${new Date(item.timestamp).toLocaleString()}</small></td>
            <td><small>${(item.text || item.content || '').substring(0, 50)}...</small></td>
            <td><span class="badge bg-info">${item.type || 'analysis'}</span></td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="viewDetail(${index})">
                    <i class="fas fa-eye"></i> View
                </button>
            </td>
        </tr>
    `).join('');
}

/**
 * Format key names for display
 */
function formatKey(key) {
    return key
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

/**
 * Format values for display
 */
function formatValue(value) {
    if (typeof value === 'number') {
        return value.toFixed(2);
    }
    if (typeof value === 'boolean') {
        return value ? '✓ Yes' : '✗ No';
    }
    if (typeof value === 'object') {
        return JSON.stringify(value).substring(0, 50) + '...';
    }
    return String(value).substring(0, 100);
}

/**
 * Show spinner
 */
function showSpinner(id) {
    const spinner = document.getElementById(id);
    if (spinner) {
        spinner.classList.add('active');
    }
}

/**
 * Hide spinner
 */
function hideSpinner(id) {
    const spinner = document.getElementById(id);
    if (spinner) {
        spinner.classList.remove('active');
    }
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div class="toast-body">
            <div>${message}</div>
        </div>
    `;
    
    container.appendChild(toast);
    
    // Auto remove after 4 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

/**
 * View analysis detail
 */
function viewDetail(index) {
    const item = analysisHistory[index];
    console.log('Viewing detail:', item);
    showToast('📊 Detailed view functionality will be implemented', 'info');
}

/**
 * Handle API errors
 */
function handleError(error, message = 'An error occurred') {
    console.error('❌ Error:', error);
    showToast(`❌ ${message}: ${error.message}`, 'error');
}
