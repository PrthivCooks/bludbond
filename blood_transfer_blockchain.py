
"""
Complete Blockchain-based Blood Transfer System
This file contains the full implementation of the blockchain system
Save as 'blood_transfer_blockchain.py'
"""

import json
import hashlib
import time
import math
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import logging

@dataclass
class BloodUnit:
    """Represents a unit of blood in the system"""
    unit_id: str
    blood_type: str
    expiry_date: datetime
    donor_info: Dict[str, Any]
    quality_score: float
    location: str

class HospitalNode:
    """Represents a hospital node in the network"""

    def __init__(self, hospital_id: str, name: str, location: Tuple[float, float], 
                 initial_blood_credits: int = 100, tampering_credits: int = 2):
        self.hospital_id = hospital_id
        self.name = name
        self.location = location  # (latitude, longitude)
        self.blood_credits = initial_blood_credits
        self.tampering_credits = tampering_credits
        self.blood_inventory = {}
        self.transaction_history = []
        self.is_blacklisted = False
        self.reputation_score = 100
        self.total_transfers_sent = 0
        self.total_transfers_received = 0

    def to_dict(self):
        return {
            'hospital_id': self.hospital_id,
            'name': self.name,
            'location': self.location,
            'blood_credits': self.blood_credits,
            'tampering_credits': self.tampering_credits,
            'blood_inventory': self.blood_inventory,
            'is_blacklisted': self.is_blacklisted,
            'reputation_score': self.reputation_score,
            'total_transfers_sent': self.total_transfers_sent,
            'total_transfers_received': self.total_transfers_received
        }

class SmartContract:
    """Smart contract for blood transfer validation"""

    @staticmethod
    def validate_blood_transfer(sender: HospitalNode, receiver: HospitalNode, 
                              blood_type: str, quantity: int, distance: float) -> Tuple[bool, str]:
        """Validate if a blood transfer should be allowed"""

        # Check if hospitals are blacklisted
        if sender.is_blacklisted:
            return False, f"Sender hospital {sender.hospital_id} is blacklisted"
        if receiver.is_blacklisted:
            return False, f"Receiver hospital {receiver.hospital_id} is blacklisted"

        # Check blood credits
        min_credits = 10
        if sender.blood_credits < min_credits:
            return False, f"Sender has insufficient blood credits ({sender.blood_credits} < {min_credits})"

        # Check blood inventory
        if blood_type not in sender.blood_inventory or sender.blood_inventory[blood_type] < quantity:
            return False, f"Insufficient {blood_type} inventory at sender hospital"

        # Check distance constraints
        max_distance = 100.0  # Maximum 100km for blood transfer
        if distance > max_distance:
            return False, f"Transfer distance ({distance:.2f}km) exceeds maximum allowed ({max_distance}km)"

        # All checks passed
        return True, "Transfer validation successful"

    @staticmethod
    def execute_blood_transfer(sender: HospitalNode, receiver: HospitalNode, 
                             blood_type: str, quantity: int) -> bool:
        """Execute the blood transfer between hospitals"""
        try:
            # Deduct from sender
            sender.blood_inventory[blood_type] -= quantity
            sender.blood_credits -= 5  # Small cost for transfer
            sender.total_transfers_sent += 1

            # Add to receiver
            if blood_type not in receiver.blood_inventory:
                receiver.blood_inventory[blood_type] = 0
            receiver.blood_inventory[blood_type] += quantity
            receiver.blood_credits += 2  # Small reward for receiving
            receiver.total_transfers_received += 1

            return True
        except Exception as e:
            logging.error(f"Error executing blood transfer: {e}")
            return False

