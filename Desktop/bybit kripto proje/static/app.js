// Ana JavaScript dosyası - API çağrıları ve UI işlemleri

// Helper function for notifications (fallback to alert if notifications not available)
function showNotification(message, type = 'info') {
    if (typeof notifications !== 'undefined' && notifications) {
        notifications[type](message);
    } else {
        // Fallback to alert for backward compatibility
        alert(message);
    }
}

// Portföy Analizi
let portfolioItems = 1;

function addPortfolioItem() {
    const container = document.getElementById('portfolio-inputs');
    const newItem = document.createElement('div');
    newItem.className = 'portfolio-item mb-3 border-top pt-3';
    newItem.innerHTML = `
        <label>Coin</label>
        <input type="text" class="form-control coin-symbol" placeholder="ETH" 
               list="coin-list-new" autocomplete="off">
        <datalist id="coin-list-new">
            <option value="BTC">Bitcoin</option>
            <option value="ETH">Ethereum</option>
            <option value="BNB">Binance Coin</option>
            <option value="SOL">Solana</option>
            <option value="XRP">Ripple</option>
            <option value="ADA">Cardano</option>
            <option value="DOGE">Dogecoin</option>
            <option value="TRX">Tron</option>
            <option value="AVAX">Avalanche</option>
            <option value="LINK">Chainlink</option>
            <option value="DOT">Polkadot</option>
            <option value="MATIC">Polygon</option>
            <option value="SHIB">Shiba Inu</option>
            <option value="LTC">Litecoin</option>
            <option value="BCH">Bitcoin Cash</option>
            <option value="UNI">Uniswap</option>
            <option value="ATOM">Cosmos</option>
        </datalist>
        <label class="mt-2">Miktar</label>
        <input type="number" class="form-control coin-amount" placeholder="5" step="0.000001">
        <label class="mt-2">Girdi Fiyatı (Opsiyonel)</label>
        <input type="number" class="form-control coin-price" placeholder="Auto" step="0.01">
        <button class="btn btn-sm btn-danger mt-2" onclick="this.parentElement.remove()">
            <i class="bi bi-trash"></i> Sil
        </button>
    `;
    container.appendChild(newItem);
}

async function analyzePortfolio() {
    const items = document.querySelectorAll('.portfolio-item');
    const portfolio = [];
    
    for (let item of items) {
        const symbol = item.querySelector('.coin-symbol').value.toUpperCase();
        const amount = parseFloat(item.querySelector('.coin-amount').value);
        const price = item.querySelector('.coin-price').value;
        
        if (symbol && amount > 0) {
            portfolio.push({
                symbol: symbol,
                amount: amount,
                price: price ? parseFloat(price) : null
            });
        }
    }
    
    if (portfolio.length === 0) {
        showNotification('Lütfen en az bir coin girin!', 'warning');
        return;
    }
    
    const resultsDiv = document.getElementById('portfolio-results');
    resultsDiv.innerHTML = '<div class="loading"><div class="spinner-border text-primary" role="status"></div><p>Analiz yapılıyor...</p></div>';
    resultsDiv.querySelector('.loading').style.display = 'flex';
    
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({portfolio: portfolio})
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayPortfolioResults(data.data);
            showNotification('Portföy analizi tamamlandı!', 'success');
        } else {
            resultsDiv.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
            showNotification(data.error || 'Analiz sırasında bir hata oluştu', 'error');
        }
    } catch (error) {
        resultsDiv.innerHTML = `<div class="alert alert-danger">Hata: ${error.message}</div>`;
        showNotification('Bağlantı hatası: ' + error.message, 'error');
    }
}

