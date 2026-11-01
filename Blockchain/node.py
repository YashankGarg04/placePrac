import argparse
import json
import os
import socket
import threading
import time
from blockchain import Block, Blockchain

PORT_TO_NAME = {
    5001: "node1",
    5002: "node2",
    5003: "node3"
}


class BlockchainNode:
    def __init__(self, node_id, port, peers, log_dir="output"):
        self.node_id = node_id
        self.port = port
        self.peers = peers
        self.blockchain = Blockchain(difficulty=3)
        self.lock = threading.Lock()
        self.running = True
        self.state_file = f"state_{self.node_id}.json"

        os.makedirs(log_dir, exist_ok=True)
        self.log_file = os.path.join(log_dir, f"{self.node_id}.txt")

        if os.path.exists(self.state_file):
            self.load_local_state()
        else:
            self.save_local_state()

    def log(self, message):
        line = f"[{self.node_id}] {message}"
        print(line, flush=True)
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception:
            pass

    def save_local_state(self):
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(self.blockchain.to_list(), f, indent=2)
        except Exception:
            pass

    def load_local_state(self):
        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.blockchain.chain = Blockchain.from_list(data)
        except Exception:
            self.blockchain.create_genesis_block()

    def peer_label(self, peer_str):
        try:
            _, p = peer_str.split(":")
            return PORT_TO_NAME.get(int(p), peer_str)
        except Exception:
            return peer_str

    def start_server(self):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind(("localhost", self.port))
        server_sock.listen(10)
        server_sock.settimeout(1.0)

        def accept_loop():
            while self.running:
                try:
                    client_sock, addr = server_sock.accept()
                    threading.Thread(
                        target=self.handle_peer_request,
                        args=(client_sock, addr),
                        daemon=True
                    ).start()
                except socket.timeout:
                    continue
                except Exception:
                    break
            server_sock.close()

        threading.Thread(target=accept_loop, daemon=True).start()
        self.log(f"Started on port {self.port} with Genesis {self.blockchain.chain[0].hash[:10]}...")

    def send_message(self, peer_str, payload, expect_reply=False):
        host, port_str = peer_str.split(":")
        port = int(port_str)
        try:
            with socket.create_connection((host, port), timeout=2.0) as s:
                data = json.dumps(payload).encode("utf-8")
                s.sendall(data)
                s.shutdown(socket.SHUT_WR)
                if expect_reply:
                    chunks = []
                    while True:
                        buf = s.recv(65536)
                        if not buf:
                            break
                        chunks.append(buf)
                    if chunks:
                        return json.loads(b"".join(chunks).decode("utf-8"))
                return True
        except Exception:
            return None

    def mine_block(self, transactions):
        with self.lock:
            if not self.blockchain.is_valid():
                self.log("Cannot mine: Local chain is currently INVALID. Run 'sync' or 'reset' first.")
                return None

            prev_block = self.blockchain.get_latest_block()
            new_index = prev_block.index + 1
            self.log(f"Mining Block {new_index}...")
            new_block = Block(
                index=new_index,
                timestamp=str(int(time.time())),
                transactions=transactions,
                previous_hash=prev_block.hash,
                nonce=0,
                miner_id=self.node_id
            )
            new_block.mine(self.blockchain.difficulty)
            self.blockchain.add_block(new_block)
            self.save_local_state()
            self.log(f"Block mined: {new_block.hash[:10]}...")

        self.broadcast_block(new_block)
        return new_block

    def validate_block(self, block):
        latest = self.blockchain.get_latest_block()

        if block.index != latest.index + 1:
            self.log(f"Block {block.index} rejected: Expected index {latest.index + 1}, got {block.index}")
            return False

        if block.calculate_hash() != block.hash:
            self.log(f"Block {block.index} rejected: Hash invalid")
            return False
        self.log("Hash valid")

        if block.previous_hash != latest.hash:
            self.log(f"Block {block.index} rejected: Previous hash invalid")
            return False
        self.log("Previous hash valid")

        if not block.hash.startswith("0" * self.blockchain.difficulty):
            self.log(f"Block {block.index} rejected: Proof-of-work invalid")
            return False
        self.log("Proof-of-work valid")

        return True

    def broadcast_block(self, block):
        peer_names = ", ".join(self.peer_label(p) for p in self.peers)
        self.log(f"Broadcasting Block {block.index} to {peer_names}")
        payload = {
            "type": "NEW_BLOCK",
            "sender": self.node_id,
            "block": block.to_dict()
        }
        for peer in self.peers:
            res = self.send_message(peer, payload, expect_reply=False)
            if res is None:
                self.log(f"Peer {self.peer_label(peer)} ({peer}) unreachable during broadcast")

    def receive_block(self, block, sender_id="peer"):
        with self.lock:
            self.log(f"Block {block.index} received from {sender_id}")
            if not self.blockchain.is_valid():
                self.log("Rejected block: Local chain is currently corrupted/invalid")
                return False
            if self.validate_block(block):
                self.blockchain.chain.append(block)
                self.save_local_state()
                self.log("Block appended")
                return True
            return False

    def sync_chain(self):
        with self.lock:
            local_valid = self.blockchain.is_valid()
            local_height = len(self.blockchain.chain) - 1
            self.log(f"Local height: {local_height} (Valid: {local_valid})")

            best_chain = None
            best_len = len(self.blockchain.chain) if local_valid else 0

            for peer in self.peers:
                reply = self.send_message(
                    peer,
                    {"type": "GET_CHAIN", "sender": self.node_id},
                    expect_reply=True
                )
                if not reply or reply.get("type") != "CHAIN":
                    self.log(f"Peer {self.peer_label(peer)} unreachable")
                    continue

                peer_id = reply.get("sender", self.peer_label(peer))
                candidate_dicts = reply.get("chain", [])
                candidate_chain = Blockchain.from_list(candidate_dicts)
                peer_height = len(candidate_chain) - 1
                self.log(f"Peer ({peer_id}) height: {peer_height}")

                is_cand_valid = Blockchain.validate_chain_list(candidate_chain, self.blockchain.difficulty)
                if not is_cand_valid:
                    self.log(f"Candidate chain from {peer_id} INVALID - rejected")
                    continue

                self.log(f"Candidate chain valid")
                if len(candidate_chain) > best_len or (not local_valid and len(candidate_chain) >= len(self.blockchain.chain)):
                    best_chain = candidate_chain
                    best_len = len(candidate_chain)
                    local_valid = True

            if best_chain is not None:
                self.blockchain.chain = best_chain
                self.save_local_state()
                self.log("Local chain replaced")
                return True
            else:
                self.log("Local chain retained (no longer valid chain found)")
                return False

    def handle_peer_request(self, client_sock, addr):
        try:
            chunks = []
            while True:
                buf = client_sock.recv(65536)
                if not buf:
                    break
                chunks.append(buf)
            if not chunks:
                return
            msg = json.loads(b"".join(chunks).decode("utf-8"))
            msg_type = msg.get("type")

            if msg_type == "NEW_BLOCK":
                sender = msg.get("sender", "peer")
                block = Block.from_dict(msg["block"])
                self.receive_block(block, sender)

            elif msg_type == "GET_CHAIN":
                with self.lock:
                    response = {
                        "type": "CHAIN",
                        "sender": self.node_id,
                        "chain": self.blockchain.to_list()
                    }
                client_sock.sendall(json.dumps(response).encode("utf-8"))
        except Exception as e:
            self.log(f"Error handling peer request: {e}")
        finally:
            client_sock.close()

    def print_chain(self):
        with self.lock:
            chain_arrows = " -> ".join(f"B{b.index}({b.hash[:6]})" for b in self.blockchain.chain)
            self.log(f"Chain summary: {chain_arrows}")
            for b in self.blockchain.chain:
                print(
                    f"  Block {b.index} | Hash: {b.hash[:12]}... | Prev: {b.previous_hash[:12]}... "
                    f"| Nonce: {b.nonce} | Miner: {b.miner_id} | Tx: {b.transactions}"
                )

    def tamper_block(self, block_index, tx_index, new_tx):
        with self.lock:
            if 0 <= block_index < len(self.blockchain.chain):
                blk = self.blockchain.chain[block_index]
                if 0 <= tx_index < len(blk.transactions):
                    old_tx = blk.transactions[tx_index]
                    blk.transactions[tx_index] = new_tx
                    self.save_local_state()
                    self.log(f"Tampered Block {block_index} Tx {tx_index}: '{old_tx}' -> '{new_tx}'")
                else:
                    self.log(f"Invalid transaction index {tx_index}")
            else:
                self.log(f"Invalid block index {block_index}")

    def forge_longer_invalid_chain(self):
        """Helper for Test T8: Append unmined/invalid blocks locally so this node advertises a longer invalid chain."""
        with self.lock:
            last = self.blockchain.get_latest_block()
            fake1 = Block(last.index + 1, str(int(time.time())), ["FAKE->TX:999"], last.hash, nonce=1, miner_id=self.node_id, block_hash="999badhash" + "0" * 54)
            fake2 = Block(last.index + 2, str(int(time.time())), ["FAKE->TX:888"], fake1.hash, nonce=1, miner_id=self.node_id, block_hash="888badhash" + "0" * 54)
            self.blockchain.chain.extend([fake1, fake2])
            self.save_local_state()
            self.log(f"Injected 2 invalid blocks for T8 testing (New local height: {len(self.blockchain.chain) - 1})")


