"""
====================================================================
  BLOCKCHAIN-BASED PROOF-OF-WORK SYSTEM USING PYTHON
  Bytonix IT Solutions Internship Project — Prajwal M
  M S Ramaiah Polytechnic | Diploma in CSE | Reg: 476CS23039
====================================================================
  Features:
    • SHA-256 cryptographic hashing
    • Adjustable difficulty Proof-of-Work mining
    • Immutable block chain with tamper detection
    • Chain validation
    • Block explorer (view all blocks)
    • Interactive CLI menu
====================================================================
"""

import hashlib
import time
import json


# ──────────────────────────────────────────────────────────────────
# BLOCK CLASS
# ──────────────────────────────────────────────────────────────────

class Block:
    """
    Represents a single block in the blockchain.

    Attributes:
        index       : Position of the block in the chain
        timestamp   : Time the block was created (Unix epoch)
        data        : Payload / transaction data stored in the block
        previous_hash: Hash of the previous block (cryptographic link)
        nonce       : Number iterated during Proof-of-Work mining
        hash        : SHA-256 hash of this block (computed after mining)
    """

    def __init__(self, index: int, data: str, previous_hash: str):
        self.index         = index
        self.timestamp     = time.time()
        self.data          = data
        self.previous_hash = previous_hash
        self.nonce         = 0
        self.hash          = self.calculate_hash()

    # ── SHA-256 hashing ──────────────────────────────────────────

    def calculate_hash(self) -> str:
        """
        Compute SHA-256 hash over all block fields.
        Any change in data/nonce produces a completely different hash.
        """
        block_string = json.dumps({
            "index":         self.index,
            "timestamp":     self.timestamp,
            "data":          self.data,
            "previous_hash": self.previous_hash,
            "nonce":         self.nonce,
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    # ── Proof-of-Work mining ─────────────────────────────────────

    def mine_block(self, difficulty: int) -> None:
        """
        Proof-of-Work: increment nonce until the hash starts with
        `difficulty` leading zeros (the 'target').

        Steps (matching the PPT slide):
          1. Receive input data
          2. Generate / increment nonce
          3. Compute SHA-256 hash of block header + nonce
          4. Compare hash against target difficulty prefix
          5. If match → block added; else → retry with next nonce
        """
        target = "0" * difficulty
        print(f"\n  ⛏  Mining block #{self.index}  (difficulty = {difficulty}) ...")

        start = time.time()
        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash   = self.calculate_hash()

        elapsed = time.time() - start
        print(f"  ✅ Block mined!  Nonce: {self.nonce}  |  Time: {elapsed:.3f}s")
        print(f"  🔐 Hash : {self.hash}")

    # ── Pretty display ───────────────────────────────────────────

    def display(self) -> None:
        """Print a formatted view of this block (Block Explorer)."""
        print("  " + "─" * 62)
        print(f"  Block #{self.index}")
        print("  " + "─" * 62)
        print(f"  Timestamp    : {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.timestamp))}")
        print(f"  Data         : {self.data}")
        print(f"  Nonce        : {self.nonce}")
        print(f"  Prev Hash    : {self.previous_hash[:32]}...")
        print(f"  Hash         : {self.hash[:32]}...")
        print()


# ──────────────────────────────────────────────────────────────────
# BLOCKCHAIN CLASS
# ──────────────────────────────────────────────────────────────────

class Blockchain:
    """
    Manages the chain of blocks.

    Responsibilities:
        • Create and store the Genesis block
        • Add new blocks after Proof-of-Work mining
        • Validate the entire chain (tamper detection)
        • Expose a Block Explorer
    """

    def __init__(self, difficulty: int = 3):
        self.difficulty : int         = difficulty
        self.chain      : list[Block] = []
        self._create_genesis_block()

    # ── Genesis block ────────────────────────────────────────────

    def _create_genesis_block(self) -> None:
        """
        The Genesis block is the very first block in the chain.
        It has no predecessor, so previous_hash is set to "0".
        """
        print("\n  🌱 Creating Genesis Block ...")
        genesis = Block(0, "Genesis Block — Bytonix IT Solutions", "0")
        genesis.mine_block(self.difficulty)
        self.chain.append(genesis)

    # ── Add a new block ──────────────────────────────────────────

    def add_block(self, data: str) -> Block:
        """
        Create a new block, link it to the chain via previous_hash,
        mine it using PoW, then append to the chain.
        """
        previous_block = self.chain[-1]
        new_block      = Block(
            index         = len(self.chain),
            data          = data,
            previous_hash = previous_block.hash,
        )
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)
        return new_block

    # ── Chain validation (tamper detection) ──────────────────────

    def is_chain_valid(self) -> bool:
        """
        Walk every block and verify:
          1. Its stored hash matches a freshly computed hash
             (detects data tampering inside the block).
          2. Its previous_hash matches the actual hash of the
             preceding block (detects chain re-ordering/removal).
        """
        print("\n  🔍 Validating blockchain integrity ...\n")
        for i in range(1, len(self.chain)):
            current  = self.chain[i]
            previous = self.chain[i - 1]

            # Check 1 — stored hash still correct?
            if current.hash != current.calculate_hash():
                print(f"  ❌ Block #{i} hash is INVALID  (data was tampered!)")
                return False

            # Check 2 — cryptographic link intact?
            if current.previous_hash != previous.hash:
                print(f"  ❌ Block #{i} is NOT linked to Block #{i-1}  (chain broken!)")
                return False

            print(f"  ✔  Block #{i} OK")

        print(f"\n  ✅ All {len(self.chain)} blocks are VALID.  Chain is intact.")
        return True

    # ── Block Explorer ───────────────────────────────────────────

    def display_chain(self) -> None:
        """Print every block in the chain."""
        print(f"\n  {'═'*64}")
        print(f"  BLOCK EXPLORER  —  {len(self.chain)} blocks on chain")
        print(f"  {'═'*64}\n")
        for block in self.chain:
            block.display()

    # ── Tamper simulation ────────────────────────────────────────

    def tamper_block(self, index: int, new_data: str) -> None:
        """
        Manually overwrite data in a block to simulate an attack.
        Demonstrates that is_chain_valid() will catch the tampering.
        """
        if 0 < index < len(self.chain):
            self.chain[index].data = new_data
            # Note: hash is NOT recalculated → tampering detected on next validation
            print(f"\n  ⚠️  Block #{index} data tampered → '{new_data}'")
        else:
            print(f"\n  ❌ Cannot tamper: invalid index {index}")

    # ── Statistics ───────────────────────────────────────────────

    def stats(self) -> None:
        """Display summary statistics about the chain."""
        print(f"\n  {'─'*40}")
        print(f"  CHAIN STATISTICS")
        print(f"  {'─'*40}")
        print(f"  Total Blocks  : {len(self.chain)}")
        print(f"  Difficulty    : {self.difficulty}  ({'0'*self.difficulty}...)")
        avg_nonce = sum(b.nonce for b in self.chain) / len(self.chain)
        print(f"  Avg Nonce     : {avg_nonce:.0f}")
        print(f"  Chain Valid   : {'✅ Yes' if self._quick_validate() else '❌ No'}")

    def _quick_validate(self) -> bool:
        for i in range(1, len(self.chain)):
            c = self.chain[i]
            p = self.chain[i - 1]
            if c.hash != c.calculate_hash() or c.previous_hash != p.hash:
                return False
        return True


# ──────────────────────────────────────────────────────────────────
# INTERACTIVE CLI MENU
# ──────────────────────────────────────────────────────────────────

def print_banner() -> None:
    print()
    print("  ╔══════════════════════════════════════════════════════════╗")
    print("  ║   BLOCKCHAIN PROOF-OF-WORK SYSTEM  —  Bytonix IT        ║")
    print("  ║   Prajwal M  |  M S Ramaiah Polytechnic  |  476CS23039  ║")
    print("  ╚══════════════════════════════════════════════════════════╝")
    print()


def print_menu() -> None:
    print("\n  ┌─────────────────────────────────────────┐")
    print("  │              MAIN MENU                  │")
    print("  ├─────────────────────────────────────────┤")
    print("  │  1. Add a new block (mine)              │")
    print("  │  2. View all blocks (Block Explorer)    │")
    print("  │  3. Validate the blockchain             │")
    print("  │  4. Simulate tampering attack           │")
    print("  │  5. Show chain statistics               │")
    print("  │  6. Change mining difficulty            │")
    print("  │  7. Run demo (auto-add 3 blocks)        │")
    print("  │  0. Exit                                │")
    print("  └─────────────────────────────────────────┘")
    print("  Choice: ", end="")


def run_demo(bc: Blockchain) -> None:
    """Automatically add 3 sample transaction blocks."""
    print("\n  🚀 Running demo — adding 3 sample blocks ...\n")
    sample_transactions = [
        "Alice → Bob  :  5.00 BTC",
        "Bob   → Carol:  2.50 BTC",
        "Carol → Dave :  1.25 BTC",
    ]
    for tx in sample_transactions:
        bc.add_block(tx)
    print("\n  ✅ Demo complete.")


def main() -> None:
    print_banner()

    # Choose starting difficulty
    print("  Set initial mining difficulty (leading zeros).")
    print("  Suggested: 3 (fast) | 4 (moderate) | 5 (slow)")
    try:
        difficulty = int(input("  Difficulty [default 3]: ").strip() or "3")
        difficulty = max(1, min(difficulty, 6))          # clamp 1-6
    except ValueError:
        difficulty = 3

    # Initialise blockchain (creates genesis block)
    bc = Blockchain(difficulty)

    # ── Main loop ────────────────────────────────────────────────
    while True:
        print_menu()
        try:
            choice = input().strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n  Goodbye! 👋\n")
            break

        # ── 1. Add block ─────────────────────────────────────────
        if choice == "1":
            data = input("\n  Enter transaction / block data: ").strip()
            if data:
                bc.add_block(data)
            else:
                print("  ⚠️  No data entered. Block not added.")

        # ── 2. Block Explorer ────────────────────────────────────
        elif choice == "2":
            bc.display_chain()

        # ── 3. Validate ──────────────────────────────────────────
        elif choice == "3":
            bc.is_chain_valid()

        # ── 4. Tamper simulation ─────────────────────────────────
        elif choice == "4":
            bc.display_chain()
            try:
                idx      = int(input("  Enter block index to tamper (not genesis): "))
                new_data = input("  Enter fake data: ").strip()
                bc.tamper_block(idx, new_data)
                print("\n  Now validating chain to detect tampering ...")
                bc.is_chain_valid()
            except ValueError:
                print("  ❌ Invalid input.")

        # ── 5. Statistics ────────────────────────────────────────
        elif choice == "5":
            bc.stats()

        # ── 6. Change difficulty ─────────────────────────────────
        elif choice == "6":
            try:
                new_diff = int(input("\n  New difficulty (1-6): ").strip())
                bc.difficulty = max(1, min(new_diff, 6))
                print(f"  ✅ Difficulty updated to {bc.difficulty}.")
                print("     (New blocks will use the new difficulty.)")
            except ValueError:
                print("  ❌ Invalid input.")

        # ── 7. Demo ──────────────────────────────────────────────
        elif choice == "7":
            run_demo(bc)

        # ── 0. Exit ──────────────────────────────────────────────
        elif choice == "0":
            print("\n  Goodbye! 👋\n")
            break

        else:
            print("  ❌ Invalid choice. Try again.")


# ──────────────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    main()