function displayPortfolioResults(data) {
    const riskScore = data.risk_analysis.overall_score;
    const riskLevel = data.risk_analysis.risk_level;
    const riskClass = getRiskClass(riskScore);
    
    let html = `
        <div class="card">
            <div class="card-header">Portföy Analiz Sonuçları</div>
            <div class="card-body">
                <div class="row mb-4">
                    <div class="col-md-3">
                        <div class="stat-card">
                            <div class="stat-value">$${data.total_value.toLocaleString('tr-TR', {minimumFractionDigits: 2})}</div>
                            <div class="stat-label">Toplam Değer</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="stat-card">
                            <div class="stat-value ${riskClass}">${riskScore.toFixed(1)}</div>
                            <div class="stat-label">Risk Skoru</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="stat-card">
                            <div class="stat-value">${data.coin_count}</div>
                            <div class="stat-label">Coin Sayısı</div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="stat-card">
                            <span class="risk-badge ${riskClass}">${riskLevel}</span>
                            <div class="stat-label">Risk Seviyesi</div>
                        </div>
                    </div>
                </div>
                
                <div class="mb-3">
                    <h5>Detaylı Risk Analizi</h5>
                    <div class="progress mb-2" style="height: 30px;">
                        <div class="progress-bar bg-danger" role="progressbar" style="width: ${riskScore}%">
                            ${riskScore.toFixed(1)}%
                        </div>
                    </div>
                    <small>Düşük Risk: 0-40 | Orta Risk: 40-60 | Yüksek Risk: 60-75 | Çok Yüksek: 75-100</small>
                </div>
                
                <div class="row mb-3">
                    <div class="col-md-6">
                        <p><strong>Diversifikasyon Skoru:</strong> ${data.risk_analysis.diversification_score}/100</p>
                        <div class="progress mb-2">
                            <div class="progress-bar bg-success" style="width: ${data.risk_analysis.diversification_score}%"></div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <p><strong>Volatilite Skoru:</strong> ${data.risk_analysis.volatility_score}/100</p>
                        <div class="progress mb-2">
                            <div class="progress-bar bg-warning" style="width: ${data.risk_analysis.volatility_score}%"></div>
                        </div>
                    </div>
                </div>
                
                <h5>Portföy Detayları</h5>
                <div class="table-responsive">
                    <table class="table table-striped">
                        <thead>
                            <tr>
                                <th>Coin</th>
                                <th>Miktar</th>
                                <th>Fiyat</th>
                                <th>Değer (USD)</th>
                                <th>%</th>
                                <th>Volatilite</th>
                            </tr>
                        </thead>
                        <tbody>
    `;
    
    data.portfolio.forEach(item => {
        const vol = data.coin_volatilities[item.symbol] || 'N/A';
        html += `
            <tr>
                <td><strong>${item.symbol}</strong></td>
                <td>${item.amount.toFixed(6)}</td>
                <td>$${item.price.toLocaleString('tr-TR', {minimumFractionDigits: 2})}</td>
                <td>$${item.value.toLocaleString('tr-TR', {minimumFractionDigits: 2})}</td>
                <td>${item.percentage.toFixed(2)}%</td>
                <td>${typeof vol === 'number' ? vol.toFixed(1) + '%' : vol}</td>
            </tr>
        `;
    });
    
    html += `
                        </tbody>
                    </table>
                </div>
    `;
    
    // Son güncelleme zamanı
    if (data.last_updated) {
        html += `<div class="text-muted text-end mt-2"><small>Son güncelleme: ${data.last_updated}</small></div>`;
    }
    
    html += `
                <div class="mt-3">
                    <button class="btn btn-sm btn-outline-primary" onclick="analyzePortfolio()">
                        <i class="bi bi-arrow-clockwise"></i> Yenile
                    </button>
                    <label class="ms-3">
                        <input type="checkbox" id="auto-refresh-portfolio" onchange="toggleAutoRefreshPortfolio()">
                        Otomatik güncelleme (5 saniye)
                    </label>
                </div>
            </div>
        </div>
    `;
    
    document.getElementById('portfolio-results').innerHTML = html;
    
    // Otomatik yenileme başlat (eğer aktifse)
    if (document.getElementById('auto-refresh-portfolio')?.checked) {
        startPortfolioAutoRefresh();
    }
}

// Kaldıraç Analizi
let leverageItems = 1;

