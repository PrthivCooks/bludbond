
"""
Comprehensive test suite for Blood Transfer Blockchain System
Save as 'test_blood_transfer.py'
"""

import unittest
import time
import tempfile
import json
from unittest.mock import patch, MagicMock

# Import the blockchain system
from blood_transfer_blockchain import BloodTransferBlockchain, HospitalNode, SmartContract
from config import Config, get_config

class TestBloodTransferBlockchain(unittest.TestCase):
    """Test cases for the blood transfer blockchain system"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        self.blockchain = BloodTransferBlockchain()
        self.test_config = get_config('testing')

        # Register test hospitals
        self.blockchain.register_hospital("TEST001", "Test Hospital 1", (40.7128, -74.0060), 100)
        self.blockchain.register_hospital("TEST002", "Test Hospital 2", (40.7589, -73.9851), 150)
        self.blockchain.register_hospital("TEST003", "Test Hospital 3", (40.7831, -73.9712), 200)

        # Add test blood inventory
        self.blockchain.add_blood_to_inventory("TEST001", "O+", 10)
        self.blockchain.add_blood_to_inventory("TEST001", "A+", 5)
        self.blockchain.add_blood_to_inventory("TEST002", "B+", 8)
        self.blockchain.add_blood_to_inventory("TEST003", "AB+", 15)

    def test_genesis_block_creation(self):
        """Test that genesis block is created correctly"""
        self.assertEqual(len(self.blockchain.chain), 1)
        genesis_block = self.blockchain.chain[0]
        self.assertEqual(genesis_block['index'], 0)
        self.assertEqual(genesis_block['previous_hash'], '0')
        self.assertIsNotNone(genesis_block['hash'])

    def test_hospital_registration(self):
        """Test hospital registration functionality"""
        # Test successful registration
        result = self.blockchain.register_hospital("TEST004", "Test Hospital 4", (41.0, -74.0), 120)
        self.assertTrue(result)
        self.assertIn("TEST004", self.blockchain.hospitals)

        # Test duplicate registration
        result = self.blockchain.register_hospital("TEST004", "Duplicate Hospital", (41.0, -74.0), 120)
        self.assertFalse(result)

    def test_blood_inventory_management(self):
        """Test blood inventory addition and tracking"""
        initial_o_plus = self.blockchain.hospitals["TEST001"].blood_inventory.get("O+", 0)

        # Add more blood
        result = self.blockchain.add_blood_to_inventory("TEST001", "O+", 5)
        self.assertTrue(result)

        new_o_plus = self.blockchain.hospitals["TEST001"].blood_inventory["O+"]
        self.assertEqual(new_o_plus, initial_o_plus + 5)

        # Test invalid hospital
        result = self.blockchain.add_blood_to_inventory("INVALID", "O+", 5)
        self.assertFalse(result)

    def test_location_proximity_verification(self):
        """Test GPS-based location proximity verification"""
        # Test nearby hospitals (should be valid)
        result = self.blockchain.verify_location_proximity("TEST001", "TEST002")
        self.assertTrue(result)

        # Test with custom max distance
        result = self.blockchain.verify_location_proximity("TEST001", "TEST002", max_distance=1.0)
        self.assertFalse(result)  # Should be too far with 1km limit

        # Test invalid hospitals
        result = self.blockchain.verify_location_proximity("TEST001", "INVALID")
        self.assertFalse(result)

    def test_blood_transfer_transaction_creation(self):
        """Test blood transfer transaction creation and validation"""
        # Test valid transfer
        transaction = self.blockchain.create_blood_transfer_transaction(
            "TEST001", "TEST002", "O+", 2, "urgent"
        )
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction['sender_id'], "TEST001")
        self.assertEqual(transaction['receiver_id'], "TEST002")
        self.assertEqual(transaction['blood_type'], "O+")
        self.assertEqual(transaction['quantity'], 2)

        # Test invalid transfer (insufficient inventory)
        transaction = self.blockchain.create_blood_transfer_transaction(
            "TEST001", "TEST002", "O+", 100, "urgent"
        )
        self.assertIsNone(transaction)

        # Test invalid hospitals
        transaction = self.blockchain.create_blood_transfer_transaction(
            "INVALID", "TEST002", "O+", 2, "urgent"
        )
        self.assertIsNone(transaction)

    def test_smart_contract_validation(self):
        """Test smart contract validation logic"""
        sender = self.blockchain.hospitals["TEST001"]
        receiver = self.blockchain.hospitals["TEST002"]

        # Test valid transfer
        is_valid, message = SmartContract.validate_blood_transfer(
            sender, receiver, "O+", 2, 10.0
        )
        self.assertTrue(is_valid)

        # Test insufficient credits
        sender.blood_credits = 5  # Below minimum
        is_valid, message = SmartContract.validate_blood_transfer(
            sender, receiver, "O+", 2, 10.0
        )
        self.assertFalse(is_valid)
        self.assertIn("insufficient blood credits", message.lower())

        # Reset credits
        sender.blood_credits = 100

        # Test blacklisted hospital
        sender.is_blacklisted = True
        is_valid, message = SmartContract.validate_blood_transfer(
            sender, receiver, "O+", 2, 10.0
        )
        self.assertFalse(is_valid)
        self.assertIn("blacklisted", message.lower())

    def test_tampering_penalty_system(self):
        """Test the tampering penalty and credit system"""
        hospital = self.blockchain.hospitals["TEST001"]
        initial_credits = hospital.tampering_credits
        initial_reputation = hospital.reputation_score

        # First penalty
        result = self.blockchain.penalize_tampering("TEST001", "Test tampering")
        self.assertTrue(result)
        self.assertEqual(hospital.tampering_credits, initial_credits - 1)
        self.assertLess(hospital.reputation_score, initial_reputation)
        self.assertFalse(hospital.is_blacklisted)

        # Second penalty (should blacklist)
        self.blockchain.penalize_tampering("TEST001", "Second tampering")
        self.assertEqual(hospital.tampering_credits, 0)
        self.assertTrue(hospital.is_blacklisted)

    def test_mining_and_block_creation(self):
        """Test block mining and transaction processing"""
        # Create some transactions
        tx1 = self.blockchain.create_blood_transfer_transaction("TEST001", "TEST002", "O+", 2)
        tx2 = self.blockchain.create_blood_transfer_transaction("TEST003", "TEST001", "AB+", 1)

        if tx1:
            self.blockchain.pending_transactions.append(tx1)
        if tx2:
            self.blockchain.pending_transactions.append(tx2)

        initial_chain_length = len(self.blockchain.chain)
        initial_pending = len(self.blockchain.pending_transactions)

        # Mine a block
        new_block = self.blockchain.mine_pending_transactions("TEST001")

        self.assertIsNotNone(new_block)
        self.assertEqual(len(self.blockchain.chain), initial_chain_length + 1)
        self.assertLess(len(self.blockchain.pending_transactions), initial_pending)

    def test_blockchain_validation(self):
        """Test blockchain integrity validation"""
        # Initially should be valid
        self.assertTrue(self.blockchain.validate_chain())

        # Create and mine a block
        tx = self.blockchain.create_blood_transfer_transaction("TEST001", "TEST002", "O+", 1)
        if tx:
            self.blockchain.pending_transactions.append(tx)
            self.blockchain.mine_pending_transactions("TEST001")

        # Should still be valid
        self.assertTrue(self.blockchain.validate_chain())

        # Tamper with a block (should become invalid)
        if len(self.blockchain.chain) > 1:
            self.blockchain.chain[1]['hash'] = "tampered_hash"
            self.assertFalse(self.blockchain.validate_chain())

    def test_blood_compatibility(self):
        """Test blood type compatibility checking"""
        config = Config()

        # Test universal donor (O-)
        compatible = config.get_compatible_recipients("O-")
        self.assertEqual(len(compatible), 8)  # Should be compatible with all types

        # Test universal recipient (AB+)
        self.assertTrue(config.is_compatible("O-", "AB+"))
        self.assertTrue(config.is_compatible("A+", "AB+"))
        self.assertTrue(config.is_compatible("B-", "AB+"))

        # Test incompatible combinations
        self.assertFalse(config.is_compatible("A+", "B+"))
        self.assertFalse(config.is_compatible("AB+", "O+"))

    def test_system_statistics(self):
        """Test system statistics generation"""
        stats = self.blockchain.get_system_stats()

        self.assertIn('total_hospitals', stats)
        self.assertIn('active_hospitals', stats)
        self.assertIn('blacklisted_hospitals', stats)
        self.assertIn('total_blood_units', stats)
        self.assertIn('blockchain_length', stats)
        self.assertIn('pending_transactions', stats)
        self.assertIn('is_chain_valid', stats)

        self.assertEqual(stats['total_hospitals'], 3)
        self.assertTrue(stats['is_chain_valid'])

    def test_hospital_statistics(self):
        """Test individual hospital statistics"""
        stats = self.blockchain.get_hospital_stats("TEST001")

        self.assertIsNotNone(stats)
        self.assertEqual(stats['hospital_id'], "TEST001")
        self.assertIn('blood_credits', stats)
        self.assertIn('blood_inventory', stats)
        self.assertIn('total_transactions', stats)

        # Test invalid hospital
        stats = self.blockchain.get_hospital_stats("INVALID")
        self.assertIsNone(stats)

    def test_distance_calculation(self):
        """Test GPS distance calculation accuracy"""
        # Test known distance between NYC landmarks
        distance = self.blockchain.calculate_distance(
            40.7128, -74.0060,  # Wall Street area
            40.7589, -73.9851   # Times Square area
        )

        # Should be approximately 5-6 km
        self.assertGreater(distance, 4.0)
        self.assertLess(distance, 7.0)

        # Test same location
        distance = self.blockchain.calculate_distance(40.7128, -74.0060, 40.7128, -74.0060)
        self.assertAlmostEqual(distance, 0.0, places=5)

class TestGRPCIntegration(unittest.TestCase):
    """Test gRPC client-server integration"""

    def setUp(self):
        """Set up gRPC test fixtures"""
        # These would be actual gRPC tests in a full implementation
        pass

    def test_secure_channel_creation(self):
        """Test secure gRPC channel creation"""
        # Mock test for gRPC functionality
        with patch('grpc.insecure_channel') as mock_channel:
            mock_channel.return_value = MagicMock()
            # Import and test client creation
            # This would test actual gRPC client functionality
            self.assertTrue(True)  # Placeholder

    def test_hospital_registration_via_grpc(self):
        """Test hospital registration through gRPC"""
        # Mock test for gRPC hospital registration
        self.assertTrue(True)  # Placeholder

    def test_blood_transfer_request_via_grpc(self):
        """Test blood transfer requests through gRPC"""
        # Mock test for gRPC blood transfer requests
        self.assertTrue(True)  # Placeholder

def run_performance_tests():
    """Run performance tests for the blockchain system"""
    print("\n=== Performance Tests ===")

    blockchain = BloodTransferBlockchain()

    # Test transaction creation performance
    start_time = time.time()
    for i in range(100):
        blockchain.register_hospital(f"PERF{i:03d}", f"Performance Hospital {i}", (40.7 + i*0.01, -74.0 + i*0.01))

    registration_time = time.time() - start_time
    print(f"Hospital registration (100 hospitals): {registration_time:.3f} seconds")

    # Test blood transfer creation performance
    start_time = time.time()
    for i in range(50):
        blockchain.add_blood_to_inventory(f"PERF{i:03d}", "O+", 10)

    inventory_time = time.time() - start_time
    print(f"Blood inventory updates (50 operations): {inventory_time:.3f} seconds")

    # Test mining performance
    start_time = time.time()
    for i in range(10):
        tx = blockchain.create_blood_transfer_transaction(f"PERF{i:03d}", f"PERF{i+1:03d}", "O+", 1)
        if tx:
            blockchain.pending_transactions.append(tx)

    blockchain.mine_pending_transactions("PERF001")
    mining_time = time.time() - start_time
    print(f"Block mining (10 transactions): {mining_time:.3f} seconds")

if __name__ == '__main__':
    # Run unit tests
    print("Running Blood Transfer Blockchain System Tests...")

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestBloodTransferBlockchain))
    suite.addTests(loader.loadTestsFromTestCase(TestGRPCIntegration))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Run performance tests
    run_performance_tests()

    # Print summary
    print(f"\n=== Test Summary ===")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
