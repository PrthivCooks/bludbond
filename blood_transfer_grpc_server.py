
"""
gRPC Server implementation for secure hospital-to-hospital communication
This file should be saved as 'blood_transfer_grpc_server.py'
"""

import grpc
from concurrent import futures
import time
import ssl
import logging
from typing import Dict, Any
import json

# Import the blockchain system
from blood_transfer_blockchain import BloodTransferBlockchain

# Proto definitions (would normally be generated from .proto file)
class BloodTransferRequest:
    def __init__(self, sender_id, receiver_id, blood_type, quantity, urgency_level):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.blood_type = blood_type
        self.quantity = quantity
        self.urgency_level = urgency_level

class BloodTransferResponse:
    def __init__(self, success, message, transaction_id=None, distance_km=0):
        self.success = success
        self.message = message
        self.transaction_id = transaction_id
        self.distance_km = distance_km

class HospitalRegistrationRequest:
    def __init__(self, hospital_id, name, latitude, longitude, initial_credits):
        self.hospital_id = hospital_id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.initial_credits = initial_credits

class HospitalRegistrationResponse:
    def __init__(self, success, message):
        self.success = success
        self.message = message

class BloodTransferService:
    """gRPC service for blood transfer operations"""

    def __init__(self):
        self.blockchain = BloodTransferBlockchain()
        self.logger = logging.getLogger(__name__)

    def RegisterHospital(self, request, context):
        """Register a new hospital in the network"""
        try:
            success = self.blockchain.register_hospital(
                request.hospital_id,
                request.name,
                (request.latitude, request.longitude),
                request.initial_credits
            )

            if success:
                message = f"Hospital {request.hospital_id} registered successfully"
                self.logger.info(message)
                return HospitalRegistrationResponse(True, message)
            else:
                message = f"Failed to register hospital {request.hospital_id} - may already exist"
                self.logger.warning(message)
                return HospitalRegistrationResponse(False, message)

        except Exception as e:
            self.logger.error(f"Error registering hospital: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return HospitalRegistrationResponse(False, f"Internal error: {str(e)}")

    def RequestBloodTransfer(self, request, context):
        """Handle blood transfer requests between hospitals"""
        try:
            # Authenticate the requesting hospital (would check certificates in production)
            requesting_hospital = context.peer()
            self.logger.info(f"Blood transfer request from {requesting_hospital}")

            # Create the blood transfer transaction
            transaction = self.blockchain.create_blood_transfer_transaction(
                request.sender_id,
                request.receiver_id,
                request.blood_type,
                request.quantity,
                request.urgency_level
            )

            if transaction:
                # Add to pending transactions
                self.blockchain.pending_transactions.append(transaction)

                message = f"Blood transfer request accepted. Transaction ID: {transaction['transaction_id']}"
                self.logger.info(message)

                return BloodTransferResponse(
                    True, 
                    message, 
                    transaction['transaction_id'],
                    transaction['distance_km']
                )
            else:
                message = "Blood transfer request denied - check requirements"
                self.logger.warning(message)
                return BloodTransferResponse(False, message)

        except Exception as e:
            self.logger.error(f"Error processing blood transfer: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return BloodTransferResponse(False, f"Internal error: {str(e)}")

    def VerifyLocationProximity(self, request, context):
        """Verify if two hospitals are within acceptable distance"""
        try:
            is_valid = self.blockchain.verify_location_proximity(
                request.sender_id, 
                request.receiver_id
            )

            if is_valid:
                return BloodTransferResponse(True, "Hospitals are within acceptable distance")
            else:
                return BloodTransferResponse(False, "Hospitals are too far apart")

        except Exception as e:
            self.logger.error(f"Error verifying location: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return BloodTransferResponse(False, f"Internal error: {str(e)}")

def create_secure_server(port=50051, private_key_path=None, certificate_path=None):
    """Create a secure gRPC server with TLS"""

    # Create the gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # Add the blood transfer service
    service = BloodTransferService()
    # In real implementation, would use generated proto files:
    # blood_transfer_pb2_grpc.add_BloodTransferServiceServicer_to_server(service, server)

    # Configure TLS (if certificates provided)
    if private_key_path and certificate_path:
        with open(private_key_path, 'rb') as f:
            private_key = f.read()
        with open(certificate_path, 'rb') as f:
            certificate = f.read()

        credentials = grpc.ssl_server_credentials(
            [(private_key, certificate)],
            root_certificates=None,
            require_client_auth=False
        )
        server.add_secure_port(f'[::]:{port}', credentials)
        print(f"Secure gRPC server starting on port {port} with TLS")
    else:
        # For development - insecure connection
        server.add_insecure_port(f'[::]:{port}')
        print(f"gRPC server starting on port {port} (INSECURE - for development only)")

    return server, service

def main():
    """Main server function"""
    logging.basicConfig(level=logging.INFO)

    server, service = create_secure_server()

    try:
        server.start()
        print("Blood Transfer gRPC Server is running...")
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Shutting down server...")
        server.stop(0)

if __name__ == '__main__':
    main()