function addLeverageItem() {
    const container = document.getElementById('leverage-inputs');
    const newItem = document.createElement('div');
    newItem.className = 'leverage-item mb-3 border p-3 rounded';
    newItem.innerHTML = `
        <label>Coin</label>
        <input type="text" class="form-control leverage-symbol" placeholder="ETH"
               list="coin-list-leverage-new" autocomplete="off">
        <datalist id="coin-list-leverage-new">
            <option value="BTC">Bitcoin</option>
            <option value="ETH">Ethereum</option>
            <option value="BNB">Binance Coin</option>
            <option value="SOL">Solana</option>
            <option value="XRP">Ripple</option>
            <option value="ADA">Cardano</option>
            <option value="DOGE">Dogecoin</option>
            <option value="TRX">Tron</option>
            <option value="AVAX">Avalanche</option>
            <option value="LINK">Chainlink</option>
            <option value="DOT">Polkadot</option>
            <option value="MATIC">Polygon</option>
            <option value="SHIB">Shiba Inu</option>
            <option value="LTC">Litecoin</option>
            <option value="BCH">Bitcoin Cash</option>
            <option value="UNI">Uniswap</option>
            <option value="ATOM">Cosmos</option>
        </datalist>
        <label class="mt-2">Pozisyon Boyutu (USD)</label>
        <input type="number" class="form-control leverage-size" placeholder="10000" step="0.01">
        <label class="mt-2">Kaldıraç (x)</label>
        <input type="number" class="form-control leverage-ratio" placeholder="5" value="5" min="1">
        <label class="mt-2">Girdi Fiyatı</label>
        <input type="number" class="form-control leverage-entry" placeholder="3000" step="0.01">
        <label class="mt-2">Yön</label>
        <select class="form-control leverage-side">
            <option value="Buy">Long (Alış)</option>
            <option value="Sell">Short (Satış)</option>
        </select>
        <button class="btn btn-sm btn-danger mt-2" onclick="this.parentElement.remove()">
            <i class="bi bi-trash"></i> Sil
        </button>
    `;
    container.appendChild(newItem);
}

async function analyzeLeverage() {
    const totalBalance = parseFloat(document.getElementById('total-balance').value);
    if (!totalBalance || totalBalance <= 0) {
        alert('Lütfen geçerli bir hesap bakiyesi girin!');
        return;
    }
    
    const items = document.querySelectorAll('.leverage-item');
    const positions = [];
    
    for (let item of items) {
        const symbol = item.querySelector('.leverage-symbol').value.toUpperCase();
        const size = parseFloat(item.querySelector('.leverage-size').value);
        const leverage = parseFloat(item.querySelector('.leverage-ratio').value);
        const entryPrice = parseFloat(item.querySelector('.leverage-entry').value);
        const side = item.querySelector('.leverage-side').value;
        
        if (symbol && size > 0 && leverage > 0 && entryPrice > 0) {
            const margin = size / leverage;
            positions.push({
                symbol: symbol,
                size: size,
                leverage: leverage,
                entry_price: entryPrice,
                // current_price backend'de API'den otomatik çekilecek
                side: side,
                margin: margin
            });
        }
    }
    
    if (positions.length === 0) {
        alert('Lütfen en az bir pozisyon girin!');
        return;
    }
    
    const resultsDiv = document.getElementById('leverage-results');
    resultsDiv.innerHTML = '<div class="loading"><div class="spinner-border" role="status"></div><p>Analiz yapılıyor...</p></div>';
    
    try {
        const response = await fetch('/api/analyze-leverage', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                positions: positions,
                total_balance: totalBalance
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayLeverageResults(data.data);
        } else {
            resultsDiv.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
        }
    } catch (error) {
        resultsDiv.innerHTML = `<div class="alert alert-danger">Hata: ${error.message}</div>`;
    }
}

