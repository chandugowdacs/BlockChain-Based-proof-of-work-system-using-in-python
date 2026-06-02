from flask import Flask, render_template, request, jsonify
from blockchain import Blockchain
import threading

app = Flask(__name__)
blockchain = Blockchain(difficulty=2)
mining_in_progress = False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/blockchain', methods=['GET'])
def get_blockchain():
    try:
        blocks = blockchain.get_chain_data()
        return jsonify({'success': True, 'blocks': blocks, 'total_blocks': len(blocks)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/pending-transactions', methods=['GET'])
def get_pending_transactions():
    try:
        return jsonify({'success': True, 'pending_transactions': blockchain.pending_transactions, 'count': len(blockchain.pending_transactions)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/transaction', methods=['POST'])
def add_transaction():
    try:
        data = request.json
        sender = data.get('sender', '').strip()
        recipient = data.get('recipient', '').strip()
        amount = float(data.get('amount', 0))
        
        if not sender or not recipient:
            return jsonify({'success': False, 'error': 'Sender and recipient required'}), 400
        if amount <= 0:
            return jsonify({'success': False, 'error': 'Amount must be positive'}), 400
        if sender == recipient:
            return jsonify({'success': False, 'error': 'Sender and recipient cannot be same'}), 400
        
        blockchain.add_transaction(sender, recipient, amount)
        return jsonify({'success': True, 'message': f'Transaction added: {sender} -> {recipient} ({amount} coins)', 'pending_count': len(blockchain.pending_transactions)})
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid amount'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/mine', methods=['POST'])
def mine_block():
    global mining_in_progress
    try:
        if mining_in_progress:
            return jsonify({'success': False, 'error': 'Mining already in progress'}), 400
        
        data = request.json
        miner_address = data.get('miner_address', '').strip()
        
        if not miner_address:
            return jsonify({'success': False, 'error': 'Miner address required'}), 400
        
        if not blockchain.pending_transactions:
            return jsonify({'success': False, 'error': 'No pending transactions'}), 400
        
        mining_in_progress = True
        
        def mine_task():
            global mining_in_progress
            try:
                blockchain.mine_pending_transactions(miner_address)
            except Exception as e:
                print(f"Mining error: {e}")
            finally:
                mining_in_progress = False
        
        thread = threading.Thread(target=mine_task)
        thread.daemon = True
        thread.start()
        
        return jsonify({'success': True, 'message': 'Mining started...'})
    except Exception as e:
        mining_in_progress = False
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/balance/<address>', methods=['GET'])
def get_balance(address):
    try:
        balance = blockchain.get_balance(address)
        return jsonify({'success': True, 'address': address, 'balance': balance})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/balances', methods=['GET'])
def get_all_balances():
    try:
        addresses = blockchain.get_all_addresses()
        balances = {address: blockchain.get_balance(address) for address in addresses}
        return jsonify({'success': True, 'balances': balances})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/addresses', methods=['GET'])
def get_addresses():
    try:
        addresses = blockchain.get_all_addresses()
        return jsonify({'success': True, 'addresses': addresses, 'count': len(addresses)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/transaction-history/<address>', methods=['GET'])
def get_history(address):
    try:
        history = blockchain.get_transaction_history(address)
        return jsonify({'success': True, 'address': address, 'transactions': history})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    try:
        stats = blockchain.get_statistics()
        stats['mining_in_progress'] = mining_in_progress
        stats['difficulty_level'] = blockchain.difficulty
        return jsonify({'success': True, 'statistics': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/validate', methods=['GET'])
def validate_blockchain():
    try:
        is_valid = blockchain.is_chain_valid()
        return jsonify({'success': True, 'is_valid': is_valid})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/clear', methods=['POST'])
def clear_blockchain():
    global blockchain, mining_in_progress
    try:
        blockchain = Blockchain(difficulty=2)
        mining_in_progress = False
        return jsonify({'success': True, 'message': 'Blockchain reset'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/mining-status', methods=['GET'])
def mining_status():
    return jsonify({
        'mining_in_progress': mining_in_progress,
        'pending_transactions': len(blockchain.pending_transactions),
        'total_blocks': len(blockchain.chain)
    })

if __name__ == '__main__':
    print("Starting Blockchain Server...")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True, host='0.0.0.0', port=5000)