class BloodTransferBlockchain:
    """
    Main blockchain implementation for secure blood transfer system
    """

    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.hospitals = {}
        self.blood_inventory = {}
        self.mining_difficulty = 4
        self.mining_reward = 100
        self.max_transactions_per_block = 10
        self.logger = logging.getLogger(__name__)

        # Initialize with genesis block
        self.create_genesis_block()

    def create_genesis_block(self):
        """Create the first block in the blockchain"""
        genesis_block = {
            'index': 0,
            'timestamp': time.time(),
            'transactions': [],
            'proof': 0,
            'previous_hash': '0',
            'merkle_root': self.calculate_merkle_root([]),
            'validator': 'system'
        }
        genesis_block['hash'] = self.calculate_hash(genesis_block)
        self.chain.append(genesis_block)
        self.logger.info("Genesis block created")

    def calculate_hash(self, block: Dict) -> str:
        """Calculate SHA-256 hash of a block"""
        block_string = json.dumps(block, sort_keys=True, default=str)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def calculate_merkle_root(self, transactions: List[Dict]) -> str:
        """Calculate Merkle root of transactions for integrity verification"""
        if not transactions:
            return hashlib.sha256(b'').hexdigest()

        transaction_hashes = [
            hashlib.sha256(json.dumps(tx, sort_keys=True).encode()).hexdigest() 
            for tx in transactions
        ]

        while len(transaction_hashes) > 1:
            if len(transaction_hashes) % 2 != 0:
                transaction_hashes.append(transaction_hashes[-1])

            new_hashes = []
            for i in range(0, len(transaction_hashes), 2):
                combined = transaction_hashes[i] + transaction_hashes[i + 1]
                new_hashes.append(hashlib.sha256(combined.encode()).hexdigest())

            transaction_hashes = new_hashes

        return transaction_hashes[0]

    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two GPS coordinates using Haversine formula"""
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))

        return c * 6371  # Earth radius in kilometers

    def register_hospital(self, hospital_id: str, name: str, location: Tuple[float, float], 
                         initial_credits: int = 100) -> bool:
        """Register a new hospital in the network"""
        if hospital_id in self.hospitals:
            self.logger.warning(f"Hospital {hospital_id} already registered")
            return False

        hospital = HospitalNode(hospital_id, name, location, initial_credits)
        self.hospitals[hospital_id] = hospital

        # Create registration transaction
        registration_tx = {
            'type': 'hospital_registration',
            'hospital_id': hospital_id,
            'name': name,
            'location': location,
            'initial_credits': initial_credits,
            'timestamp': time.time(),
            'transaction_id': str(uuid.uuid4())
        }

        self.pending_transactions.append(registration_tx)
        self.logger.info(f"Hospital {hospital_id} registered successfully")
        return True

    def add_blood_to_inventory(self, hospital_id: str, blood_type: str, quantity: int) -> bool:
        """Add blood units to hospital inventory"""
        if hospital_id not in self.hospitals:
            return False

        hospital = self.hospitals[hospital_id]
        if blood_type not in hospital.blood_inventory:
            hospital.blood_inventory[blood_type] = 0

        hospital.blood_inventory[blood_type] += quantity

        # Create inventory update transaction
        inventory_tx = {
            'type': 'inventory_update',
            'hospital_id': hospital_id,
            'blood_type': blood_type,
            'quantity_added': quantity,
            'new_total': hospital.blood_inventory[blood_type],
            'timestamp': time.time(),
            'transaction_id': str(uuid.uuid4())
        }

        self.pending_transactions.append(inventory_tx)
        return True

    def verify_location_proximity(self, sender_id: str, receiver_id: str, 
                                max_distance: float = 100.0) -> bool:
        """Verify that hospitals are within acceptable distance"""
        if sender_id not in self.hospitals or receiver_id not in self.hospitals:
            return False

        sender_location = self.hospitals[sender_id].location
        receiver_location = self.hospitals[receiver_id].location

        distance = self.calculate_distance(
            sender_location[0], sender_location[1],
            receiver_location[0], receiver_location[1]
        )

        return distance <= max_distance

    def create_blood_transfer_transaction(self, sender_id: str, receiver_id: str, 
                                        blood_type: str, quantity: int, 
                                        urgency_level: str = "normal") -> Optional[Dict]:
        """Create and validate a blood transfer transaction"""
        if (sender_id not in self.hospitals or receiver_id not in self.hospitals):
            self.logger.error("Invalid hospital IDs")
            return None

        sender = self.hospitals[sender_id]
        receiver = self.hospitals[receiver_id]

        # Calculate distance
        distance = self.calculate_distance(
            sender.location[0], sender.location[1],
            receiver.location[0], receiver.location[1]
        )

        # Validate transfer using smart contract
        is_valid, message = SmartContract.validate_blood_transfer(
            sender, receiver, blood_type, quantity, distance
        )

        if not is_valid:
            self.logger.warning(f"Transfer validation failed: {message}")
            return None

        # Create transaction
        transaction = {
            'type': 'blood_transfer',
            'transaction_id': str(uuid.uuid4()),
            'sender_id': sender_id,
            'receiver_id': receiver_id,
            'blood_type': blood_type,
            'quantity': quantity,
            'urgency_level': urgency_level,
            'distance_km': distance,
            'timestamp': time.time(),
            'status': 'pending',
            'verification_hash': self.generate_verification_hash(sender_id, receiver_id, blood_type, quantity)
        }

        self.logger.info(f"Blood transfer transaction created: {transaction['transaction_id']}")
        return transaction

    def generate_verification_hash(self, sender_id: str, receiver_id: str, 
                                 blood_type: str, quantity: int) -> str:
        """Generate verification hash to prevent tampering"""
        data = f"{sender_id}{receiver_id}{blood_type}{quantity}{time.time()}"
        return hashlib.sha256(data.encode()).hexdigest()

    def penalize_tampering(self, hospital_id: str, reason: str = "Data tampering detected") -> bool:
        """Penalize hospital for tampering or providing bad data"""
        if hospital_id not in self.hospitals:
            return False

        hospital = self.hospitals[hospital_id]
        hospital.tampering_credits -= 1
        hospital.reputation_score = max(0, hospital.reputation_score - 15)

        if hospital.tampering_credits <= 0:
            hospital.is_blacklisted = True
            self.logger.warning(f"Hospital {hospital_id} blacklisted due to tampering violations")

        # Create penalty transaction
        penalty_tx = {
            'type': 'tampering_penalty',
            'hospital_id': hospital_id,
            'reason': reason,
            'remaining_tampering_credits': hospital.tampering_credits,
            'new_reputation_score': hospital.reputation_score,
            'is_blacklisted': hospital.is_blacklisted,
            'timestamp': time.time(),
            'transaction_id': str(uuid.uuid4())
        }

        self.pending_transactions.append(penalty_tx)
        return True

    def proof_of_work(self, last_proof: int, last_hash: str) -> int:
        """Simple proof of work algorithm for mining"""
        proof = 0
        while not self.valid_proof(last_proof, proof, last_hash):
            proof += 1
        return proof

    def valid_proof(self, last_proof: int, proof: int, last_hash: str) -> bool:
        """Validate the proof of work"""
        guess = f'{last_proof}{proof}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:self.mining_difficulty] == "0" * self.mining_difficulty

    def mine_pending_transactions(self, miner_id: str) -> Optional[Dict]:
        """Mine pending transactions into a new block"""
        if not self.pending_transactions:
            self.logger.info("No pending transactions to mine")
            return None

        # Take up to max_transactions_per_block transactions
        transactions_to_mine = self.pending_transactions[:self.max_transactions_per_block]

        # Get last block
        last_block = self.chain[-1]

        # Create new block
        new_block = {
            'index': len(self.chain),
            'timestamp': time.time(),
            'transactions': transactions_to_mine,
            'previous_hash': last_block['hash'],
            'merkle_root': self.calculate_merkle_root(transactions_to_mine),
            'validator': miner_id
        }

        # Proof of work
        new_block['proof'] = self.proof_of_work(last_block['proof'], last_block['hash'])
        new_block['hash'] = self.calculate_hash(new_block)

        # Add block to chain
        self.chain.append(new_block)

        # Remove mined transactions from pending
        self.pending_transactions = self.pending_transactions[self.max_transactions_per_block:]

        # Execute blood transfers in the block
        for tx in transactions_to_mine:
            if tx['type'] == 'blood_transfer':
                sender = self.hospitals[tx['sender_id']]
                receiver = self.hospitals[tx['receiver_id']]
                SmartContract.execute_blood_transfer(
                    sender, receiver, tx['blood_type'], tx['quantity']
                )

        self.logger.info(f"Block {new_block['index']} mined by {miner_id}")
        return new_block

    def validate_chain(self) -> bool:
        """Validate the entire blockchain"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            # Check if current block hash is correct
            if current_block['hash'] != self.calculate_hash(current_block):
                return False

            # Check if previous hash matches
            if current_block['previous_hash'] != previous_block['hash']:
                return False

            # Validate proof of work
            if not self.valid_proof(previous_block['proof'], current_block['proof'], 
                                  previous_block['hash']):
                return False

        return True

    def get_hospital_stats(self, hospital_id: str) -> Optional[Dict]:
        """Get comprehensive statistics for a hospital"""
        if hospital_id not in self.hospitals:
            return None

        hospital = self.hospitals[hospital_id]

        # Calculate transaction count
        tx_count = 0
        for block in self.chain:
            for tx in block['transactions']:
                if (tx.get('sender_id') == hospital_id or 
                    tx.get('receiver_id') == hospital_id or
                    tx.get('hospital_id') == hospital_id):
                    tx_count += 1

        return {
            **hospital.to_dict(),
            'total_transactions': tx_count,
            'blockchain_blocks': len(self.chain),
            'pending_transactions': len(self.pending_transactions)
        }

    def get_system_stats(self) -> Dict:
        """Get overall system statistics"""
        total_hospitals = len(self.hospitals)
        active_hospitals = len([h for h in self.hospitals.values() if not h.is_blacklisted])
        blacklisted_hospitals = total_hospitals - active_hospitals

        total_blood_units = sum(
            sum(hospital.blood_inventory.values()) 
            for hospital in self.hospitals.values()
        )

        return {
            'total_hospitals': total_hospitals,
            'active_hospitals': active_hospitals,
            'blacklisted_hospitals': blacklisted_hospitals,
            'total_blood_units': total_blood_units,
            'blockchain_length': len(self.chain),
            'pending_transactions': len(self.pending_transactions),
            'is_chain_valid': self.validate_chain()
        }

