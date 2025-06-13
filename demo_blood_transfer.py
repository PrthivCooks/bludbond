
"""
Main Demo for Blood Transfer Blockchain System
This file demonstrates all functionality of the blockchain-based blood transfer system
Save as 'demo_blood_transfer.py'
"""

import json
import time
import logging
from datetime import datetime
from typing import Dict, List

# Import the blockchain system components
from blood_transfer_blockchain import BloodTransferBlockchain, HospitalNode, SmartContract
from blood_transfer_grpc_client import BloodTransferClient
from config import Config, get_config

def setup_logging():
    """Set up logging for the demo"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('blood_transfer_demo.log')
        ]
    )

def print_section(title: str):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_hospital_info(blockchain: BloodTransferBlockchain, hospital_id: str):
    """Print detailed hospital information"""
    stats = blockchain.get_hospital_stats(hospital_id)
    if stats:
        print(f"\n📍 Hospital: {stats['name']} ({stats['hospital_id']})")
        print(f"   Location: {stats['location']}")
        print(f"   Blood Credits: {stats['blood_credits']}")
        print(f"   Tampering Credits: {stats['tampering_credits']}")
        print(f"   Reputation Score: {stats['reputation_score']}")
        print(f"   Blacklisted: {stats['is_blacklisted']}")
        print(f"   Blood Inventory: {stats['blood_inventory']}")
        print(f"   Transfers Sent: {stats['total_transfers_sent']}")
        print(f"   Transfers Received: {stats['total_transfers_received']}")
    else:
        print(f"❌ Hospital {hospital_id} not found")

def demonstrate_hospital_registration(blockchain: BloodTransferBlockchain):
    """Demonstrate hospital registration functionality"""
    print_section("HOSPITAL REGISTRATION")

    hospitals = [
        ("HOSP001", "City General Hospital", (40.7128, -74.0060), 150),
        ("HOSP002", "Memorial Medical Center", (40.7589, -73.9851), 120),
        ("HOSP003", "Regional Blood Center", (40.7831, -73.9712), 200),
        ("HOSP004", "Emergency Care Hospital", (40.6782, -73.9442), 100),
        ("HOSP005", "University Medical Center", (40.8176, -73.9482), 180)
    ]

    print("🏥 Registering hospitals in the blockchain network...")

    for hospital_id, name, location, credits in hospitals:
        success = blockchain.register_hospital(hospital_id, name, location, credits)
        if success:
            print(f"✅ Registered: {name} ({hospital_id})")
        else:
            print(f"❌ Failed to register: {name} ({hospital_id})")

    print(f"\n📊 Total hospitals registered: {len(blockchain.hospitals)}")

def demonstrate_blood_inventory_management(blockchain: BloodTransferBlockchain):
    """Demonstrate blood inventory management"""
    print_section("BLOOD INVENTORY MANAGEMENT")

    # Define blood inventory for each hospital
    inventory_data = {
        "HOSP001": [("O+", 15), ("A+", 10), ("B+", 8), ("AB+", 5)],
        "HOSP002": [("O-", 12), ("A-", 6), ("B-", 4), ("O+", 20)],
        "HOSP003": [("AB+", 25), ("AB-", 8), ("A+", 15), ("B+", 12)],
        "HOSP004": [("O+", 10), ("O-", 8), ("A+", 6)],
        "HOSP005": [("B-", 10), ("AB-", 15), ("A-", 12), ("B+", 18)]
    }

    print("🩸 Adding blood inventory to hospitals...")

    for hospital_id, inventory in inventory_data.items():
        print(f"\n🏥 {blockchain.hospitals[hospital_id].name}:")
        for blood_type, quantity in inventory:
            success = blockchain.add_blood_to_inventory(hospital_id, blood_type, quantity)
            if success:
                print(f"   ✅ Added {quantity} units of {blood_type}")
            else:
                print(f"   ❌ Failed to add {blood_type}")

    # Display total blood inventory
    total_units = sum(
        sum(hospital.blood_inventory.values()) 
        for hospital in blockchain.hospitals.values()
    )
    print(f"\n📊 Total blood units in system: {total_units}")

def demonstrate_location_verification(blockchain: BloodTransferBlockchain):
    """Demonstrate GPS-based location verification"""
    print_section("GPS LOCATION VERIFICATION")

    hospital_pairs = [
        ("HOSP001", "HOSP002"),  # Close hospitals
        ("HOSP003", "HOSP004"),  # Medium distance
        ("HOSP001", "HOSP005"),  # Longer distance
    ]

    print("📍 Testing location proximity for blood transfers...")

    for sender_id, receiver_id in hospital_pairs:
        sender = blockchain.hospitals[sender_id]
        receiver = blockchain.hospitals[receiver_id]

        distance = blockchain.calculate_distance(
            sender.location[0], sender.location[1],
            receiver.location[0], receiver.location[1]
        )

        is_valid = blockchain.verify_location_proximity(sender_id, receiver_id)

        print(f"\n🔄 {sender.name} → {receiver.name}")
        print(f"   Distance: {distance:.2f} km")
        print(f"   Within transfer range: {'✅ Yes' if is_valid else '❌ No'}")

def demonstrate_blood_transfers(blockchain: BloodTransferBlockchain):
    """Demonstrate blood transfer transactions"""
    print_section("BLOOD TRANSFER TRANSACTIONS")

    # Define transfer scenarios
    transfers = [
        ("HOSP001", "HOSP002", "O+", 3, "urgent"),
        ("HOSP003", "HOSP004", "AB+", 2, "normal"),
        ("HOSP002", "HOSP001", "O-", 1, "emergency"),
        ("HOSP005", "HOSP003", "B+", 4, "normal"),
        ("HOSP001", "HOSP005", "A+", 2, "urgent")
    ]

    print("🔄 Creating blood transfer transactions...")

    successful_transfers = []

    for sender_id, receiver_id, blood_type, quantity, urgency in transfers:
        sender_name = blockchain.hospitals[sender_id].name
        receiver_name = blockchain.hospitals[receiver_id].name

        print(f"\n📋 Transfer Request:")
        print(f"   From: {sender_name} ({sender_id})")
        print(f"   To: {receiver_name} ({receiver_id})")
        print(f"   Blood Type: {blood_type}")
        print(f"   Quantity: {quantity} units")
        print(f"   Urgency: {urgency}")

        transaction = blockchain.create_blood_transfer_transaction(
            sender_id, receiver_id, blood_type, quantity, urgency
        )

        if transaction:
            blockchain.pending_transactions.append(transaction)
            successful_transfers.append(transaction)
            print(f"   ✅ Transaction created: {transaction['transaction_id'][:8]}...")
            print(f"   Distance: {transaction['distance_km']:.2f} km")
        else:
            print(f"   ❌ Transaction failed - check requirements")

    print(f"\n📊 Successful transfer requests: {len(successful_transfers)}")
    return successful_transfers

def demonstrate_tampering_detection(blockchain: BloodTransferBlockchain):
    """Demonstrate tampering detection and penalty system"""
    print_section("TAMPERING DETECTION & PENALTIES")

    print("🚨 Simulating tampering scenarios...")

    # Simulate tampering by HOSP004
    print("\n⚠️  Scenario 1: HOSP004 submits invalid blood data")
    blockchain.penalize_tampering("HOSP004", "Submitted blood with falsified expiry date")

    print("\n⚠️  Scenario 2: HOSP004 attempts data manipulation")
    blockchain.penalize_tampering("HOSP004", "Attempted to modify transaction data")

    # Show hospital status after penalties
    print("\n📊 Hospital status after tampering violations:")
    print_hospital_info(blockchain, "HOSP004")

    # Try to create a transfer from blacklisted hospital
    print("\n🔄 Attempting transfer from blacklisted hospital...")
    transaction = blockchain.create_blood_transfer_transaction(
        "HOSP004", "HOSP001", "O+", 2, "normal"
    )

    if transaction:
        print("   ❌ Transfer should have been blocked!")
    else:
        print("   ✅ Transfer correctly blocked from blacklisted hospital")

def demonstrate_blockchain_mining(blockchain: BloodTransferBlockchain):
    """Demonstrate blockchain mining and validation"""
    print_section("BLOCKCHAIN MINING & VALIDATION")

    print(f"📊 Current blockchain status:")
    print(f"   Blocks in chain: {len(blockchain.chain)}")
    print(f"   Pending transactions: {len(blockchain.pending_transactions)}")

    if blockchain.pending_transactions:
        print("\n⛏️  Mining pending transactions...")

        # Mine transactions in batches
        miners = ["HOSP001", "HOSP002", "HOSP003", "HOSP005"]
        miner_index = 0

        while blockchain.pending_transactions:
            miner = miners[miner_index % len(miners)]

            print(f"\n🔨 {blockchain.hospitals[miner].name} is mining...")
            start_time = time.time()

            new_block = blockchain.mine_pending_transactions(miner)

            if new_block:
                mining_time = time.time() - start_time
                print(f"   ✅ Block {new_block['index']} mined in {mining_time:.2f}s")
                print(f"   📋 Transactions in block: {len(new_block['transactions'])}")
                print(f"   🔒 Block hash: {new_block['hash'][:16]}...")

            miner_index += 1

            # Safety break
            if miner_index > 10:
                break

    print(f"\n📊 Final blockchain status:")
    print(f"   Total blocks: {len(blockchain.chain)}")
    print(f"   Remaining pending transactions: {len(blockchain.pending_transactions)}")
    print(f"   Chain valid: {'✅ Yes' if blockchain.validate_chain() else '❌ No'}")

def demonstrate_system_statistics(blockchain: BloodTransferBlockchain):
    """Demonstrate system statistics and reporting"""
    print_section("SYSTEM STATISTICS & REPORTING")

    # Overall system stats
    stats = blockchain.get_system_stats()
    print("🔍 System Overview:")
    print(f"   Total Hospitals: {stats['total_hospitals']}")
    print(f"   Active Hospitals: {stats['active_hospitals']}")
    print(f"   Blacklisted Hospitals: {stats['blacklisted_hospitals']}")
    print(f"   Total Blood Units: {stats['total_blood_units']}")
    print(f"   Blockchain Length: {stats['blockchain_length']}")
    print(f"   Pending Transactions: {stats['pending_transactions']}")
    print(f"   Chain Valid: {'✅ Yes' if stats['is_chain_valid'] else '❌ No'}")

    # Individual hospital statistics
    print("\n🏥 Hospital Details:")
    for hospital_id in ["HOSP001", "HOSP002", "HOSP003", "HOSP005"]:  # Skip blacklisted HOSP004
        print_hospital_info(blockchain, hospital_id)

    # Blood type distribution
    print("\n🩸 Blood Type Distribution:")
    blood_types = {}
    for hospital in blockchain.hospitals.values():
        for blood_type, quantity in hospital.blood_inventory.items():
            blood_types[blood_type] = blood_types.get(blood_type, 0) + quantity

    for blood_type, total in sorted(blood_types.items()):
        print(f"   {blood_type}: {total} units")

def demonstrate_grpc_communication():
    """Demonstrate gRPC client-server communication"""
    print_section("gRPC COMMUNICATION DEMO")

    print("🌐 Setting up gRPC client for hospital communication...")

    # Create gRPC client for a hospital
    client = BloodTransferClient("HOSP001", "localhost:50051", use_tls=False)

    print("\n🔗 Testing network connectivity...")
    if client.check_network_status():
        print("   ✅ gRPC network connection established")

        # Demonstrate registration
        print("\n📝 Testing hospital registration via gRPC...")
        success, message = client.register_hospital(
            name="Remote Hospital",
            latitude=40.6892,
            longitude=-74.0445,
            initial_credits=125
        )
        print(f"   {message}")

        # Demonstrate blood transfer request
        print("\n🔄 Testing blood transfer request via gRPC...")
        success, message, tx_id = client.request_blood_transfer(
            receiver_id="HOSP002",
            blood_type="O+",
            quantity=2,
            urgency_level="urgent"
        )
        print(f"   {message}")
        if tx_id:
            print(f"   Transaction ID: {tx_id}")

        # Demonstrate proximity verification
        print("\n📍 Testing location proximity via gRPC...")
        success, message = client.verify_location_proximity("HOSP002")
        print(f"   {message}")

    else:
        print("   ⚠️  gRPC server not available (this is expected in demo mode)")
        print("   💡 To test gRPC: run 'python blood_transfer_grpc_server.py' in another terminal")

def main():
    """Main demo function"""
    print("🩸 BLOCKCHAIN-BASED BLOOD TRANSFER SYSTEM DEMO 🩸")
    print("=" * 60)
    print("This demo showcases all features of the blood transfer blockchain system:")
    print("• Hospital registration and management")
    print("• Blood inventory tracking")
    print("• GPS-based location verification")
    print("• Smart contract validation")
    print("• Tampering detection and penalties")
    print("• Blockchain mining and validation")
    print("• gRPC secure communication")
    print("• System statistics and reporting")

    # Set up logging
    setup_logging()

    # Initialize blockchain
    blockchain = BloodTransferBlockchain()

    try:
        # Run demonstrations
        demonstrate_hospital_registration(blockchain)
        demonstrate_blood_inventory_management(blockchain)
        demonstrate_location_verification(blockchain)
        demonstrate_blood_transfers(blockchain)
        demonstrate_tampering_detection(blockchain)
        demonstrate_blockchain_mining(blockchain)
        demonstrate_system_statistics(blockchain)
        demonstrate_grpc_communication()

        print_section("DEMO COMPLETED SUCCESSFULLY")
        print("✅ All blockchain features demonstrated successfully!")
        print("\n📄 Generated files:")
        print("   • blood_transfer_demo.log - Demo execution log")
        print("   • Check other .py files for complete implementation")

        print("\n🚀 Next steps:")
        print("   • Run tests: python test_blood_transfer.py")
        print("   • Start gRPC server: python blood_transfer_grpc_server.py")
        print("   • Customize configuration in config.py")

    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        logging.error(f"Demo failed: {e}", exc_info=True)

    finally:
        print("\n🏁 Demo session ended")

if __name__ == "__main__":
    main()
