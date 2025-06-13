# Blockchain-Based Blood Transfer System

A comprehensive blockchain implementation for secure blood transfer between hospitals with gRPC communication, GPS verification, and tampering prevention.

## Features

### Core Blockchain Features
- Complete blockchain implementation with proof-of-work mining
- Smart contracts for blood transfer validation
- Merkle tree transaction verification
- Immutable transaction ledger

### Hospital Management
- Hospital registration and authentication
- Blood inventory tracking and management
- Reputation scoring system
- Blacklisting for tampering violations

### Security & Verification
- GPS-based location proximity verification
- Credit system with minimum transfer requirements
- Tampering detection and penalty system
- Cryptographic hash verification

### Communication
- Secure gRPC server-to-server communication
- TLS encryption support
- Real-time blood transfer requests
- Network status monitoring

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the demo:
```bash
python demo_blood_transfer.py
```

3. Run tests:
```bash
python test_blood_transfer.py
```

4. Start gRPC server (optional):
```bash
python blood_transfer_grpc_server.py
```

## Files Overview

- `blood_transfer_blockchain.py` - Complete blockchain implementation
- `blood_transfer_grpc_server.py` - gRPC server for hospital communication
- `blood_transfer_grpc_client.py` - gRPC client for hospital connections
- `config.py` - System configuration and settings
- `demo_blood_transfer.py` - Comprehensive system demonstration
- `test_blood_transfer.py` - Complete test suite
- `requirements.txt` - Python dependencies

## Usage Example

```python
from blood_transfer_blockchain import BloodTransferBlockchain

# Create blockchain
blockchain = BloodTransferBlockchain()

# Register hospitals
blockchain.register_hospital("HOSP001", "City Hospital", (40.7128, -74.0060), 150)
blockchain.register_hospital("HOSP002", "Memorial Hospital", (40.7589, -73.9851), 120)

# Add blood inventory
blockchain.add_blood_to_inventory("HOSP001", "O+", 10)

# Create blood transfer
transaction = blockchain.create_blood_transfer_transaction(
    "HOSP001", "HOSP002", "O+", 2, "urgent"
)

# Mine transactions
blockchain.pending_transactions.append(transaction)
new_block = blockchain.mine_pending_transactions("HOSP001")
```

## Configuration

Modify `config.py` to customize:
- Mining difficulty
- Transfer distance limits
- Credit requirements
- gRPC settings
- Security parameters

## Security Features

1. **GPS Verification**: Ensures blood is transferred only between nearby hospitals
2. **Credit System**: Requires minimum blood credits for transfer initiation
3. **Tampering Detection**: Tracks and penalizes fraudulent behavior
4. **Blockchain Integrity**: Immutable transaction history with cryptographic verification
5. **gRPC Security**: Secure communication with TLS encryption support

## Testing

The system includes comprehensive tests covering:
- Blockchain functionality
- Hospital management
- Blood transfer validation
- Security features
- Performance metrics

## License

This implementation is for educational and research purposes.