function displayLeverageResults(data) {
    let html = `
        <div class="card">
            <div class="card-header">Kaldıraç Analiz Sonuçları</div>
            <div class="card-body">
                <div class="row mb-4">
                    <div class="col-md-4">
                        <div class="stat-card">
                            <div class="stat-value ${getRiskClass(data.total_leverage_risk)}">${data.total_leverage_risk.toFixed(1)}</div>
                            <div class="stat-label">Toplam Risk Skoru</div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="stat-card">
                            <div class="stat-value">$${data.total_exposure.toLocaleString('tr-TR')}</div>
                            <div class="stat-label">Toplam Exposure</div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="stat-card">
                            <div class="stat-value ${data.margin_usage_percentage > 50 ? 'text-danger' : ''}">${data.margin_usage_percentage.toFixed(1)}%</div>
                            <div class="stat-label">Margin Kullanımı</div>
                        </div>
                    </div>
                </div>
    `;
    
    // Uyarılar
    if (data.warnings.length > 0) {
        html += '<h5>⚠️ Uyarılar ve Riskler</h5>';
        data.warnings.forEach(warning => {
            const alertClass = warning.severity === 'CRITICAL' ? 'danger-box' : 'warning-box';
            html += `
                <div class="${alertClass}">
                    <strong>${warning.type.replace('_', ' ')}</strong>
                    <p>${warning.message}</p>
                    ${warning.recommendation ? `<p><strong>Öneri:</strong> ${warning.recommendation}</p>` : ''}
                </div>
            `;
        });
    }
    
    // Öneriler
    if (data.recommendations.length > 0) {
        html += '<h5 class="mt-3">💡 Öneriler</h5>';
        data.recommendations.forEach(rec => {
            html += `<div class="info-box">${rec.message}</div>`;
        });
    }
    
    // Pozisyon detayları
    html += '<h5 class="mt-3">Pozisyon Detayları (Gerçek Zamanlı)</h5>';
    html += '<div class="table-responsive"><table class="table table-striped"><thead><tr><th>Coin</th><th>Kaldıraç</th><th>Pozisyon</th><th>Margin</th><th>PnL</th><th>PnL %</th><th>Liquidation</th><th>Mesafe</th><th>Risk</th></tr></thead><tbody>';
    
    data.positions_analysis.forEach(pos => {
        const pnlClass = pos.pnl_amount >= 0 ? 'text-success' : 'text-danger';
        const distanceClass = pos.distance_to_liquidation !== null && pos.distance_to_liquidation < 10 ? 'text-danger' : '';
        
        html += `
            <tr>
                <td><strong>${pos.symbol}</strong></td>
                <td>${pos.leverage}x</td>
                <td>$${pos.size.toLocaleString('tr-TR', {minimumFractionDigits: 2})}</td>
                <td>$${pos.margin.toLocaleString('tr-TR', {minimumFractionDigits: 2})}</td>
                <td class="${pnlClass}">
                    ${pos.pnl_amount >= 0 ? '+' : ''}$${pos.pnl_amount.toLocaleString('tr-TR', {minimumFractionDigits: 2})}
                </td>
                <td class="${pnlClass}">
                    ${pos.pnl_percentage >= 0 ? '+' : ''}${pos.pnl_percentage.toFixed(2)}%
                </td>
                <td>${pos.liquidation_price ? '$' + pos.liquidation_price.toLocaleString('tr-TR', {minimumFractionDigits: 2}) : 'N/A'}</td>
                <td class="${distanceClass}">
                    ${pos.distance_to_liquidation !== null ? pos.distance_to_liquidation.toFixed(2) + '%' : 'N/A'}
                </td>
                <td><span class="risk-badge ${getRiskClass(pos.risk_score)}">${pos.risk_score.toFixed(0)}</span></td>
            </tr>
        `;
    });
    
    html += `</tbody></table></div>`;
    
    // Toplam PnL göster
    if (data.total_pnl !== undefined) {
        const pnlClass = data.total_pnl >= 0 ? 'text-success' : 'text-danger';
        html += `
            <div class="row mt-3">
                <div class="col-md-6">
                    <div class="stat-card">
                        <div class="stat-value ${pnlClass}">
                            ${data.total_pnl >= 0 ? '+' : ''}$${data.total_pnl.toLocaleString('tr-TR', {minimumFractionDigits: 2})}
                        </div>
                        <div class="stat-label">Toplam PnL</div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="stat-card">
                        <div class="stat-value ${pnlClass}">
                            ${data.total_pnl_percentage !== undefined ? (data.total_pnl_percentage >= 0 ? '+' : '') + data.total_pnl_percentage.toFixed(2) + '%' : 'N/A'}
                        </div>
                        <div class="stat-label">PnL %</div>
                    </div>
                </div>
            </div>
        `;
    }
    
    // Son güncelleme zamanı
    if (data.last_updated) {
        html += `<div class="text-muted text-end mt-2"><small>Son güncelleme: ${data.last_updated}</small></div>`;
    }
    
    html += `
                <div class="info-box mt-3">
                    <strong>💡 Güvenli Margin Limiti:</strong> $${data.safe_margin_limit.toLocaleString('tr-TR')}
                    (Toplam bakiyenin %30'u)
                </div>
                <div class="mt-2">
                    <button class="btn btn-sm btn-outline-primary" onclick="analyzeLeverage()">
                        <i class="bi bi-arrow-clockwise"></i> Yenile
                    </button>
                    <label class="ms-3">
                        <input type="checkbox" id="auto-refresh-leverage" onchange="toggleAutoRefreshLeverage()">
                        Otomatik güncelleme (5 saniye)
                    </label>
                </div>
            </div>
        </div>
    `;
    
    document.getElementById('leverage-results').innerHTML = html;
    
    // Otomatik yenileme başlat (eğer aktifse)
    if (document.getElementById('auto-refresh-leverage')?.checked) {
        startLeverageAutoRefresh();
    }
}