def run_cli(node):
    while node.running:
        try:
            cmd_line = input(f"{node.node_id}> ").strip()
        except (EOFError, KeyboardInterrupt):
            node.log("Shutting down node...")
            node.running = False
            break

        if not cmd_line:
            continue

        parts = cmd_line.split()
        cmd = parts[0].lower()

        if cmd == "chain":
            node.print_chain()

        elif cmd == "mine":
            if len(parts) < 2:
                print("Usage: mine <transaction>")
                continue
            tx = " ".join(parts[1:])
            node.mine_block([tx])

        elif cmd == "validate":
            valid = node.blockchain.is_valid()
            if valid:
                node.log("Local chain VALID")
            else:
                node.log("Local chain INVALID after tamper")

        elif cmd == "peers":
            node.log(f"Configured peers: {', '.join(node.peers)}")

        elif cmd == "sync":
            node.sync_chain()

        elif cmd == "tamper":
            if len(parts) < 4:
                print("Usage: tamper <block_index> <tx_index> <new_tx>")
                continue
            b_idx = int(parts[1])
            t_idx = int(parts[2])
            new_tx = " ".join(parts[3:])
            node.tamper_block(b_idx, t_idx, new_tx)

        elif cmd == "forge_invalid":
            node.forge_longer_invalid_chain()

        elif cmd == "reset":
            with node.lock:
                node.blockchain.create_genesis_block()
                node.save_local_state()
                node.log("Reset local chain to Genesis (B0)")

        elif cmd == "exit":
            node.log("Stopping node...")
            node.running = False
            break

        else:
            print("Commands: chain | mine <tx> | validate | peers | sync | tamper <blk> <tx_i> <val> | forge_invalid | reset | exit")


def main():
    parser = argparse.ArgumentParser(description="MiniChain Distributed Blockchain Node")
    parser.add_argument("--id", required=True, help="Unique node identifier (e.g., node1)")
    parser.add_argument("--port", type=int, required=True, help="Local listening port")
    parser.add_argument("--peers", required=True, help="Comma-separated list of host:port peers")
    parser.add_argument("--reset", action="store_true", help="Clear saved local state on startup")
    args = parser.parse_args()

    peers_list = [p.strip() for p in args.peers.split(",") if p.strip()]
    state_file = f"state_{args.id}.json"
    if args.reset and os.path.exists(state_file):
        os.remove(state_file)

    node = BlockchainNode(node_id=args.id, port=args.port, peers=peers_list)
    node.start_server()
    run_cli(node)


if __name__ == "__main__":
    main()