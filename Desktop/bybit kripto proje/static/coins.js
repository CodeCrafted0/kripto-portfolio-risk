// Popüler kripto coinler listesi
const POPULAR_COINS = [
    'BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'DOGE', 'TRX', 'AVAX', 'LINK',
    'DOT', 'MATIC', 'SHIB', 'LTC', 'BCH', 'UNI', 'ATOM', 'ETC', 'XLM', 'FIL',
    'ALGO', 'VET', 'ICP', 'THETA', 'EOS', 'AAVE', 'AXS', 'MKR', 'SAND', 'MANA',
    'ENJ', 'FLOW', 'NEAR', 'APT', 'OP', 'ARB', 'FTM', 'HBAR', 'QNT', 'IMX',
    'GRT', 'RENDER', 'INJ', 'TIA', 'SEI', 'SUI', 'BLUR', 'PENDLE', 'ONDO', 'JUP'
];

// Coin bilgileri
const COIN_INFO = {
    'BTC': { name: 'Bitcoin', icon: '₿' },
    'ETH': { name: 'Ethereum', icon: 'Ξ' },
    'BNB': { name: 'Binance Coin', icon: '🟡' },
    'SOL': { name: 'Solana', icon: '◎' },
    'XRP': { name: 'Ripple', icon: '✕' },
    'ADA': { name: 'Cardano', icon: '₳' },
    'DOGE': { name: 'Dogecoin', icon: 'Ð' },
    'TRX': { name: 'Tron', icon: 'T' },
    'AVAX': { name: 'Avalanche', icon: '🔺' },
    'LINK': { name: 'Chainlink', icon: '🔗' }
};

// Coin seçim dropdown'u oluştur
function createCoinSelect(className, defaultValue = 'BTC') {
    let html = `<select class="form-control ${className} coin-select">`;
    html += `<option value="">Coin Seçin...</option>`;
    
    POPULAR_COINS.forEach(coin => {
        const selected = coin === defaultValue ? 'selected' : '';
        const coinName = COIN_INFO[coin]?.name || coin;
        html += `<option value="${coin}" ${selected}>${coin} - ${coinName}</option>`;
    });
    
    html += `</select>`;
    return html;
}

// Coin input için autocomplete önerileri
function createCoinInput(className, placeholder = 'BTC') {
    return `
        <div class="coin-input-wrapper">
            <input type="text" class="form-control ${className} coin-symbol" 
                   placeholder="${placeholder}" 
                   list="coin-list-${Math.random().toString(36).substr(2, 9)}"
                   autocomplete="off">
            <datalist id="coin-list-${Math.random().toString(36).substr(2, 9)}">
                ${POPULAR_COINS.map(coin => `<option value="${coin}">${COIN_INFO[coin]?.name || coin}</option>`).join('')}
            </datalist>
        </div>
    `;
}