// Otomatik yenileme değişkenleri
let leverageAutoRefreshInterval = null;
let portfolioAutoRefreshInterval = null;

function toggleAutoRefreshLeverage() {
    const checkbox = document.getElementById('auto-refresh-leverage');
    if (checkbox?.checked) {
        startLeverageAutoRefresh();
    } else {
        stopLeverageAutoRefresh();
    }
}

function startLeverageAutoRefresh() {
    stopLeverageAutoRefresh(); // Önceki interval'i temizle
    leverageAutoRefreshInterval = setInterval(() => {
        analyzeLeverage();
    }, 5000); // 5 saniyede bir güncelle
}

function stopLeverageAutoRefresh() {
    if (leverageAutoRefreshInterval) {
        clearInterval(leverageAutoRefreshInterval);
        leverageAutoRefreshInterval = null;
    }
}

function toggleAutoRefreshPortfolio() {
    const checkbox = document.getElementById('auto-refresh-portfolio');
    if (checkbox?.checked) {
        startPortfolioAutoRefresh();
    } else {
        stopPortfolioAutoRefresh();
    }
}

function startPortfolioAutoRefresh() {
    stopPortfolioAutoRefresh();
    portfolioAutoRefreshInterval = setInterval(() => {
        analyzePortfolio();
    }, 5000); // 5 saniyede bir güncelle
}

function stopPortfolioAutoRefresh() {
    if (portfolioAutoRefreshInterval) {
        clearInterval(portfolioAutoRefreshInterval);
        portfolioAutoRefreshInterval = null;
    }
}

// Pozisyon Boyutu
async function calculatePositionSize() {
    const symbol = document.getElementById('position-symbol').value.toUpperCase();
    const balance = parseFloat(document.getElementById('position-balance').value);
    const riskTolerance = document.getElementById('risk-tolerance').value;
    const leverage = parseInt(document.getElementById('position-leverage').value);
    const stopLoss = document.getElementById('stop-loss-pct').value ? parseFloat(document.getElementById('stop-loss-pct').value) : null;
    
    if (!symbol || !balance || balance <= 0) {
        alert('Lütfen geçerli değerler girin!');
        return;
    }
    
    const resultsDiv = document.getElementById('position-results');
    resultsDiv.innerHTML = '<div class="loading"><div class="spinner-border" role="status"></div><p>Hesaplanıyor...</p></div>';
    
    try {
        const response = await fetch('/api/position-size', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                symbol: symbol,
                account_balance: balance,
                risk_tolerance: riskTolerance,
                leverage: leverage,
                stop_loss_percentage: stopLoss
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayPositionSizeResults(data.data);
        } else {
            resultsDiv.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
        }
    } catch (error) {
        resultsDiv.innerHTML = `<div class="alert alert-danger">Hata: ${error.message}</div>`;
    }
}

