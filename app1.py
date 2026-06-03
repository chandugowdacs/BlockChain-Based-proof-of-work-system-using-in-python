"""
====================================================================
  BLOCKCHAIN PROOF-OF-WORK SYSTEM - Flask Backend
  Bytonix IT Solutions | Prajwal M | 476CS23039
====================================================================
  Run:  python app1.py
  Open: http://127.0.0.1:5000
====================================================================
"""

from flask import Flask, jsonify, request, render_template
import hashlib
import time
import json

app = Flask(__name__)  # Flask auto-uses /templates and /static folders

# ---------------------------------------------
# BLOCK & BLOCKCHAIN CORE
# ---------------------------------------------

class Block:
    def __init__(self, index, data, previous_hash):
        self.index         = index
        self.timestamp     = time.time()
        self.data          = data
        self.previous_hash = previous_hash
        self.nonce         = 0
        self.hash          = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps({
            "index":         self.index,
            "timestamp":     self.timestamp,
            "data":          self.data,
            "previous_hash": self.previous_hash,
            "nonce":         self.nonce,
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty):
        target = "0" * difficulty
        start  = time.time()
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash   = self.calculate_hash()
        self.mine_time = round(time.time() - start, 4)

    def to_dict(self):
        return {
            "index":         self.index,
            "timestamp":     self.timestamp,
            "data":          self.data,
            "previous_hash": self.previous_hash,
            "nonce":         self.nonce,
            "hash":          self.hash,
            "mine_time":     getattr(self, "mine_time", 0),
        }


class Blockchain:
    def __init__(self, difficulty=3):
        self.difficulty = difficulty
        self.chain      = []
        self._create_genesis()

    def _create_genesis(self):
        g = Block(0, "Genesis Block - Bytonix IT Solutions", "0" * 64)
        g.mine_block(self.difficulty)
        self.chain.append(g)

    def add_block(self, data):
        prev  = self.chain[-1]
        block = Block(len(self.chain), data, prev.hash)
        block.mine_block(self.difficulty)
        self.chain.append(block)
        return block

    def is_valid(self):
        errors = []
        for i in range(1, len(self.chain)):
            c = self.chain[i]
            p = self.chain[i - 1]
            if c.hash != c.calculate_hash():
                errors.append({"block": i, "reason": "Hash mismatch - data tampered"})
            if c.previous_hash != p.hash:
                errors.append({"block": i, "reason": "Broken link to previous block"})
        return errors

    def tamper(self, index, new_data):
        if 0 < index < len(self.chain):
            self.chain[index].data = new_data
            return True
        return False

    def set_difficulty(self, d):
        self.difficulty = max(1, min(d, 6))

    def to_dict(self):
        return {
            "difficulty": self.difficulty,
            "length":     len(self.chain),
            "chain":      [b.to_dict() for b in self.chain],
        }


# Global blockchain instance
bc = Blockchain(difficulty=3)

# ---------------------------------------------
# CORS helper
# ---------------------------------------------

def cors(response):
    response.headers["Access-Control-Allow-Origin"]  = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response

@app.after_request
def after(r):
    return cors(r)

@app.before_request
def handle_options():
    if request.method == "OPTIONS":
        return cors(app.response_class(status=200))

# ---------------------------------------------
# MAIN ROUTE - serves index.html from templates/
# ---------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")   # looks in templates/index.html

# ---------------------------------------------
# API ROUTES
# ---------------------------------------------

@app.route("/api/chain", methods=["GET"])
def get_chain():
    return jsonify(bc.to_dict())

@app.route("/api/mine", methods=["POST"])
def mine():
    data = request.json.get("data", "").strip()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    block = bc.add_block(data)
    return jsonify({"success": True, "block": block.to_dict()})

@app.route("/api/validate", methods=["GET"])
def validate():
    errors = bc.is_valid()
    return jsonify({"valid": len(errors) == 0, "errors": errors, "length": len(bc.chain)})

@app.route("/api/tamper", methods=["POST"])
def tamper():
    index    = request.json.get("index")
    new_data = request.json.get("data", "TAMPERED").strip()
    if bc.tamper(index, new_data):
        return jsonify({"success": True, "message": f"Block #{index} tampered"})
    return jsonify({"error": "Invalid block index"}), 400

@app.route("/api/difficulty", methods=["POST"])
def set_difficulty():
    d = int(request.json.get("difficulty", 3))
    bc.set_difficulty(d)
    return jsonify({"difficulty": bc.difficulty})

@app.route("/api/reset", methods=["POST"])
def reset():
    global bc
    d  = request.json.get("difficulty", bc.difficulty)
    bc = Blockchain(difficulty=int(d))
    return jsonify({"success": True, "chain": bc.to_dict()})

@app.route("/api/demo", methods=["POST"])
def demo():
    transactions = [
        "Alice -> Bob   : 5.00 BTC",
        "Bob   -> Carol : 2.50 BTC",
        "Carol -> Dave  : 1.25 BTC",
    ]
    mined = []
    for tx in transactions:
        b = bc.add_block(tx)
        mined.append(b.to_dict())
    return jsonify({"success": True, "blocks": mined, "chain": bc.to_dict()})

# ---------------------------------------------

if __name__ == "__main__":
    print("")
    print("  ==========================================")
    print("  BLOCKCHAIN PoW - Bytonix IT Solutions")
    print("  Server -> http://127.0.0.1:5000")
    print("  ==========================================")
    print("")
    app.run(debug=True, port=5000)
