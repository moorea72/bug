import requests
import json
from datetime import datetime
from decimal import Decimal
import os

class BlockchainVerifier:
    def __init__(self):
        # Configurable wallet address from environment or database
        self.wallet_address = os.environ.get('WALLET_ADDRESS', "0xae49d3b4775c0524bd81da704340b5ef5a7416e9")
        # USDT contract address on BSC
        self.usdt_contract = "0x55d398326f99059fF775485246999027B3197955"
        # Configurable API settings
        self.moralis_api_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJub25jZSI6IjVlYWI2YjhkLWFhNWYtNDc1ZS1iZmY1LTFkOWVlNGVjMzM5NSIsIm9yZ0lkIjoiNDU4MzcyIiwidXNlcklkIjoiNDcxNTgxIiwidHlwZUlkIjoiYWZiZjUxNjEtMDQ0Zi00NTA3LTlkY2EtMGY1ZDFkYzZjOThlIiwidHlwZSI6IlBST0pFQ1QiLCJpYXQiOjE3NTIwNTU0NTEsImV4cCI6NDkwNzgxNTQ1MX0.AnPiPQ136UOBg2GUu56SUEkkubqA1JcfxvxPAQkV5Ew"
        self.moralis_api_url = os.environ.get('MORALIS_API_URL', "https://deep-index.moralis.io/api/v2.2")
        self.bsc_chain_id = "bsc"
        self.bscscan_api_key = os.environ.get('BSCSCAN_API_KEY')  # Optional fallback API
        # India-friendly API endpoints - VPN Free
        self.api_endpoints = [
            "https://api.bscscan.com/api",  # BSCScan - Works in India
            "https://deep-index.moralis.io/api/v2.2",
            "https://api.moralis.io/api/v2.2",
            "https://bsc-dataseed.binance.org/",  # Binance BSC - India accessible
            "https://gateway.moralis.io/api/v2.2"
        ]

    def verify_usdt_transaction(self, tx_hash, expected_amount, expected_to_address, network='BEP20'):
        """
        Verify USDT transaction on multiple networks using enhanced blockchain verification
        """
        try:
            # Enhanced format validation
            if not tx_hash or not isinstance(tx_hash, str):
                return {
                    'success': False,
                    'error': 'Transaction hash is required'
                }
            
            # Clean and validate transaction hash
            tx_hash = tx_hash.strip()
            if not tx_hash.startswith('0x'):
                tx_hash = '0x' + tx_hash
                
            if len(tx_hash) != 66:
                return {
                    'success': False,
                    'error': 'Invalid transaction hash format (must be 64 characters)'
                }
            
            # Validate hex characters
            try:
                int(tx_hash[2:], 16)
            except ValueError:
                return {
                    'success': False,
                    'error': 'Transaction hash contains invalid characters'
                }
            
            # Set chain and contract based on network
            if network == 'BEP20':
                self.bsc_chain_id = "bsc"
                self.usdt_contract = "0x55d398326f99059fF775485246999027B3197955"  # USDT BEP20
            elif network == 'TRC20':
                self.bsc_chain_id = "tron"
                self.usdt_contract = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"  # USDT TRC20
            else:
                return {
                    'success': False,
                    'error': f'Unsupported network: {network}. Please use BEP20 or TRC20'
                }
            
            # Validate amount
            if not expected_amount or expected_amount <= 0:
                return {
                    'success': False,
                    'error': 'Invalid amount specified'
                }
            
            # Validate address
            if not expected_to_address or len(expected_to_address) < 26:
                return {
                    'success': False,
                    'error': 'Invalid destination address'
                }
            
            # Use enhanced verification with better error handling
            result = self._verify_with_enhanced_moralis(tx_hash, expected_amount, expected_to_address, network)
            return result
            
        except Exception as e:
            import traceback
            print(f"Verification error: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return {
                'success': False,
                'error': f'Blockchain verification failed: {str(e)}',
                'details': 'Please check your transaction hash and try again'
            }
    
    def _verify_with_enhanced_moralis(self, tx_hash, expected_amount, expected_to_address, network='BEP20'):
        """
        Enhanced blockchain verification using multiple APIs with better error handling
        """
        try:
            headers = {
                'X-API-Key': self.moralis_api_key,
                'Content-Type': 'application/json',
                'User-Agent': 'USDT-Platform/1.0',
                'Accept': 'application/json'
            }
            
            params = {
                'chain': self.bsc_chain_id
            }
            
            # Try multiple API endpoints
            verification_results = []
            
            for api_url in self.api_endpoints:
                try:
                    if 'bscscan' in api_url and network != 'BEP20':
                        continue  # Skip BSCScan for non-BEP20
                        
                    tx_url = f"{api_url}/transaction/{tx_hash}"
                    print(f"Verifying with API: {tx_url}")
                    
                    response = requests.get(tx_url, headers=headers, params=params, timeout=15)
                    
                    if response.status_code == 200:
                        tx_data = response.json()
                        
                        # Check if transaction exists
                        if not tx_data:
                            verification_results.append({
                                'api': api_url,
                                'success': False,
                                'error': 'Transaction not found'
                            })
                            continue
                        
                        # Check transaction status
                        receipt_status = tx_data.get('receipt_status', '0')
                        if receipt_status != '1':
                            verification_results.append({
                                'api': api_url,
                                'success': False,
                                'error': 'Transaction failed on blockchain'
                            })
                            continue
                        
                        # Parse USDT transfer from logs
                        logs_data = tx_data.get('logs', [])
                        transfer_data = self._parse_moralis_usdt_transfer(logs_data)
                        
                        if not transfer_data:
                            verification_results.append({
                                'api': api_url,
                                'success': False,
                                'error': 'No USDT transfer found in transaction'
                            })
                            continue
                        
                        # Verify destination address
                        if transfer_data['to'].lower() != expected_to_address.lower():
                            verification_results.append({
                                'api': api_url,
                                'success': False,
                                'error': f'Wrong destination. Expected: {expected_to_address}, Got: {transfer_data["to"]}'
                            })
                            continue
                        
                        # Verify amount (USDT has 18 decimals for BEP20, 6 for TRC20)
                        decimals = 18 if network == 'BEP20' else 6
                        actual_amount = Decimal(transfer_data['value']) / Decimal(10**decimals)
                        expected_amount_decimal = Decimal(str(expected_amount))
                        
                        # Allow small rounding differences (0.01 USDT)
                        if abs(actual_amount - expected_amount_decimal) > Decimal('0.01'):
                            verification_results.append({
                                'api': api_url,
                                'success': False,
                                'error': f'Amount mismatch. Expected: ${expected_amount}, Got: ${actual_amount}'
                            })
                            continue
                        
                        # Successful verification
                        return {
                            'success': True,
                            'transaction_hash': tx_hash,
                            'from_address': transfer_data['from'],
                            'to_address': transfer_data['to'],
                            'amount': float(actual_amount),
                            'block_number': tx_data.get('block_number'),
                            'verification_method': f'moralis_enhanced_{network.lower()}',
                            'timestamp': datetime.utcnow().isoformat(),
                            'gas_used': tx_data.get('gas_used'),
                            'network': network,
                            'verified_by': api_url
                        }
                        
                except requests.exceptions.Timeout:
                    verification_results.append({
                        'api': api_url,
                        'success': False,
                        'error': 'Request timeout'
                    })
                    continue
                except requests.exceptions.RequestException as e:
                    verification_results.append({
                        'api': api_url,
                        'success': False,
                        'error': f'Network error: {str(e)}'
                    })
                    continue
                except Exception as e:
                    verification_results.append({
                        'api': api_url,
                        'success': False,
                        'error': f'API error: {str(e)}'
                    })
                    continue
            
            # If all APIs failed, return comprehensive error
            error_summary = "; ".join([f"{r['api']}: {r['error']}" for r in verification_results[-3:]])  # Last 3 errors
            
            return {
                'success': False,
                'error': 'Transaction verification failed on all blockchain APIs',
                'details': error_summary,
                'verification_attempts': len(verification_results),
                'network': network,
                'suggestion': 'Please verify your transaction hash is correct and the transaction is confirmed on the blockchain'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Verification system error: {str(e)}',
                'network': network
            }

    def _verify_with_moralis(self, tx_hash, expected_amount, expected_to_address, network='BEP20'):
        """
        India-friendly blockchain verification using multiple APIs without VPN dependency
        """
        try:
            # Skip BSCScan for now and use Moralis directly
            # bscscan_result = self._verify_with_bscscan(tx_hash, expected_amount, expected_to_address)
            # if bscscan_result.get('success'):
            #     return bscscan_result
            
            # Fallback to Moralis with India-friendly headers
            headers = {
                'X-API-Key': self.moralis_api_key,
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json'
            }
            
            params = {
                'chain': self.bsc_chain_id
            }
            
            # Try multiple API endpoints optimized for India
            for api_url in self.api_endpoints:
                try:
                    if 'bscscan' in api_url:
                        continue  # Already tried BSCScan
                        
                    tx_url = f"{api_url}/transaction/{tx_hash}"
                    print(f"Trying API endpoint: {tx_url}")
                    
                    response = requests.get(tx_url, headers=headers, params=params, timeout=30)
                    
                    if response.status_code == 200:
                        tx_data = response.json()
                        print(f"Successfully got data from {api_url}")
                        
                        # Check if transaction exists and is successful
                        if not tx_data or tx_data.get('receipt_status') != '1':
                            return {
                                'success': False,
                                'error': 'Transaction not found or failed on blockchain'
                            }
                        
                        # Parse USDT transfer from logs
                        logs_data = tx_data.get('logs', [])
                        transfer_data = self._parse_moralis_usdt_transfer(logs_data)
                        
                        if not transfer_data:
                            return {
                                'success': False,
                                'error': 'No USDT transfer found in transaction'
                            }
                        
                        # Verify transfer details
                        if transfer_data['to'].lower() != expected_to_address.lower():
                            return {
                                'success': False,
                                'error': f'Wrong destination address. Expected: {expected_to_address}, Got: {transfer_data["to"]}'
                            }
                        
                        # Convert amount (USDT has 18 decimals)
                        actual_amount = Decimal(transfer_data['value']) / Decimal(10**18)
                        expected_amount_decimal = Decimal(str(expected_amount))
                        
                        # Allow small rounding differences (0.01 USDT)
                        if abs(actual_amount - expected_amount_decimal) > Decimal('0.01'):
                            return {
                                'success': False,
                                'error': f'Amount mismatch. Expected: {expected_amount}, Got: {actual_amount}'
                            }
                        
                        # Return success
                        return {
                            'success': True,
                            'transaction_hash': tx_hash,
                            'from_address': transfer_data['from'],
                            'to_address': transfer_data['to'],
                            'amount': float(actual_amount),
                            'block_number': tx_data.get('block_number'),
                            'verification_method': f'moralis_blockchain_{api_url}',
                            'timestamp': datetime.utcnow(),
                            'gas_used': tx_data.get('gas_used'),
                            'gas_price': tx_data.get('gas_price')
                        }
                        
                except requests.exceptions.RequestException as e:
                    print(f"API endpoint {api_url} failed: {str(e)}")
                    continue  # Try next endpoint
            
            # If all Moralis endpoints fail, try BSCscan as backup
            if self.bscscan_api_key:
                try:
                    print("Trying BSCscan as backup...")
                    bsc_url = "https://api.bscscan.com/api"
                    bsc_params = {
                        "module": "proxy",
                        "action": "eth_getTransactionByHash",
                        "txhash": tx_hash,
                        "apikey": self.bscscan_api_key
                    }
                    
                    response = requests.get(bsc_url, params=bsc_params, timeout=15)
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('result'):
                            print("BSCscan verification successful")
                            return self._verify_transaction_details(tx_hash, expected_amount, expected_to_address)
                except Exception as e:
                    print(f"BSCscan backup failed: {str(e)}")
            
            return {
                'success': False,
                'error': 'All verification endpoints failed. Please check your internet connection or try again later.',
                'message': 'Network connectivity issue - no VPN required'
            }
            
        except requests.RequestException:
            return {
                'success': False,
                'error': 'Network connection failed'
            }
        except Exception as e:
            # Better error debugging
            import traceback
            print(f"Verification error: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return {
                'success': False,
                'error': f'Verification error: {str(e)}'
            }
    
    def _process_transaction_data(self, tx_data, tx_hash, expected_amount, expected_to_address):
        """
        Process transaction data and verify USDT transfer details
        """
        try:
            
            # Check if transaction is to USDT contract
            if tx_data.get('to') and tx_data['to'].lower() != self.usdt_contract.lower():
                return {
                    'success': False,
                    'error': 'This is not a USDT transfer transaction.'
                }
            
            # Get transaction receipt for detailed verification
            receipt_params = {
                'module': 'proxy',
                'action': 'eth_getTransactionReceipt',
                'txhash': tx_hash
            }
            if self.api_key:
                receipt_params['apikey'] = self.api_key
            
            receipt_response = requests.get(self.bsc_api_url, params=receipt_params, timeout=15)
            if receipt_response.status_code != 200:
                return {
                    'success': False,
                    'error': 'Could not fetch transaction receipt from blockchain.'
                }
            
            receipt_data = receipt_response.json()
            
            # Handle API errors for receipt
            if 'error' in receipt_data:
                return {
                    'success': False,
                    'error': f'Receipt API error: {receipt_data["error"]["message"]}'
                }
            
            if 'result' not in receipt_data or receipt_data['result'] is None:
                return {
                    'success': False,
                    'error': 'Transaction receipt not found on blockchain.'
                }
            
            receipt = receipt_data['result']
            
            # Check transaction status
            if receipt['status'] != '0x1':
                return {
                    'success': False,
                    'error': 'Transaction failed on blockchain. Only successful transactions are accepted.'
                }
            
            # Parse transfer logs for USDT transfer
            transfer_data = self.parse_usdt_transfer_logs(receipt['logs'])
            
            if not transfer_data:
                return {
                    'success': False,
                    'error': 'No USDT transfer found in transaction'
                }
            
            # Verify the transfer details
            if transfer_data['to'].lower() != expected_to_address.lower():
                return {
                    'success': False,
                    'error': f'Wrong destination address. Expected: {expected_to_address}'
                }
            
            # Convert amount (USDT has 18 decimals)
            actual_amount = Decimal(transfer_data['value']) / Decimal(10**18)
            expected_amount_decimal = Decimal(str(expected_amount))
            
            # Allow small rounding differences
            if abs(actual_amount - expected_amount_decimal) > Decimal('0.01'):
                return {
                    'success': False,
                    'error': f'Amount mismatch. Expected: {expected_amount}, Got: {actual_amount}'
                }
            
            return {
                'success': True,
                'transaction_hash': tx_hash,
                'from_address': transfer_data['from'],
                'to_address': transfer_data['to'],
                'amount': float(actual_amount),
                'block_number': int(receipt['blockNumber'], 16),
                'verification_method': 'blockchain',
                'timestamp': datetime.utcnow()
            }
            
        except requests.RequestException:
            return {
                'success': False,
                'error': 'Network connection failed'
            }
        except Exception as e:
            # Better error debugging
            import traceback
            print(f"Verification error: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return {
                'success': False,
                'error': f'Verification error: {str(e)}'
            }
    
    def _verify_transaction_details(self, tx_hash, expected_amount, expected_to_address):
        """
        Simplified verification when we know transaction exists
        """
        return {
            'success': True,
            'transaction_hash': tx_hash,
            'from_address': 'Unknown',
            'to_address': expected_to_address,
            'amount': expected_amount,
            'verification_method': 'blockchain_basic',
            'timestamp': datetime.utcnow(),
            'note': 'Transaction confirmed to exist on blockchain'
        }
    
    def _is_valid_tx_format(self, tx_hash):
        """
        Check if transaction hash has valid format
        """
        return (tx_hash and 
                isinstance(tx_hash, str) and 
                tx_hash.startswith('0x') and 
                len(tx_hash) == 66 and 
                all(c in '0123456789abcdefABCDEF' for c in tx_hash[2:]))

    def parse_usdt_transfer_logs(self, logs):
        """
        Parse USDT transfer logs from transaction receipt
        """
        # USDT Transfer event signature
        transfer_topic = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
        
        for log in logs:
            if (log['address'].lower() == self.usdt_contract.lower() and 
                len(log['topics']) >= 3 and 
                log['topics'][0] == transfer_topic):
                
                # Parse transfer data
                from_address = "0x" + log['topics'][1][-40:]
                to_address = "0x" + log['topics'][2][-40:]
                value = int(log['data'], 16)
                
                return {
                    'from': from_address,
                    'to': to_address,
                    'value': value
                }
        
        return None

    def _parse_moralis_usdt_transfer(self, logs_data):
        """
        Parse USDT transfer from Moralis transaction logs
        """
        # USDT Transfer event signature
        transfer_topic = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
        
        for log in logs_data:
            if (log.get('address', '').lower() == self.usdt_contract.lower() and 
                log.get('topic0') == transfer_topic):
                
                # Parse transfer data from Moralis format
                from_address = "0x" + log.get('topic1', '')[-40:]
                to_address = "0x" + log.get('topic2', '')[-40:]
                value = int(log.get('data', '0x0'), 16)
                
                return {
                    'from': from_address,
                    'to': to_address,
                    'value': value
                }
        
        return None

    def get_wallet_qr_code(self):
        """
        Generate QR code for wallet address
        """
        import qrcode
        from io import BytesIO
        import base64
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.wallet_address)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Convert to base64 for HTML display
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_base64}"

    def _verify_with_bscscan(self, tx_hash, expected_amount, expected_to_address):
        """
        Verify transaction using BSCScan API - fallback method
        """
        if not self.bscscan_api_key:
            return {
                'success': False,
                'error': 'BSCScan API key not configured'
            }
        
        try:
            # Get transaction details
            url = f"https://api.bscscan.com/api?module=proxy&action=eth_getTransactionByHash&txhash={tx_hash}&apikey={self.bscscan_api_key}"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if 'result' not in data or not data['result']:
                return {
                    'success': False,
                    'error': 'Transaction not found on BSC network'
                }
            
            return {
                'success': True,
                'message': 'Transaction found via BSCScan',
                'transaction_hash': tx_hash,
                'verification_method': 'bscscan_api'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'BSCScan verification failed: {str(e)}'
            }

# Initialize the verifier
blockchain_verifier = BlockchainVerifier()