function displayPositionSizeResults(data) {
    let html = `
        <div class="card">
            <div class="card-header">Pozisyon Boyutu Önerisi</div>
            <div class="card-body">
                <div class="info-box">
                    <pre style="white-space: pre-wrap; margin: 0;">${data.recommendation}</pre>
                </div>
                
                <div class="row mt-3">
                    <div class="col-md-6">
                        <div class="stat-card">
                            <div class="stat-value">$${data.position_size_usd.toLocaleString('tr-TR', {minimumFractionDigits: 2})}</div>
                            <div class="stat-label">Önerilen Pozisyon Boyutu</div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="stat-card">
                            <div class="stat-value">$${data.margin_required.toLocaleString('tr-TR', {minimumFractionDigits: 2})}</div>
                            <div class="stat-label">Gerekli Margin</div>
                        </div>
                    </div>
                </div>
                
                <div class="row mt-3">
                    <div class="col-md-4">
                        <p><strong>Coin Miktarı:</strong><br>${data.coin_amount ? data.coin_amount.toFixed(6) : 'N/A'} ${data.symbol}</p>
                    </div>
                    <div class="col-md-4">
                        <p><strong>Maksimum Risk:</strong><br>$${data.risk_amount.toLocaleString('tr-TR', {minimumFractionDigits: 2})} (${data.risk_percentage}%)</p>
                    </div>
                    <div class="col-md-4">
                        <p><strong>Stop-Loss:</strong><br>${data.stop_loss_percentage}% ($${data.stop_loss_price ? data.stop_loss_price.toLocaleString('tr-TR', {minimumFractionDigits: 2}) : 'N/A'})</p>
                    </div>
                </div>
    `;
    
    if (data.warnings && data.warnings.length > 0) {
        html += '<div class="warning-box mt-3">';
        data.warnings.forEach(warning => {
            html += `<p>${warning}</p>`;
        });
        html += '</div>';
    }
    
    html += '</div></div>';
    
    document.getElementById('position-results').innerHTML = html;
}

// Risk/Reward
async function calculateRiskReward() {
    const entryPrice = parseFloat(document.getElementById('rr-entry').value);
    const stopLoss = parseFloat(document.getElementById('rr-stop').value);
    const takeProfit = parseFloat(document.getElementById('rr-tp').value);
    const side = document.getElementById('rr-side').value;
    
    if (!entryPrice || !stopLoss || !takeProfit) {
        alert('Lütfen tüm fiyatları girin!');
        return;
    }
    
    const resultsDiv = document.getElementById('risk-reward-results');
    resultsDiv.innerHTML = '<div class="loading"><div class="spinner-border" role="status"></div><p>Hesaplanıyor...</p></div>';
    
    try {
        const response = await fetch('/api/risk-reward', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                entry_price: entryPrice,
                stop_loss_price: stopLoss,
                take_profit_price: takeProfit,
                side: side
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayRiskRewardResults(data.data);
        } else {
            resultsDiv.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
        }
    } catch (error) {
        resultsDiv.innerHTML = `<div class="alert alert-danger">Hata: ${error.message}</div>`;
    }
}

