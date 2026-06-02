const API_BASE = '/api';

document.addEventListener('DOMContentLoaded', function() {
    refreshData();
    setInterval(refreshData, 5000);
});

function switchTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.nav-link').forEach(link => link.classList.remove('active'));
    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');
    
    if (tabName === 'blocks') loadBlocks();
    if (tabName === 'wallets') loadWallets();
}

async function refreshData() {
    try {
        const response = await fetch(`${API_BASE}/statistics`);
        const data = await response.json();
        if (data.success) {
            const stats = data.statistics;
            document.getElementById('totalBlocks').textContent = stats.total_blocks;
            document.getElementById('totalTx').textContent = stats.total_transactions;
            document.getElementById('totalVolume').textContent = stats.total_volume;
            document.getElementById('chainValid').textContent = stats.is_valid ? 'Yes' : 'No';
        }
    } catch (e) { console.error(e); }
}

async function addTransaction() {
    const sender = document.getElementById('sender').value.trim();
    const recipient = document.getElementById('recipient').value.trim();
    const amount = parseFloat(document.getElementById('amount').value);
    
    if (!sender || !recipient || amount <= 0) {
        showToast('Please fill all fields correctly', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/transaction`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sender, recipient, amount })
        });
        const data = await response.json();
        if (data.success) {
            showToast(data.message, 'success');
            document.getElementById('sender').value = '';
            document.getElementById('recipient').value = '';
            document.getElementById('amount').value = '';
            refreshData();
        } else {
            showToast(data.error, 'error');
        }
    } catch (e) {
        showToast('Error: ' + e.message, 'error');
    }
}

async function mineBlock() {
    const minerAddress = document.getElementById('minerAddress').value.trim();
    if (!minerAddress) {
        showToast('Enter miner address', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/mine`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ miner_address: minerAddress })
        });
        const data = await response.json();
        if (data.success) {
            showToast('Mining started...', 'success');
            setTimeout(() => {
                refreshData();
                document.getElementById('minerAddress').value = '';
            }, 5000);
        } else {
            showToast(data.error, 'error');
        }
    } catch (e) {
        showToast('Error mining', 'error');
    }
}

async function loadBlocks() {
    try {
        const response = await fetch(`${API_BASE}/blockchain`);
        const data = await response.json();
        const container = document.getElementById('blocksContainer');
        
        if (data.success && data.blocks.length > 0) {
            container.innerHTML = data.blocks.map(block => `
                <div class="block-item">
                    <h4>Block #${block.index}</h4>
                    <p><strong>Nonce:</strong> ${block.nonce}</p>
                    <p><strong>Transactions:</strong> ${block.transactions.length}</p>
                    <p><strong>Hash:</strong> ${block.hash.substring(0, 20)}...</p>
                    <p><strong>Time:</strong> ${block.formatted_timestamp}</p>
                </div>
            `).join('');
        }
    } catch (e) { console.error(e); }
}

async function loadWallets() {
    try {
        const response = await fetch(`${API_BASE}/balances`);
        const data = await response.json();
        const container = document.getElementById('walletsContainer');
        
        if (data.success) {
            const balances = data.balances;
            const sorted = Object.entries(balances).sort(([,a],[,b]) => b-a);
            container.innerHTML = sorted.map(([address, balance]) => `
                <div class="wallet-item">
                    <h4>${address}</h4>
                    <p><strong>Balance:</strong> <span class="amount">${balance} coins</span></p>
                </div>
            `).join('');
        }
    } catch (e) { console.error(e); }
}

async function validateChain() {
    try {
        const response = await fetch(`${API_BASE}/validate`);
        const data = await response.json();
        showToast(data.is_valid ? 'Blockchain is valid!' : 'Blockchain invalid!', data.is_valid ? 'success' : 'error');
    } catch (e) {
        showToast('Error validating', 'error');
    }
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast show ${type === 'error' ? 'error' : ''}`;
    setTimeout(() => toast.classList.remove('show'), 3000);
}