// Anlık fiyat grafikleri için Chart.js kullanımı

let btcChart = null;
let ethChart = null;
let btcPriceHistory = [];
let ethPriceHistory = [];
let maxDataPoints = 20; // Grafikte maksimum 20 nokta

// BTC Grafiği
function initBTCChart() {
    const ctx = document.getElementById('btcChart');
    if (!ctx) return;
    
    btcChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'BTC Fiyat (USD)',
                data: [],
                borderColor: '#f7931a',
                backgroundColor: 'rgba(247, 147, 26, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            return 'BTC: $' + context.parsed.y.toLocaleString('tr-TR', {minimumFractionDigits: 2});
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString('tr-TR');
                        }
                    }
                },
                x: {
                    display: false
                }
            },
            animation: {
                duration: 750
            }
        }
    });
}

// ETH Grafiği
function initETHChart() {
    const ctx = document.getElementById('ethChart');
    if (!ctx) return;
    
    ethChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'ETH Fiyat (USD)',
                data: [],
                borderColor: '#627eea',
                backgroundColor: 'rgba(98, 126, 234, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            return 'ETH: $' + context.parsed.y.toLocaleString('tr-TR', {minimumFractionDigits: 2});
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString('tr-TR');
                        }
                    }
                },
                x: {
                    display: false
                }
            },
            animation: {
                duration: 750
            }
        }
    });
}

// Fiyat güncelleme
async function updatePriceCharts() {
    try {
        const response = await fetch('/api/prices?symbols=BTC,ETH');
        const data = await response.json();
        
        if (data.success) {
            const btcPrice = data.data.BTC;
            const ethPrice = data.data.ETH;
            
            if (btcPrice && btcPrice > 0) {
                updateBTCChart(btcPrice);
                updateBTCBadge(btcPrice);
            }
            
            if (ethPrice && ethPrice > 0) {
                updateETHChart(ethPrice);
                updateETHBadge(ethPrice);
            }
        }
    } catch (error) {
        console.error('Fiyat güncelleme hatası:', error);
    }
}

// BTC grafiğini güncelle
function updateBTCChart(price) {
    if (!btcChart) return;
    
    const now = new Date();
    const timeLabel = now.getHours() + ':' + now.getMinutes().toString().padStart(2, '0');
    
    btcPriceHistory.push({
        time: timeLabel,
        price: price
    });
    
    // Maksimum nokta sayısını aşarsa ilkini sil
    if (btcPriceHistory.length > maxDataPoints) {
        btcPriceHistory.shift();
    }
    
    // Grafiği güncelle
    btcChart.data.labels = btcPriceHistory.map(d => d.time);
    btcChart.data.datasets[0].data = btcPriceHistory.map(d => d.price);
    
    // Y eksenini fiyat aralığına göre ayarla
    const prices = btcPriceHistory.map(d => d.price);
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    const padding = (maxPrice - minPrice) * 0.1;
    
    btcChart.options.scales.y.min = Math.max(0, minPrice - padding);
    btcChart.options.scales.y.max = maxPrice + padding;
    
    btcChart.update('none'); // Animasyon olmadan güncelle
    
    // Son güncelleme zamanı
    document.getElementById('btc-last-update').textContent = 
        'Son güncelleme: ' + now.toLocaleTimeString('tr-TR');
}

// ETH grafiğini güncelle
function updateETHChart(price) {
    if (!ethChart) return;
    
    const now = new Date();
    const timeLabel = now.getHours() + ':' + now.getMinutes().toString().padStart(2, '0');
    
    ethPriceHistory.push({
        time: timeLabel,
        price: price
    });
    
    // Maksimum nokta sayısını aşarsa ilkini sil
    if (ethPriceHistory.length > maxDataPoints) {
        ethPriceHistory.shift();
    }
    
    // Grafiği güncelle
    ethChart.data.labels = ethPriceHistory.map(d => d.time);
    ethChart.data.datasets[0].data = ethPriceHistory.map(d => d.price);
    
    // Y eksenini fiyat aralığına göre ayarla
    const prices = ethPriceHistory.map(d => d.price);
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    const padding = (maxPrice - minPrice) * 0.1;
    
    ethChart.options.scales.y.min = Math.max(0, minPrice - padding);
    ethChart.options.scales.y.max = maxPrice + padding;
    
    ethChart.update('none'); // Animasyon olmadan güncelle
    
    // Son güncelleme zamanı
    document.getElementById('eth-last-update').textContent = 
        'Son güncelleme: ' + now.toLocaleTimeString('tr-TR');
}

// BTC badge güncelle
function updateBTCBadge(price) {
    const badge = document.getElementById('btc-price-badge');
    if (badge) {
        badge.textContent = '$' + price.toLocaleString('tr-TR', {minimumFractionDigits: 2});
    }
}

// ETH badge güncelle
function updateETHBadge(price) {
    const badge = document.getElementById('eth-price-badge');
    if (badge) {
        badge.textContent = '$' + price.toLocaleString('tr-TR', {minimumFractionDigits: 2});
    }
}

// İlk yükleme ve otomatik güncelleme
let chartUpdateInterval = null;

function startChartUpdates() {
    // İlk güncelleme
    updatePriceCharts();
    
    // Her 5 saniyede bir güncelle
    if (chartUpdateInterval) {
        clearInterval(chartUpdateInterval);
    }
    
    chartUpdateInterval = setInterval(updatePriceCharts, 5000);
}

function stopChartUpdates() {
    if (chartUpdateInterval) {
        clearInterval(chartUpdateInterval);
        chartUpdateInterval = null;
    }
}

// Sayfa yüklendiğinde grafikleri başlat
document.addEventListener('DOMContentLoaded', function() {
    // Chart.js yüklenene kadar bekle
    if (typeof Chart !== 'undefined') {
        initBTCChart();
        initETHChart();
        startChartUpdates();
    } else {
        // Chart.js henüz yüklenmemişse bekle
        setTimeout(function() {
            initBTCChart();
            initETHChart();
            startChartUpdates();
        }, 500);
    }
});