function displayRiskRewardResults(data) {
    const rrClass = data.risk_reward_ratio >= 2 ? 'success' : data.risk_reward_ratio >= 1.5 ? 'warning' : 'danger';
    
    let html = `
        <div class="card">
            <div class="card-header">Risk/Reward Analizi</div>
            <div class="card-body">
                <div class="stat-card">
                    <div class="stat-value text-${rrClass}">${data.risk_reward_ratio.toFixed(2)}:1</div>
                    <div class="stat-label">Risk/Reward Oranı</div>
                </div>
                
                <div class="info-box mt-3">
                    <p><strong>Değerlendirme:</strong> ${data.evaluation}</p>
                    <p>${data.recommendation}</p>
                </div>
                
                <div class="row mt-3">
                    <div class="col-md-6">
                        <p><strong>Risk:</strong> ${data.risk_percentage}%</p>
                        <div class="progress">
                            <div class="progress-bar bg-danger" style="width: ${Math.min(data.risk_percentage * 5, 100)}%"></div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <p><strong>Reward:</strong> ${data.reward_percentage}%</p>
                        <div class="progress">
                            <div class="progress-bar bg-success" style="width: ${Math.min(data.reward_percentage * 2, 100)}%"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.getElementById('risk-reward-results').innerHTML = html;
}

// Bybit API Entegrasyonu
async function connectBybit() {
    const apiKey = document.getElementById('api-key').value.trim();
    const apiSecret = document.getElementById('api-secret').value.trim();
    
    if (!apiKey || !apiSecret) {
        alert('Lütfen API Key ve Secret girin!');
        return;
    }
    
    const statusDiv = document.getElementById('integration-status');
    statusDiv.innerHTML = '<div class="spinner-border spinner-border-sm"></div> Bağlanıyor...';
    
    try {
        const response = await fetch('/api/connect-bybit', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                api_key: apiKey,
                api_secret: apiSecret
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            statusDiv.innerHTML = '<div class="alert alert-success">✅ ' + data.message + '</div>';
            document.getElementById('connection-form').style.display = 'none';
            document.getElementById('connected-actions').style.display = 'block';
            checkBybitStatus();
        } else {
            let errorHtml = '<div class="alert alert-danger"><strong>❌ ' + data.error + '</strong>';
            
            if (data.error_code) {
                errorHtml += '<br><small>Hata Kodu: ' + data.error_code + '</small>';
            }
            
            if (data.suggestion) {
                errorHtml += '<div class="mt-2 p-2 bg-light border rounded"><strong>💡 Çözüm:</strong><br>' + data.suggestion + '</div>';
            }
            
            // Yaygın hata çözümleri
            if (data.error_code === '10006' || data.error.includes('IP')) {
                errorHtml += '<div class="mt-2 p-2 bg-warning bg-opacity-25 border rounded">';
                errorHtml += '<strong>📝 Nasıl Düzeltilir:</strong><ol class="mb-0">';
                errorHtml += '<li>Bybit API Management sayfasına gidin</li>';
                errorHtml += '<li>API Key\'inizi bulun</li>';
                errorHtml += '<li>"Edit" butonuna tıklayın</li>';
                errorHtml += '<li>IP kısıtlamasını kaldırın veya kendi IP\'nizi ekleyin</li>';
                errorHtml += '<li>Google\'da "what is my ip" yazarak IP\'nizi öğrenin</li>';
                errorHtml += '</ol></div>';
            }
            
            if (data.error_code === '33004' || data.error.includes('izin')) {
                errorHtml += '<div class="mt-2 p-2 bg-warning bg-opacity-25 border rounded">';
                errorHtml += '<strong>📝 Gerekli İzinler:</strong><ul class="mb-0">';
                errorHtml += '<li>Unified Trading > Contract > Positions ✓</li>';
                errorHtml += '<li>Unified Trading > SPOT > Trade ✓</li>';
                errorHtml += '<li>Assets > Wallet > Account Transfer ✓</li>';
                errorHtml += '</ul></div>';
            }
            
            errorHtml += '</div>';
            statusDiv.innerHTML = errorHtml;
            showNotification(data.error, 'error');
        }
    } catch (error) {
        statusDiv.innerHTML = '<div class="alert alert-danger">Hata: ' + error.message + '</div>';
        showNotification('Bağlantı hatası: ' + error.message, 'error');
    }
}

async function disconnectBybit() {
    try {
        const response = await fetch('/api/disconnect-bybit', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            document.getElementById('connection-form').style.display = 'block';
            document.getElementById('connected-actions').style.display = 'none';
            document.getElementById('integration-status').innerHTML = '<div class="alert alert-info">Bağlantı kesildi</div>';
            document.getElementById('api-key').value = '';
            document.getElementById('api-secret').value = '';
        }
    } catch (error) {
        console.error('Bağlantı kesme hatası:', error);
    }
}

async function checkBybitStatus() {
    try {
        const response = await fetch('/api/bybit-status');
        const data = await response.json();
        
        if (data.connected) {
            document.getElementById('connection-form').style.display = 'none';
            document.getElementById('connected-actions').style.display = 'block';
        }
    } catch (error) {
        console.error('Status kontrol hatası:', error);
    }
}

async function syncBybitPositions() {
    const resultsDiv = document.getElementById('integration-results');
    resultsDiv.innerHTML = '<div class="loading"><div class="spinner-border" role="status"></div><p>Pozisyonlar çekiliyor...</p></div>';
    
    try {
        const response = await fetch('/api/sync-positions');
        const data = await response.json();
        
        if (data.success) {
            displayBybitPositions(data.data);
        } else {
            resultsDiv.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
        }
    } catch (error) {
        resultsDiv.innerHTML = `<div class="alert alert-danger">Hata: ${error.message}</div>`;
    }
}

function displayBybitPositions(data) {
    let html = `
        <div class="card">
            <div class="card-header">📊 Bybit Pozisyonları</div>
            <div class="card-body">
                <div class="row mb-3">
                    <div class="col-md-6">
                        <div class="stat-card">
                            <div class="stat-value">$${data.total_balance_usdt.toLocaleString('tr-TR', {minimumFractionDigits: 2})}</div>
                            <div class="stat-label">USDT Bakiye</div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="stat-card">
                            <div class="stat-value">${data.futures_positions.length + data.spot_positions.length}</div>
                            <div class="stat-label">Toplam Pozisyon</div>
                        </div>
                    </div>
                </div>
    `;
    
    // Futures pozisyonları
    if (data.futures_positions.length > 0) {
        html += '<h5>⚡ Futures Pozisyonları</h5>';
        html += '<div class="table-responsive"><table class="table table-sm table-striped"><thead><tr><th>Coin</th><th>Yön</th><th>Kaldıraç</th><th>Pozisyon</th><th>PnL</th></tr></thead><tbody>';
        
        data.futures_positions.forEach(pos => {
            const pnlClass = pos.unrealized_pnl >= 0 ? 'text-success' : 'text-danger';
            html += `
                <tr>
                    <td><strong>${pos.symbol}</strong></td>
                    <td>${pos.side}</td>
                    <td>${pos.leverage}x</td>
                    <td>$${pos.size.toLocaleString('tr-TR', {minimumFractionDigits: 2})}</td>
                    <td class="${pnlClass}">$${pos.unrealized_pnl.toLocaleString('tr-TR', {minimumFractionDigits: 2})}</td>
                </tr>
            `;
        });
        
        html += '</tbody></table></div>';
    }
    
    // Spot pozisyonları
    if (data.spot_positions.length > 0) {
        html += '<h5 class="mt-3">💰 Spot Pozisyonları</h5>';
        html += '<div class="table-responsive"><table class="table table-sm table-striped"><thead><tr><th>Coin</th><th>Miktar</th><th>Kullanılabilir</th></tr></thead><tbody>';
        
        data.spot_positions.forEach(pos => {
            html += `
                <tr>
                    <td><strong>${pos.symbol}</strong></td>
                    <td>${pos.amount.toFixed(6)}</td>
                    <td>${pos.available.toFixed(6)}</td>
                </tr>
            `;
        });
        
        html += '</tbody></table></div>';
    }
    
    if (data.futures_positions.length === 0 && data.spot_positions.length === 0) {
        html += '<div class="alert alert-info">Henüz açık pozisyonunuz yok.</div>';
    }
    
    html += '</div></div>';
    document.getElementById('integration-results').innerHTML = html;
}

async function loadPortfolioFromBybit() {
    try {
        const response = await fetch('/api/sync-positions');
        const data = await response.json();
        
        if (data.success && data.data.spot_positions.length > 0) {
            // Spot pozisyonları portföy analizine aktar
            const portfolio = data.data.spot_positions.map(pos => ({
                symbol: pos.symbol,
                amount: pos.amount,
                price: null  // Fiyat API'den çekilecek
            }));
            
            // Portföy analizi sekmesine geç
            document.getElementById('portfolio-tab').click();
            
            // Portföyü analiz et
            const analyzeResponse = await fetch('/api/analyze', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({portfolio: portfolio})
            });
            
            const analyzeData = await analyzeResponse.json();
            
            if (analyzeData.success) {
                displayPortfolioResults(analyzeData.data);
                alert('✅ Bybit portföyünüz yüklendi ve analiz edildi!');
            }
        } else {
            alert('Spot pozisyon bulunamadı. Lütfen önce pozisyonları çekin.');
        }
    } catch (error) {
        alert('Hata: ' + error.message);
    }
}

// Sayfa yüklendiğinde durumu kontrol et
document.addEventListener('DOMContentLoaded', function() {
    checkBybitStatus();
});

// Yardımcı fonksiyonlar
function getRiskClass(score) {
    if (score >= 75) return 'risk-critical';
    if (score >= 60) return 'risk-high';
    if (score >= 40) return 'risk-medium';
    return 'risk-low';
}

