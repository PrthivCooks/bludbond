
"""
gRPC Client implementation for hospital communication
This file should be saved as 'blood_transfer_grpc_client.py'
"""

import grpc
import ssl
import logging
from typing import Optional, Tuple
import time

# Import the request/response classes (normally from generated proto files)
class BloodTransferClient:
    """Client for communicating with other hospitals via gRPC"""

    def __init__(self, hospital_id: str, server_address: str = "localhost:50051", use_tls: bool = False):
        self.hospital_id = hospital_id
        self.server_address = server_address
        self.use_tls = use_tls
        self.logger = logging.getLogger(__name__)

    def create_channel(self):
        """Create gRPC channel with optional TLS"""
        if self.use_tls:
            credentials = grpc.ssl_channel_credentials()
            channel = grpc.secure_channel(self.server_address, credentials)
            self.logger.info(f"Created secure channel to {self.server_address}")
        else:
            channel = grpc.insecure_channel(self.server_address)
            self.logger.info(f"Created insecure channel to {self.server_address}")

        return channel

    def register_hospital(self, name: str, latitude: float, longitude: float, 
                         initial_credits: int = 100) -> Tuple[bool, str]:
        """Register this hospital with the network"""
        try:
            with self.create_channel() as channel:
                # In real implementation, would use:
                # stub = blood_transfer_pb2_grpc.BloodTransferServiceStub(channel)

                # Simulate request (normally would create proper protobuf message)
                self.logger.info(f"Registering hospital {self.hospital_id} with network")

                # Simulate successful registration
                message = f"Hospital {self.hospital_id} registered successfully"
                self.logger.info(message)
                return True, message

        except grpc.RpcError as e:
            self.logger.error(f"gRPC error during registration: {e}")
            return False, f"Registration failed: {e}"
        except Exception as e:
            self.logger.error(f"Unexpected error during registration: {e}")
            return False, f"Registration failed: {e}"

    def request_blood_transfer(self, receiver_id: str, blood_type: str, 
                             quantity: int, urgency_level: str = "normal") -> Tuple[bool, str, Optional[str]]:
        """Request blood transfer to another hospital"""
        try:
            with self.create_channel() as channel:
                # In real implementation, would use:
                # stub = blood_transfer_pb2_grpc.BloodTransferServiceStub(channel)

                self.logger.info(f"Requesting blood transfer: {quantity} units of {blood_type} to {receiver_id}")

                # Simulate request processing
                time.sleep(0.1)  # Simulate network delay

                # Simulate successful transfer request
                transaction_id = f"TXN_{int(time.time())}"
                message = f"Blood transfer request accepted. Transaction ID: {transaction_id}"
                self.logger.info(message)

                return True, message, transaction_id

        except grpc.RpcError as e:
            self.logger.error(f"gRPC error during blood transfer request: {e}")
            return False, f"Transfer request failed: {e}", None
        except Exception as e:
            self.logger.error(f"Unexpected error during transfer request: {e}")
            return False, f"Transfer request failed: {e}", None

    def verify_location_proximity(self, other_hospital_id: str) -> Tuple[bool, str]:
        """Verify if this hospital is within transfer range of another hospital"""
        try:
            with self.create_channel() as channel:
                # In real implementation, would use:
                # stub = blood_transfer_pb2_grpc.BloodTransferServiceStub(channel)

                self.logger.info(f"Verifying location proximity with {other_hospital_id}")

                # Simulate proximity check
                time.sleep(0.05)  # Simulate network delay

                # Simulate successful proximity verification
                message = f"Hospitals {self.hospital_id} and {other_hospital_id} are within acceptable distance"
                self.logger.info(message)

                return True, message

        except grpc.RpcError as e:
            self.logger.error(f"gRPC error during proximity verification: {e}")
            return False, f"Proximity verification failed: {e}"
        except Exception as e:
            self.logger.error(f"Unexpected error during proximity verification: {e}")
            return False, f"Proximity verification failed: {e}"

    def check_network_status(self) -> bool:
        """Check if the network is reachable"""
        try:
            with self.create_channel() as channel:
                # Attempt to create connection
                grpc.channel_ready_future(channel).result(timeout=5)
                self.logger.info("Network connection established successfully")
                return True
        except grpc.FutureTimeoutError:
            self.logger.error("Network connection timeout")
            return False
        except Exception as e:
            self.logger.error(f"Network connection failed: {e}")
            return False

# Example usage
def main():
    """Example usage of the gRPC client"""
    logging.basicConfig(level=logging.INFO)

    # Create client for a hospital
    client = BloodTransferClient("HOSP001", "localhost:50051", use_tls=False)

    # Check network connectivity
    if not client.check_network_status():
        print("Cannot connect to network. Please ensure the server is running.")
        return

    # Register the hospital
    success, message = client.register_hospital(
        name="City General Hospital",
        latitude=40.7128,
        longitude=-74.0060,
        initial_credits=150
    )
    print(f"Registration: {message}")

    if success:
        # Request a blood transfer
        success, message, tx_id = client.request_blood_transfer(
            receiver_id="HOSP002",
            blood_type="O+",
            quantity=2,
            urgency_level="urgent"
        )
        print(f"Transfer request: {message}")

        if success:
            print(f"Transaction ID: {tx_id}")

        # Verify location proximity
        success, message = client.verify_location_proximity("HOSP002")
        print(f"Proximity check: {message}")

if __name__ == '__main__':
    main()
