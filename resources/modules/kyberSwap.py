import sys
import os
import json
import time
import logging
import requests
import questionary
from customtkinter import CTk, CTkTextbox, CTkButton, CTkLabel, CTkFrame
from web3 import Web3
from rich.console import Console
from rich.logging import RichHandler
from eth_account import Account
from web3.exceptions import ABIFunctionNotFound, ContractLogicError
from eth_account.messages import encode_structured_data
import platform

import config  # Make sure your config.py is in the same directory or PYTHONPATH

console = Console()

class SwapManager:
    def __init__(self, chain_config, KYBERSWAP_API_HEADERS=config.KYBERSWAP_API_HEADERS):
        """
        Initialize the SwapManager with a specific chain configuration object.
        """
        self.console = Console()
        self.KYBERSWAP_API_HEADERS = KYBERSWAP_API_HEADERS

        # Store the chain config (Polygon, OP, Base, etc.)
        self.chain_config = chain_config

        # Extract commonly used fields
        self.rpc_url = chain_config.ALCHEMY_RPC_URL
        self.wallet_file = chain_config.WALLET_FILE
        self.contracts_file = chain_config.TOKENS_KYBER_FILE
        self.INFURA_GAS_API_URL = chain_config.INFURA_GAS_API_URL
        self.native_token = chain_config.NATIVE_TOKEN

        # Some chain configs have CHAIN_ID as string, ensure integer
        self.chain_id = int(chain_config.CHAIN_ID)
        self.chain_name = chain_config.CHAIN_NAME

        # Web3 provider
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))

        # Logging
        logging.basicConfig(level=logging.INFO, handlers=[RichHandler(console=self.console)])
        self.logger = logging.getLogger(__name__)

        self.is_ubunto = platform.system() == 'linux' in platform.version

        # Lists to store loaded wallets
        self.wallet_addresses = []
        self.wallet_private_keys = []

        self.create_placeholder_file(self.wallet_file, 'wallets')
        self.create_placeholder_file(self.contracts_file, 'contracts')
        # Load token contracts
        self.tokens = self.load_contracts()

        # Use the chain-specific KyberSwap endpoints from config
        self.kyberswap_api_route = chain_config.KYBERSWAP_API_ROUTE
        self.kyberswap_api_build = chain_config.KYBERSWAP_API_BUILD
        self.kyberswap_api_encode = chain_config.KYBERSWAP_API_ENCODE

    def load_contracts(self):
        """Load token contract addresses and symbols from the contracts file."""
        tokens = {}
        try:
            with open(self.contracts_file, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        address = self.w3.to_checksum_address(parts[0])
                        symbol = parts[1].upper()
                        tokens[f"{symbol} ({address})"] = address
                        self.console.log(f"[bold blue]Loaded token:[/bold blue] {symbol} ({address})")
            self.console.log("[bold green]Loaded token contracts successfully.[/bold green]")
        except Exception as e:
            self.console.log(f"[bold red]Error loading contracts file: {e}[/bold red]")
            sys.exit(1)
        return tokens

    def create_placeholder_file(self, file_path, content_type):
        """Create a placeholder file if it doesn't exist."""
        placeholder_content = {
            'wallets': "# Enter your private keys here, one per line\n",
            'contracts': "# Enter token contract addresses and symbols (e.g., 0x... SYMBOL)\n"
        }
        content = placeholder_content.get(content_type, "")
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.console.log(f"[bold green]Created placeholder file at {file_path}[/bold green]")

    def load_wallets_from_file(self):
        try:
            with open(self.wallet_file, 'r', encoding='utf-8') as f:
                for line in f:
                    private_key = line.strip()
                    if private_key:
                        # Validate private key
                        original_pk = private_key
                        if private_key.startswith(('0x', '0X')):
                            private_key = private_key[2:]
                        if len(private_key) != 64 or not all(c in '0123456789abcdefABCDEF' for c in private_key):
                            self.console.log(f"[bold red]Invalid private key format skipped: {original_pk}[/bold red]")
                            continue
                        self.wallet_private_keys.append(private_key)
                        try:
                            account = Account.from_key(private_key)
                            address = account.address
                            self.wallet_addresses.append(address)
                            self.console.log(f"[bold green]Loaded wallet address: {address}[/bold green]")
                        except Exception as e:
                            self.console.log(f"[bold red]Failed to derive address from private key {original_pk}: {e}[/bold red]")
            self.console.log("[bold green]All wallet addresses loaded successfully from file![/bold green]")
        except FileNotFoundError:
            self.console.log(f"[bold red]Error:[/bold red] The file '{self.wallet_file}' was not found.")
            sys.exit(1)
        except Exception as e:
            self.console.log(f"[bold red]Error loading wallets from file: {e}[/bold red]")
            sys.exit(1)

    def load_private_keys_from_file(self):
        """Load private keys from the default wallet file."""
        try:
            with open(self.wallet_file, 'r', encoding='utf-8') as f:
                self.wallet_private_keys = []
                for line in f:
                    private_key = line.strip()
                    if private_key:
                        self.console.log(f"[yellow]Original key: {private_key}[/yellow]")
                        # Remove 0x
                        if private_key.startswith(('0x', '0X')):
                            private_key = private_key[2:]
                        # Validate
                        if len(private_key) != 64:
                            self.console.log(f"[bold red]Invalid private key length: {len(private_key)} chars[/bold red]")
                            continue
                        if not all(c in '0123456789abcdefABCDEF' for c in private_key):
                            self.console.log(f"[bold red]Invalid hex characters in key[/bold red]")
                            continue

                        self.console.log(f"[green]Valid key added: {private_key[:8]}...[/green]")
                        self.wallet_private_keys.append(private_key)
            self.console.log(f"[bold blue]Total valid keys loaded: {len(self.wallet_private_keys)}[/bold blue]")
        except Exception as e:
            self.console.log(f"[bold red]Error loading private keys from file: {e}[/bold red]")
            sys.exit(1)

    def load_private_keys_from_gui(self):
        """Load private keys manually via a GUI."""
        keys = []

        def add_keys():
            input_keys = entry.get("1.0", "end").strip()
            keys.extend(input_keys.splitlines())
            root.destroy()

        root = CTk()
        root.title("Enter Private Keys")

        frame = CTkFrame(root)
        frame.pack(pady=20, padx=20)

        label = CTkLabel(frame, text="Enter your private keys (one per line):", font=("Arial", 14))
        label.pack(pady=5)

        entry = CTkTextbox(frame, width=300, height=150)
        entry.pack(pady=10)

        add_button = CTkButton(frame, text="Add Private Keys", command=add_keys)
        add_button.pack(pady=5)

        close_button = CTkButton(frame, text="Close", command=root.destroy)
        close_button.pack(pady=5)

        root.mainloop()

        self.wallet_private_keys = [key.strip() for key in keys if key.strip()]
        # Derive addresses
        for private_key in self.wallet_private_keys:
            try:
                account = Account.from_key(private_key)
                address = account.address
                self.wallet_addresses.append(address)
                self.console.log(f"[bold green]Loaded wallet address: {address}[/bold green]")
            except Exception as e:
                self.console.log(f"[bold red]Failed to derive address from private key: {e}[/bold red]")

        self.console.log(f"[bold green]Loaded {len(self.wallet_private_keys)} private keys manually from GUI[/bold green]")

    def load_private_keys_from_cli(self):
        """Load private keys manually via CLI on Ubuntu."""
        keys = []
        print("Enter your private keys (one per line). Type 'done' when finished:")

        while True:
            key = input("Private key: ").strip()
            if key.lower() == 'done':
                break
            if key:
                keys.append(key)
        
        self.wallet_private_keys = keys
        # Derive addresses from private keys
        for private_key in self.wallet_private_keys:
            try:
                account = Account.from_key(private_key)
                address = account.address
                self.wallet_addresses.append(address)
                self.console.log(f"[bold green]Loaded wallet address: {address}[/bold green]")
            except Exception as e:
                self.console.log(f"[bold red]Failed to derive address from private key: {e}[/bold red]")

        self.console.log(f"[bold green]Loaded {len(self.wallet_private_keys)} private keys from CLI[/bold green]")

    def select_private_key_input_method(self):
        if self.is_ubuntu:
            choice = questionary.select(
                "Choose private key input method:",
                choices=["Default Path (File)", "Manual Input (CLI)"]
            ).ask()
            if choice == "Default Path (File)" :
                self.load_private_keys_from_file
            if choice == "Manual Input (CLI)" :
                self.load_private_keys_from_cli()
        else:
            choice = questionary.select(
                "Choose private key input method:",
                choices=["Default Path (File)", "Manual Input (GUI)"]
            ).ask()

            if choice == "Default Path (File)":
                self.load_private_keys_from_file()
            elif choice == "Manual Input (GUI)":
                self.load_private_keys_from_gui()

    def check_token_balance(self, token_address, account_address):
        """Check the balance of a specific token for a given account."""
        try:
            if token_address == '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE':
                if self.chain_name == "ethereum":
                    balance = self.w3.eth.get_balance(account_address)
                    decimals = 18 
                    human_readable_balance = balance / (10 ** decimals)
                    return balance , human_readable_balance , decimals
                # For native token, check balance using self.native_token
                abi = json.loads(self.chain_config.TOKEN_ABI)
                token_contract = self.w3.eth.contract(address=self.native_token, abi=abi)
                balance = token_contract.functions.balanceOf(account_address).call()
                decimals = token_contract.functions.decimals().call()
                human_readable_balance = balance / (10 ** decimals)
                return balance, human_readable_balance, decimals
            else:
                # For other tokens, use contract calls
                abi = json.loads(self.chain_config.TOKEN_ABI)
                token_contract = self.w3.eth.contract(address=token_address, abi=abi)
                balance = token_contract.functions.balanceOf(account_address).call()
                decimals = token_contract.functions.decimals().call()
                human_readable_balance = balance / (10 ** decimals)
                return balance, human_readable_balance, decimals
        except json.JSONDecodeError as e:
            self.console.log(f"[bold red]Error parsing TOKEN_ABI: {str(e)}[/bold red]")
            self.console.log(f"[yellow]ABI content: {self.chain_config.TOKEN_ABI}[/yellow]")
            raise
        except Exception as e:
            self.console.log(f"[bold red]Error in check_token_balance: {str(e)}[/bold red]")
            raise

    def fetch_suggested_fees(self):
        """Fetch suggested gas fees from the Infura or another Gas API."""
        api_url = self.INFURA_GAS_API_URL

        try:
            response = requests.get(api_url)
            response.raise_for_status()
            gas_data = response.json()

            # Prompt user for gas tier
            tier = questionary.select(
                "Select gas tier to use:",
                choices=["low", "medium", "high"]
            ).ask().lower()

            max_fee_per_gas = float(gas_data[tier]['suggestedMaxFeePerGas'])
            max_priority_fee_per_gas = float(gas_data[tier]['suggestedMaxPriorityFeePerGas'])

            max_fee_per_gas_wei = Web3.to_wei(max_fee_per_gas, 'gwei')
            max_priority_fee_per_gas_wei = Web3.to_wei(max_priority_fee_per_gas, 'gwei')

            self.console.log(
                f"[bold yellow]Fetched gas fees - Max Fee Per Gas:[/bold yellow] {max_fee_per_gas} Gwei, "
                f"[bold yellow]Max Priority Fee Per Gas:[/bold yellow] {max_priority_fee_per_gas} Gwei"
            )

            return max_fee_per_gas_wei, max_priority_fee_per_gas_wei

        except requests.exceptions.HTTPError as http_err:
            self.logger.error(f"HTTP error occurred while fetching gas fees: {http_err}")
        except Exception as err:
            self.logger.error(f"An error occurred while fetching gas fees: {err}")

        return None, None

    def send_approval_transaction(self, private_key, token_address, spender, amount, max_fee_per_gas, max_priority_fee_per_gas):
        """Approve the KyberSwap router (spender) to spend the specified token."""
        try:
            account = Account.from_key(private_key)
            abi = json.loads(self.chain_config.TOKEN_ABI)
            token_contract = self.w3.eth.contract(address=token_address, abi=abi)

            approval_choice = questionary.select(
                "Do you want to approve the exact amount or unlimited amount?",
                choices=["Exact amount", "Unlimited amount"]
            ).ask()

            if approval_choice == "Exact amount":
                approval_amount = int(amount + 1)
            else:
                approval_amount = 2**256 - 1

            tx = token_contract.functions.approve(
                spender,
                approval_amount
            ).build_transaction({
                'chainId': self.chain_id,
                'from': account.address,
                'nonce': self.w3.eth.get_transaction_count(account.address),
                'maxFeePerGas': max_fee_per_gas,
                'maxPriorityFeePerGas': max_priority_fee_per_gas,
                'gas': 100000,  # Adjust as needed
                'type': 2
            })

            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            self.console.log(f"[green]Approval transaction sent: {tx_hash.hex()}[/green]")

            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            if receipt['status'] == 1:
                self.console.log("[bold green]Approval transaction confirmed successfully![/bold green]")
            else:
                self.console.log("[bold red]Approval transaction failed![/bold red]")

        except Exception as e:
            self.console.log(f"[bold red]Error in send_approval_transaction: {e}[/bold red]")
            raise

    def check_eip2612_support(self, token_address, owner_address):
        """Check if the token supports EIP-2612 permit (permit(), nonces, DOMAIN_SEPARATOR)."""
        self.console.log("[yellow]Checking EIP-2612 support...[/yellow]")
        try:
            # Some chains might not define MINIMAL_ABI_PERMIT
            if not hasattr(self.chain_config, 'MINIMAL_ABI_PERMIT'):
                self.console.log("[red]✗ This chain config does not have MINIMAL_ABI_PERMIT defined[/red]")
                return False

            minimal_abi = json.loads(self.chain_config.MINIMAL_ABI_PERMIT)
            token_contract = self.w3.eth.contract(
                address=self.w3.to_checksum_address(token_address),
                abi=minimal_abi
            )

            # Check permit()
            try:
                token_contract.get_function_by_name('permit')
                self.console.log("[green]✓ Found permit function[/green]")
            except ABIFunctionNotFound:
                self.console.log("[red]✗ No permit function found[/red]")
                return False

            # Check nonces
            try:
                nonce_function = token_contract.get_function_by_signature('nonces(address)')
                _ = nonce_function(owner_address).call()
                self.console.log("[green]✓ Found nonces(address) function[/green]")
            except (ValueError, ABIFunctionNotFound, ContractLogicError):
                try:
                    nonce_function = token_contract.get_function_by_signature('nonces()')
                    _ = nonce_function().call()
                    self.console.log("[green]✓ Found nonces() function[/green]")
                except (ValueError, ABIFunctionNotFound, ContractLogicError):
                    self.console.log("[red]✗ No working nonces function found[/red]")
                    return False

            # Check DOMAIN_SEPARATOR
            try:
                token_contract.functions.DOMAIN_SEPARATOR().call()
                self.console.log("[green]✓ Found DOMAIN_SEPARATOR[/green]")
            except (ABIFunctionNotFound, ContractLogicError):
                self.console.log("[red]✗ No DOMAIN_SEPARATOR found[/red]")
                return False

            self.console.log("[bold green]Token fully supports EIP-2612![/bold green]")
            return True

        except Exception as e:
            self.console.log(f"[bold red]Error checking EIP-2612 support: {str(e)}[/bold red]")
            return False

    def get_permit_data(self, token_address, owner, spender, value, deadline, private_key):
        """Generate permit data for EIP-2612 approval."""
        try:
            # Some chains might not define ERC20_PERMIT_ABI
            if not hasattr(self.chain_config, 'ERC20_PERMIT_ABI'):
                self.console.log("[red]✗ This chain config does not have ERC20_PERMIT_ABI defined[/red]")
                return None

            erc20_abi = json.loads(self.chain_config.ERC20_PERMIT_ABI)
            token_contract = self.w3.eth.contract(address=self.w3.to_checksum_address(token_address), abi=erc20_abi)

            # name
            try:
                name = token_contract.functions.name().call()
                self.console.log(f"[green]Token name: {name}[/green]")
            except Exception as e:
                self.console.log(f"[bold red]Error getting token name: {e}[/bold red]")
                return None

            # nonce
            try:
                nonce = token_contract.functions.nonces(owner).call()
                self.console.log(f"[green]Got nonce using nonces(address): {nonce}[/green]")
            except Exception as e1:
                try:
                    nonce = token_contract.functions.nonces().call()
                    self.console.log(f"[green]Got nonce using nonces(): {nonce}[/green]")
                except Exception as e2:
                    self.console.log(f"[bold red]Error getting nonce: {e1}, {e2}[/bold red]")
                    return None

            # version
            try:
                version = token_contract.functions.version().call()
                self.console.log(f"[green]Token version: {version}[/green]")
            except Exception:
                version = '1'
                self.console.log("[yellow]Version not found, defaulting to '1'[/yellow]")

            # domain separator (optional check)
            try:
                token_contract.functions.DOMAIN_SEPARATOR().call()
                self.console.log("[green]Successfully got DOMAIN_SEPARATOR[/green]")
            except Exception as e:
                self.console.log(f"[bold red]Error getting DOMAIN_SEPARATOR: {e}[/bold red]")
                return None

            # Build typed data
            domain = {
                'name': name,
                'version': version,
                'chainId': self.chain_id,
                'verifyingContract': self.w3.to_checksum_address(token_address)
            }
            permit = {
                'owner': owner,
                'spender': spender,
                'value': value,
                'nonce': nonce,
                'deadline': deadline
            }
            typed_data = {
                'types': {
                    'EIP712Domain': [
                        {'name': 'name', 'type': 'string'},
                        {'name': 'version', 'type': 'string'},
                        {'name': 'chainId', 'type': 'uint256'},
                        {'name': 'verifyingContract', 'type': 'address'}
                    ],
                    'Permit': [
                        {'name': 'owner', 'type': 'address'},
                        {'name': 'spender', 'type': 'address'},
                        {'name': 'value', 'type': 'uint256'},
                        {'name': 'nonce', 'type': 'uint256'},
                        {'name': 'deadline', 'type': 'uint256'}
                    ]
                },
                'domain': domain,
                'primaryType': 'Permit',
                'message': permit
            }

            # Sign EIP-712
            try:
                encoded_message = encode_structured_data(typed_data)
                signed_message = Account.sign_message(encoded_message, private_key=private_key)
                v, r, s = signed_message.v, signed_message.r, signed_message.s
                self.console.log("[green]Successfully signed permit message[/green]")
                return {'v': v, 'r': r, 's': s, 'deadline': deadline}
            except Exception as e:
                self.console.log(f"[bold red]Error signing permit data: {e}[/bold red]")
                return None

        except json.JSONDecodeError as e:
            self.console.log(f"[bold red]Error parsing ERC20_PERMIT_ABI: {str(e)}[/bold red]")
            return None
        except Exception as e:
            self.console.log(f"[bold red]Token does not support EIP-2612 permits: {e}[/bold red]")
            return None

    def check_allowance(self, token_address, owner_address, spender_address):
        """Check the current allowance of the spender for the owner's token."""
        try:
            if token_address == '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE':
                return float('inf')  # Native token doesn't need allowance
            abi = json.loads(self.chain_config.TOKEN_ABI)
            token_contract = self.w3.eth.contract(address=token_address, abi=abi)
            allowance = token_contract.functions.allowance(owner_address, spender_address).call()
            return allowance
        except Exception as e:
            self.console.log(f"[bold red]Error checking allowance: {e}[/bold red]")
            raise

    def get_swap_route(self, chain, token_in, token_out, amount_in):
        """
        Fetch the best swap route from KyberSwap Aggregator API for the selected chain.
        We'll also uncomment the fee logic so you can optionally define fee_amount > 0 if you want to charge fees.
        """
        url = self.kyberswap_api_route
        headers = self.KYBERSWAP_API_HEADERS.copy()
        headers["source"] = headers.get("x-client-id", "")

        params = {
            "tokenIn": token_in,
            "tokenOut": token_out,
            "amountIn": amount_in,
            "deadline": int(time.time()) + 1200,  # 20 min
            "slippageTolerance": 50  # 0.5%
        }

        # Un-commented fee logic:
        fee_amount = 0  # <-- set this if you want to charge fees
        if fee_amount > 0:
            params["feeAmount"] = fee_amount
            params["chargeFeeBy"] = "currency_in"  # or "currency_out"

        # Remove empty keys
        params = {k: v for k, v in params.items() if v not in [None, "", []]}

        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            route = response.json()
            if route.get("code") == 0:
                self.console.log("[bold green]Fetched swap route successfully.[/bold green]")
                return route
            else:
                self.console.log(f"[bold red]Failed to fetch swap route: {route.get('message')}[/bold red]")
                self.console.log(f"[yellow]Error code: {route.get('code')}[/yellow]")
                self.console.log(f"[yellow]Response data: {response.text}[/yellow]")
                return None
        except requests.exceptions.RequestException as e:
            self.console.log(f"[bold red]Error fetching swap route: {str(e)}[/bold red]")
            if hasattr(e, 'response') and e.response is not None:
                self.console.log(f"[yellow]Response status code: {e.response.status_code}[/yellow]")
                self.console.log(f"[yellow]Response text: {e.response.text}[/yellow]")
            return None

    def get_encoded_swap_data(self, chain , route_summary, tx_params):
        """
        Retrieve the calldata needed to execute the swap from the aggregator's /route/build endpoint.
        """
        url = self.kyberswap_api_build
        headers = self.KYBERSWAP_API_HEADERS.copy()
        headers["source"] = headers.get("x-client-id", "")

        payload = {
            "routeSummary": route_summary,
            **tx_params
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            encoded_data = response.json()
            if encoded_data.get("code") == 0:
                self.console.log("[bold green]Fetched encoded swap data successfully.[/bold green]")
                self.console.log(f"[yellow]Encoded Data: {json.dumps(encoded_data, indent=2)}[/yellow]")
                return encoded_data
            else:
                self.console.log(f"[bold red]Failed to fetch encoded swap data: {encoded_data.get('message')}[/bold red]")
                self.console.log(f"[yellow]Error code: {encoded_data.get('code')}[/yellow]")
                self.console.log(f"[yellow]Response data: {response.text}[/yellow]")
                return None
        except requests.exceptions.RequestException as e:
            self.console.log(f"[bold red]Error fetching encoded swap data: {e}[/bold red]")
            return None

    def get_swap_info_with_encoded_data(self, encoded_data):
        """(Optional) Retrieve more info from encoded data if there's a separate /route/encode endpoint."""
        url = self.kyberswap_api_encode
        headers = self.KYBERSWAP_API_HEADERS.copy()
        headers["source"] = headers.get("x-client-id", "")
        payload = {"encodedData": encoded_data}

        try:
            self.console.log(f"[yellow]Request URL: {url}[/yellow]")
            self.console.log(f"[yellow]Request Payload: {json.dumps(payload, indent=2)}[/yellow]")

            response = requests.post(url, json=payload, headers=headers)
            self.console.log(f"[yellow]Response Status Code: {response.status_code}[/yellow]")
            self.console.log(f"[yellow]Response Text: {response.text}[/yellow]")
            response.raise_for_status()

            swap_info = response.json()
            if swap_info.get("code") == 0:
                self.console.log("[bold green]Fetched swap info successfully.[/bold green]")
                return swap_info
            else:
                self.console.log(f"[bold red]Failed to fetch swap info: {swap_info.get('message')}[/bold red]")
                self.console.log(f"[yellow]Error code: {swap_info.get('code')}[/yellow]")
                self.console.log(f"[yellow]Response data: {response.text}[/yellow]")
                return None
        except requests.exceptions.RequestException as e:
            self.console.log(f"[bold red]Error fetching swap info: {e}[/bold red]")
            if hasattr(e, 'response') and e.response is not None:
                self.console.log(f"[yellow]Response status code: {e.response.status_code}[/yellow]")
                self.console.log(f"[yellow]Response text: {e.response.text}[/yellow]")
            return None

    def execute_swap(self, private_key, encoded_data, router_address , from_token , amount_in_wei):
        """Send the swap transaction to the KyberSwap router contract."""
        max_fee_per_gas, max_priority_fee_per_gas = self.fetch_suggested_fees()
        if not max_fee_per_gas or not max_priority_fee_per_gas:
            self.console.log("[bold red]Could not fetch valid gas fees. Aborting swap.[/bold red]")
            return

        try:
            account = Account.from_key(private_key)
            nonce = self.w3.eth.get_transaction_count(account.address)

            self.console.log(f"[debug]Executing swap for router_address: {router_address}[/debug]")
            calldata = encoded_data.get("data", {}).get("data")
            gas_detail = encoded_data.get("data", {}).get("gas")

            if not calldata:
                self.console.log("[bold red]Calldata is missing in encoded swap data. Aborting swap.[/bold red]")
                return

            # Clean up
            calldata = calldata.replace('\n', '').replace(' ', '')
            if not calldata.startswith('0x'):
                self.console.log("[bold red]Invalid calldata format. Aborting swap.[/bold red]")
                return
            
            # If from_token is 0xEeeeeEeee... => native coin => tx["value"] = amount_in_wei
            if from_token.lower() == "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee":
                tx_value = amount_in_wei
            else:
                tx_value = 0  # Standard ERC-20 swap => no value in the transaction

            tx = {
                'chainId': self.chain_id,
                'from': account.address,
                'to': router_address,
                'nonce': nonce,
                'gas': int(gas_detail) if gas_detail else 21000,
                'maxFeePerGas': max_fee_per_gas,
                'maxPriorityFeePerGas': max_priority_fee_per_gas,
                'data': calldata,
                'value': tx_value
            }

            self.console.log(f"[debug]Transaction Params: {json.dumps(tx, indent=2)}[/debug]")

            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            self.console.log(f"[green]Swap transaction sent: {tx_hash.hex()}[/green]")

            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            if receipt['status'] == 1:
                self.console.log("[bold green]Swap successful![/bold green]")
            else:
                self.console.log("[bold red]Swap failed![/bold red]")

        except Exception as e:
            self.console.log(f"[bold red]Error executing swap: {e}[/bold red]")

    def swap_tokens_kyberswap(self, private_key):
        """Main function to handle token swapping via KyberSwap."""
        account = Account.from_key(private_key)
        sender = account.address
        recipient = account.address  # can be changed if needed

        # 1. Select tokens (with manual contract address option)
        from_token_choices = list(self.tokens.keys()) + ["[Enter contract address manually]"]
        from_token_full = questionary.select(
            "Select the token you want to swap from:",
            choices=from_token_choices
        ).ask()
        if from_token_full == "[Enter contract address manually]":
            manual_from_token = questionary.text(
                "Enter the contract address of the token you want to swap from:"
            ).ask()
            # Validate address format
            try:
                manual_from_token = self.w3.to_checksum_address(manual_from_token.strip())
            except Exception:
                self.console.log("[bold red]Invalid contract address entered. Aborting.[/bold red]")
                return
            from_token_full = f"Custom ({manual_from_token})"
            self.tokens[from_token_full] = manual_from_token

        to_token_choices = [symbol for symbol in self.tokens.keys() if symbol != from_token_full] + ["[Enter contract address manually]"]
        to_token_full = questionary.select(
            "Select the token you want to swap to:",
            choices=to_token_choices
        ).ask()
        if to_token_full == "[Enter contract address manually]":
            manual_to_token = questionary.text(
                "Enter the contract address of the token you want to swap to:"
            ).ask()
            # Validate address format
            try:
                manual_to_token = self.w3.to_checksum_address(manual_to_token.strip())
            except Exception:
                self.console.log("[bold red]Invalid contract address entered. Aborting.[/bold red]")
                return
            to_token_full = f"Custom ({manual_to_token})"
            self.tokens[to_token_full] = manual_to_token

        from_token = self.tokens[from_token_full]
        to_token = self.tokens[to_token_full]
        from_token_symbol = from_token_full.split(' (')[0]
        to_token_symbol = to_token_full.split(' (')[0]

        # 2. Check balance
        try:
            balance_raw, human_readable_balance, decimals = self.check_token_balance(from_token, sender)
            self.console.log(f"[bold blue]Your balance of {from_token_symbol}: {human_readable_balance}[/bold blue]")
            if balance_raw <= 0:
                self.console.log("[bold red]Error: Zero balance for the input token[/bold red]")
                return
        except Exception as e:
            self.console.log(f"[bold red]Error fetching token balance: {e}[/bold red]")
            return

        # 3. Get Amount to Swap
        amount_choice = questionary.select(
            "Choose amount input method:",
            choices=["Enter fixed amount", "Enter based %"]
        ).ask()

        if amount_choice == "Enter fixed amount":
            amount = questionary.text(
                f"Enter the amount of {from_token_symbol} to swap (max {human_readable_balance}):"
            ).ask()
            try:
                amount_float = float(amount)
                if amount_float > human_readable_balance:
                    self.console.log(f"[bold red]Error: Insufficient balance[/bold red]")
                    return
                amount_in_wei = int(amount_float * (10 ** decimals))
            except ValueError:
                self.console.log(f"[bold red]Error: Invalid amount entered[/bold red]")
                return
        else:
            percentage = questionary.text(
                f"Enter how much (%) of {from_token_symbol} balance you want to swap (1-100):"
            ).ask()
            try:
                percentage_float = float(percentage)
                if not 0 < percentage_float <= 100:
                    self.console.log(f"[bold red]Error: Percentage must be between 1 and 100[/bold red]")
                    return
                amount_float = (percentage_float / 100) * human_readable_balance
                self.console.log(f"[bold blue]Amount to swap: {amount_float} {from_token_symbol}[/bold blue]")
                amount_in_wei = int(amount_float * (10 ** decimals))
            except ValueError:
                self.console.log(f"[bold red]Error: Invalid percentage entered[/bold red]")
                return

        # 4. Slippage
        slippage_choice = questionary.select(
            "Choose slippage setting:",
            choices=["Default (0.5%)", "Custom"]
        ).ask()
        if slippage_choice == "Custom":
            slippage = questionary.text("Enter slippage tolerance % (e.g., 0.5 for 0.5%):").ask()
            try:
                slippage_float = float(slippage) / 100
            except ValueError:
                self.console.log("[bold red]Invalid slippage value. Using default 0.5%[/bold red]")
                slippage_float = 0.005
        else:
            slippage_float = 0.005

        # 5. Fetch gas fees
        max_fee_per_gas, max_priority_fee_per_gas = self.fetch_suggested_fees()
        if not max_fee_per_gas or not max_priority_fee_per_gas:
            self.console.log("[bold red]Could not fetch valid gas fees. Aborting swap.[/bold red]")
            return

        # 6. Fetch swap route
        route = self.get_swap_route(
            chain=self.chain_config.CHAIN_NAME,
            token_in=from_token,
            token_out=to_token,
            amount_in=amount_in_wei
        )
        if not route:
            self.console.log("[bold red]Failed to fetch swap route. Aborting swap.[/bold red]")
            return

        data = route.get("data")
        if not data:
            self.console.log("[bold red]No data found in route response. Aborting swap.[/bold red]")
            return

        route_summary = data.get("routeSummary")
        router_address = data.get("routerAddress")

        if not router_address:
            self.console.log("[bold red]Router address not found. Aborting swap.[/bold red]")
            return
        if not route_summary:
            self.console.log("[bold red]Incomplete route data received. Aborting swap.[/bold red]")
            return

        self.console.log(f"[bold green]KyberSwap Router Address: {router_address}[/bold green]")

        # 7. Check allowance
        try:
            # Skip allowance check for native token
            if from_token == "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE":
                self.console.log("[green]Native token - no allowance needed[/green]")
            else:
                allowance = self.check_allowance(from_token, sender, router_address)
                allowance_human = allowance / (10 ** decimals)
                required_allowance_human = amount_in_wei / (10 ** decimals)

                self.console.log(f"[bold blue]Current Allowance: {allowance_human} {from_token_symbol}[/bold blue]")
                self.console.log(f"[bold blue]Required Allowance: {required_allowance_human} {from_token_symbol}[/bold blue]")

                if allowance < amount_in_wei:
                    self.console.log("[yellow]Insufficient allowance. Approving tokens...[/yellow]")
                    # EIP-2612?
                    supports_permit = self.check_eip2612_support(from_token, sender)
                    if supports_permit:
                        self.console.log("[green]Token supports EIP-2612. Using permit for approval.[/green]")
                        deadline = int(time.time()) + 1200
                        permit_data = self.get_permit_data(
                            token_address=from_token,
                            owner=sender,
                            spender=router_address,
                            value=amount_in_wei,
                            deadline=deadline,
                            private_key=private_key
                        )
                        if permit_data:
                            self.console.log("[bold green]Permit data generated successfully.[/bold green]")
                            route_summary['permit'] = permit_data
                        else:
                            self.console.log("[bold red]Failed to generate permit data. Aborting swap.[/bold red]")
                            return
                    else:
                        self.console.log("[bold yellow]Token does not support EIP-2612. "
                                        "Proceeding with traditional approval.[/bold yellow]")
                        if not questionary.confirm("Do you want to proceed with the approval transaction?").ask():
                            self.console.log("[yellow]Approval cancelled by user[/yellow]")
                            return

                        self.send_approval_transaction(
                            private_key=private_key,
                            token_address=from_token,
                            spender=router_address,
                            amount=amount_in_wei,
                            max_fee_per_gas=max_fee_per_gas,
                            max_priority_fee_per_gas=max_priority_fee_per_gas
                        )
                        allowance = self.check_allowance(from_token, sender, router_address)
                        allowance_human = allowance / (10 ** decimals)
                        self.console.log(f"[bold green]New Allowance: {allowance_human} {from_token_symbol}[/bold green]")
                else:
                    self.console.log(f"[green]Sufficient allowance exists: {allowance_human} {from_token_symbol}[/green]")
        except Exception as e:
            self.console.log(f"[bold red]Error during allowance check/approval: {e}[/bold red]")
            return

        # 8. Prepare TX params
        tx_params = {
            "sender": sender,
            "recipient": recipient,
            "deadline": int(time.time()) + 1200,
            "slippageTolerance": int(slippage_float * 10000),  # bps
            "chargeFeeBy": "",
            "feeAmount": 0,
            "isInBps": True,
            "feeReceiver": "",
            "sources": "",
            "referral": "",
            "enableGasEstimation": True,
            "permit": "",  # Overwritten if we used EIP-2612 above
            "ignoreCappedSlippage": False
        }

        # If permit was used
        if 'permit' in route_summary:
            tx_params['permit'] = route_summary['permit']

        # Clean out empty
        tx_params = {k: v for k, v in tx_params.items() if v not in [None, "", []]}

        # 9. Get encoded swap data
        encoded_data = self.get_encoded_swap_data(
            chain=self.chain_config.CHAIN_NAME,
            route_summary=route_summary,
            tx_params=tx_params
        )
            
        
        if not encoded_data:
            self.console.log("[bold red]Failed to get encoded swap data. Aborting swap.[/bold red]")
            return

        # 10. Extract some swap details
        swap_details = encoded_data.get("data", {})
        amount_in = swap_details.get("amountIn")
        amount_out = swap_details.get("amountOut")
        gas = swap_details.get("gas")
        gas_usd = swap_details.get("gasUsd")
        amount_in_usd = swap_details.get("amountInUsd")
        amount_out_usd = swap_details.get("amountOutUsd")

        amount_in_eth = Web3.from_wei(int(amount_in), 'ether') if amount_in else 0
        amount_out_eth = Web3.from_wei(int(amount_out), 'ether') if amount_out else 0

        self.console.log(f"[bold blue]Swap Details:[/bold blue]")
        self.console.log(f"  - Amount In: {amount_in_eth} {from_token_symbol} (${amount_in_usd})")
        self.console.log(f"  - Expected Amount Out: {amount_out_eth} {to_token_symbol} (${amount_out_usd})")
        self.console.log(f"  - Gas: {gas} units (${gas_usd})")

        # 11. Confirm
        if not questionary.confirm("Do you want to proceed with the swap based on the above details?").ask():
            self.console.log("[yellow]Swap cancelled by user[/yellow]")
            return

        # 12. Execute
        self.execute_swap(
            private_key=private_key,
            encoded_data=encoded_data,
            router_address=router_address,
            from_token=from_token,
            amount_in_wei=amount_in_wei  # pass in the from_token address here
        )

    def start_swaps(self):
        """Initiate the swapping process for all loaded private keys."""
        for private_key in self.wallet_private_keys:
            try:
                self.swap_tokens_kyberswap(private_key)
            except Exception as e:
                self.console.log(f"[bold red]Error in swap for wallet: {e}[/bold red]")

    def run(self):
        """Run the SwapManager."""
        # Let user pick how to load private keys
        self.select_private_key_input_method()
        if not self.wallet_private_keys:
            self.console.log("[bold red]No private keys loaded. Exiting.[/bold red]")
            sys.exit(1)

        # Start the swaps
        self.start_swaps()


def main():
    """
    Main entry point. Prompt the user for which chain to use, then run the SwapManager with that chain config.
    """
    chain_choices = ["POLYGON", "OP", "Base", "ARB", "Linea", "ETHER"]
    chain_selection = questionary.select("Select chain:", choices=chain_choices).ask()

    # Dynamically pick the chain config
    if chain_selection == "POLYGON":
        chain_config = config.POLYGON
    elif chain_selection == "OP":
        chain_config = config.OP
    elif chain_selection == "Base":
        chain_config = config.Base
    elif chain_selection == "ARB":
        chain_config = config.ARB
    elif chain_selection == "Linea":
        chain_config = config.Linea
    elif chain_selection == "ETHER":
        chain_config = config.ETHER
    else:
        # fallback
        chain_config = config.POLYGON

    # Initialize and run
    swap_manager = SwapManager(chain_config=chain_config)
    swap_manager.run()


if __name__ == "__main__":
    main()