# Example usage and testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Create blockchain instance
    blockchain = BloodTransferBlockchain()

    # Register hospitals
    blockchain.register_hospital("HOSP001", "City General Hospital", (40.7128, -74.0060), 150)
    blockchain.register_hospital("HOSP002", "Memorial Medical Center", (40.7589, -73.9851), 120)
    blockchain.register_hospital("HOSP003", "Regional Blood Center", (40.7831, -73.9712), 200)

    # Add blood inventory
    blockchain.add_blood_to_inventory("HOSP001", "O+", 10)
    blockchain.add_blood_to_inventory("HOSP001", "A+", 5)
    blockchain.add_blood_to_inventory("HOSP002", "B+", 8)
    blockchain.add_blood_to_inventory("HOSP003", "AB+", 15)

    # Create blood transfer transactions
    tx1 = blockchain.create_blood_transfer_transaction("HOSP001", "HOSP002", "O+", 2, "urgent")
    if tx1:
        blockchain.pending_transactions.append(tx1)

    tx2 = blockchain.create_blood_transfer_transaction("HOSP003", "HOSP001", "AB+", 3, "normal")
    if tx2:
        blockchain.pending_transactions.append(tx2)

    # Mine a block
    new_block = blockchain.mine_pending_transactions("HOSP001")

    # Print results
    print("\n=== Blockchain Blood Transfer System Demo ===")
    print(f"System Stats: {blockchain.get_system_stats()}")
    print(f"\nHOSP001 Stats: {blockchain.get_hospital_stats('HOSP001')}")
    print(f"\nChain is valid: {blockchain.validate_chain()}")

    # Test tampering penalty
    blockchain.penalize_tampering("HOSP002", "Submitted invalid blood data")
    print(f"\nHOSP002 after penalty: {blockchain.get_hospital_stats('HOSP002')}")
