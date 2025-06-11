# config.py
import eth_abi
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BASE_PATH = Path(__file__).resolve().parent / "resources"  # removed trailing slash
KYBERSWAP_API_BASE = "https://aggregator-api.kyberswap.com/"
KYBERSWAP_API_HEADERS = {
        "Content-Type": "application/json",
        "x-client-id": "barsavaClientId"  # Replace with your actual Client ID
    }

ALCHEMY_API_KEY = os.getenv('ALCHEMY_API_KEY')
INFURA_API_KEY = os.getenv('INFURA_API_KEY')

QUOTER_ABI = '''[
    {
        "inputs": [
            {"internalType": "address", "name": "tokenIn", "type": "address"},
            {"internalType": "address", "name": "tokenOut", "type": "address"},
            {"internalType": "uint24", "name": "fee", "type": "uint24"},
            {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
            {"internalType": "uint160", "name": "sqrtPriceLimitX96", "type": "uint160"}
        ],
        "name": "quoteExactInputSingle",
        "outputs": [{"internalType": "uint256", "name": "amountOut", "type": "uint256"}],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]'''

MINIMAL_ABI_PERMIT = '''[
        {
            "inputs": [
                {"internalType": "address", "name": "owner", "type": "address"},
                {"internalType": "address", "name": "spender", "type": "address"},
                {"internalType": "uint256", "name": "value", "type": "uint256"},
                {"internalType": "uint256", "name": "deadline", "type": "uint256"},
                {"internalType": "uint8", "name": "v", "type": "uint8"},
                {"internalType": "bytes32", "name": "r", "type": "bytes32"},
                {"internalType": "bytes32", "name": "s", "type": "bytes32"}
            ],
            "name": "permit",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [{"internalType": "address", "name": "owner", "type": "address"}],
            "name": "nonces",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "nonces",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function"
        }
    ]'''
    
ERC20_PERMIT_ABI = '''[
        {
            "inputs": [
                {"internalType": "address", "name": "owner", "type": "address"},
                {"internalType": "address", "name": "spender", "type": "address"},
                {"internalType": "uint256", "name": "value", "type": "uint256"},
                {"internalType": "uint256", "name": "deadline", "type": "uint256"},
                {"internalType": "uint8", "name": "v", "type": "uint8"},
                {"internalType": "bytes32", "name": "r", "type": "bytes32"},
                {"internalType": "bytes32", "name": "s", "type": "bytes32"}
            ],
            "name": "permit",
            "outputs": [],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "name",
            "outputs": [{"internalType": "string", "name": "", "type": "string"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "version",
            "outputs": [{"internalType": "string", "name": "", "type": "string"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "nonces",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [{"internalType": "address", "name": "owner", "type": "address"}],
            "name": "nonces",
            "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function"
        },
        {
            "inputs": [],
            "name": "DOMAIN_SEPARATOR",
            "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
            "stateMutability": "view",
            "type": "function"
        }
    ]'''
    
TOKEN_ABI = '''[
        {
            "constant": false,
            "inputs": [
                {"name": "_to", "type": "address"},
                {"name": "_value", "type": "uint256"}
            ],
            "name": "transfer",
            "outputs": [{"name": "", "type": "bool"}],
            "type": "function"
        },
        {
            "constant": false,
            "inputs": [
                {"name": "_spender", "type": "address"},
                {"name": "_value", "type": "uint256"}
            ],
            "name": "approve",
            "outputs": [{"name": "", "type": "bool"}],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [
                {"name": "_owner", "type": "address"},
                {"name": "_spender", "type": "address"}
            ],
            "name": "allowance",
            "outputs": [{"name": "remaining", "type": "uint256"}],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [{"name": "_owner", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "balance", "type": "uint256"}],
            "type": "function"
        },
        {
            "constant": true,
            "inputs": [],
            "name": "decimals",
            "outputs": [{"name": "", "type": "uint8"}],
            "type": "function"
        }
    ]'''


class POLYGON :
# RPC URL for connecting to Polygon mainnet
    ALCHEMY_API_KEY = ALCHEMY_API_KEY
    ALCHEMY_RPC_URL = f"https://polygon-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}"
    #TATUM_API_KEY = "t-6722ee17eac5621e6ae170eb-c8f714a9b5284645a001f7ee"
    
    CHAIN_ID = 137
    CHAIN_NAME = "polygon"
    NATIVE_TOKEN = "0x0000000000000000000000000000000000001010"

    # Paths to your wallet and address files
    KYBERSWAP_API_ROUTE = os.path.join(KYBERSWAP_API_BASE + CHAIN_NAME  + "/api/v1/routes")
    KYBERSWAP_API_BUILD = os.path.join(KYBERSWAP_API_BASE + CHAIN_NAME  + "/api/v1/route/build")
    KYBERSWAP_API_ENCODE = os.path.join(KYBERSWAP_API_BASE + CHAIN_NAME  + "/route/encode")
    WALLET_FILE = os.path.join(BASE_PATH,"wallet.txt") #private keys
    ADDRESS_FILE = os.path.join(BASE_PATH, "receive.txt") #public key
    CONTRACTS_FILE = os.path.join(BASE_PATH, CHAIN_NAME, "contracts.txt")
    TOKENS_KYBER_FILE = os.path.join(BASE_PATH, CHAIN_NAME, "tokens_kyber.txt") #tokens
    

    # Token-specific settings (optional)
    MINIMAL_ABI_PERMIT = MINIMAL_ABI_PERMIT
    ERC20_PERMIT_ABI = ERC20_PERMIT_ABI
    TOKEN_ABI = TOKEN_ABI

    
    # Infura Gas API Key for gas price estimation
    INFURA_API_KEY = INFURA_API_KEY
    INFURA_API_KEY2 = "ae375268a0ed49eab2313e2f1ac912bf"


    # Infura URLs for RPC and Gas Price API
    INFURA_RPC_URL = f"https://polygon-mainnet.g.alchemy.com/v2/JU3_TwEZDx6bPNyDc1AgrRZWphXoPEVk"
    INFURA_GAS_API_URL = f"https://gas.api.infura.io/v3/{INFURA_API_KEY}/networks/{CHAIN_ID}/suggestedGasFees"
    # Uniswap V3 Quoter Address

class OP :
    # RPC URL for connecting to Polygon mainnet
    ALCHEMY_API_KEY = ALCHEMY_API_KEY
    ALCHEMY_RPC_URL = f"https://opt-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}"
    #TATUM_API_KEY = "t-6722ee17eac5621e6ae170eb-c8f714a9b5284645a001f7ee"

    CHAIN_ID = "10"
    CHAIN_NAME = "optimism"
    NATIVE_TOKEN = "0x4200000000000000000000000000000000000042"

    # Paths to your wallet and address files
    KYBERSWAP_API_ROUTE = os.path.join(KYBERSWAP_API_BASE + CHAIN_NAME  + "/api/v1/routes")
    KYBERSWAP_API_BUILD = os.path.join(KYBERSWAP_API_BASE + CHAIN_NAME  + "/api/v1/route/build")
    KYBERSWAP_API_ENCODE = os.path.join(KYBERSWAP_API_BASE + CHAIN_NAME  + "/route/encode")
    
    # Paths to your wallet and address files
    WALLET_FILE = os.path.join(BASE_PATH,"wallet.txt") #private keys
    ADDRESS_FILE = os.path.join(BASE_PATH, "receive.txt") #public key
    CONTRACTS_FILE = os.path.join(BASE_PATH, "OP", "contracts.txt") #token_contracts
    TOKENS_KYBER_FILE = os.path.join(BASE_PATH, "OP", "tokens_kyber.txt") #tokens


    TOKEN_ABI = '''[
        {
            "constant": false,
            "inputs": [
                {"name": "_to", "type": "address"},
                {"name": "_value", "type": "uint256"}
            ],
            "name": "transfer",
            "outputs": [{"name": "", "type": "bool"}],
            "type": "function"
        }
    ]'''
    
    # Infura Gas API Key for gas price estimation
    INFURA_API_KEY = "cbd40adce35444b88bcbca3103b7408c"
    INFURA_API_KEY2 = "ae375268a0ed49eab2313e2f1ac912bf"

    # Infura URLs for RPC and Gas Price API
    #INFURA_RPC_URL = f"https://polygon-mainnet.g.alchemy.com/v2/JU3_TwEZDx6bPNyDc1AgrRZWphXoPEVk"
    INFURA_GAS_API_URL = f"https://gas.api.infura.io/v3/{INFURA_API_KEY}/networks/{CHAIN_ID}/suggestedGasFees"

class Base :
    # RPC URL for connecting to Polygon mainnet
    ALCHEMY_API_KEY = ALCHEMY_API_KEY
    ALCHEMY_RPC_URL = f"https://base-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}"
    #TATUM_API_KEY = "t-6722ee17eac5621e6ae170eb-c8f714a9b5284645a001f7ee"
    
    CHAIN_ID = "8453"
    CHAIN_NAME = "base"
    NATIVE_TOKEN = "0x0000000000001fF3684f28c67538d4D072C22734"

    # Paths to your wallet and address files
    KYBERSWAP_API_ROUTE = os.path.join(KYBERSWAP_API_BASE + CHAIN_NAME  + "/api/v1/routes")
    KYBERSWAP_API_BUILD = os.path.join(KYBERSWAP_API_BASE + CHAIN_NAME  + "/api/v1/route/build")
    KYBERSWAP_API_ENCODE = os.path.join(KYBERSWAP_API_BASE + CHAIN_NAME  + "/route/encode")

    # Paths to your wallet and address files
    WALLET_FILE = os.path.join(BASE_PATH,"wallet.txt") #private keys
    ADDRESS_FILE = os.path.join(BASE_PATH, "receive.txt") #public key
    CONTRACTS_FILE = os.path.join(BASE_PATH, "BASE", "contracts.txt") #token_contracts
    TOKENS_KYBER_FILE = os.path.join(BASE_PATH, "BASE", "tokens_kyber.txt") #tokens


    TOKEN_ABI = '''[
        {
            "constant": false,
            "inputs": [
                {"name": "_to", "type": "address"},
                {"name": "_value", "type": "uint256"}
            ],
            "name": "transfer",
            "outputs": [{"name": "", "type": "bool"}],
            "type": "function"
        }
    ]'''

    # Infura Gas API Key for gas price estimation
    INFURA_API_KEY = INFURA_API_KEY
    INFURA_API_KEY2 = "ae375268a0ed49eab2313e2f1ac912bf"

    # Infura URLs for RPC and Gas Price API
    #INFURA_RPC_URL = f"https://polygon-mainnet.g.alchemy.com/v2/JU3_TwEZDx6bPNyDc1AgrRZWphXoPEVk"
    INFURA_GAS_API_URL = f"https://gas.api.infura.io/v3/{INFURA_API_KEY}/networks/{CHAIN_ID}/suggestedGasFees"

class ARB :
    # RPC URL for connecting to Polygon mainnet
    ALCHEMY_API_KEY = ALCHEMY_API_KEY
    ALCHEMY_RPC_URL = f"https://arb-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}"
    #TATUM_API_KEY = "t-6722ee17eac5621e6ae170eb-c8f714a9b5284645a001f7ee"
    
    CHAIN_ID = "59144"
    CHAIN_NAME = "arbitrum"
    NATIVE_TOKEN = "0x912ce59144191c1204e64559fe8253a0e49e6548"

    # Paths to your wallet and address files
    KYBERSWAP_API_ROUTE = os.path.join(KYBERSWAP_API_BASE + CHAIN_NAME  + "/api/v1/routes")
    KYBERSWAP_API_BUILD = os.path.join(KYBERSWAP_API_BASE + CHAIN_NAME  + "/api/v1/route/build")
    KYBERSWAP_API_ENCODE = os.path.join(KYBERSWAP_API_BASE + CHAIN_NAME  + "/route/encode")

    # Paths to your wallet and address files
    WALLET_FILE = os.path.join(BASE_PATH,"wallet.txt") #private keys
    ADDRESS_FILE = os.path.join(BASE_PATH, "receive.txt") #public key
    CONTRACTS_FILE = os.path.join(BASE_PATH, "ARB", "contracts.txt") #token_contracts
    TOKENS_KYBER_FILE = os.path.join(BASE_PATH, "ARB", "tokens_kyber.txt") #tokens


    TOKEN_ABI = '''[
        {
            "constant": false,
            "inputs": [
                {"name": "_to", "type": "address"},
                {"name": "_value", "type": "uint256"}
            ],
            "name": "transfer",
            "outputs": [{"name": "", "type": "bool"}],
            "type": "function"
        }
    ]'''
    
    # Infura Gas API Key for gas price estimation
    INFURA_API_KEY = INFURA_API_KEY
    INFURA_API_KEY2 = "ae375268a0ed49eab2313e2f1ac912bf"

    # Infura URLs for RPC and Gas Price API
    #INFURA_RPC_URL = f"https://polygon-mainnet.g.alchemy.com/v2/JU3_TwEZDx6bPNyDc1AgrRZWphXoPEVk"
    INFURA_GAS_API_URL = f"https://gas.api.infura.io/v3/{INFURA_API_KEY}/networks/{CHAIN_ID}/suggestedGasFees"
    
class Linea :
    # RPC URL for connecting to Polygon mainnet
    ALCHEMY_API_KEY = ALCHEMY_API_KEY
    ALCHEMY_RPC_URL = f"https://linea-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}"
    #TATUM_API_KEY = "t-6722ee17eac5621e6ae170eb-c8f714a9b5284645a001f7ee"
    
    CHAIN_ID = "59144"
    CHAIN_NAME = "linea"
    NATIVE_TOKEN = "0x000000000000175a8b9bC6d539B3708EEd92EA6c"

     # Paths to your wallet and address files
    KYBERSWAP_API_ROUTE = os.path.join(KYBERSWAP_API_BASE + CHAIN_NAME  + "/api/v1/routes")
    KYBERSWAP_API_BUILD = os.path.join(KYBERSWAP_API_BASE + CHAIN_NAME  + "/api/v1/route/build")
    KYBERSWAP_API_ENCODE = os.path.join(KYBERSWAP_API_BASE + CHAIN_NAME  + "/route/encode")


    # Paths to your wallet and address files
    WALLET_FILE = os.path.join(BASE_PATH,"wallet.txt") #private keys
    ADDRESS_FILE = os.path.join(BASE_PATH, "receive.txt") #public key
    CONTRACTS_FILE = os.path.join(BASE_PATH, "LINEA", "contracts.txt") #token_contracts
    TOKENS_KYBER_FILE = os.path.join(BASE_PATH, "LINEA", "tokens_kyber.txt") #tokens


    TOKEN_ABI = '''[
        {
            "constant": false,
            "inputs": [
                {"name": "_to", "type": "address"},
                {"name": "_value", "type": "uint256"}
            ],
            "name": "transfer",
            "outputs": [{"name": "", "type": "bool"}],
            "type": "function"
        }
    ]'''

    # Infura Gas API Key for gas price estimation
    INFURA_API_KEY = INFURA_API_KEY
    INFURA_API_KEY2 = "ae375268a0ed49eab2313e2f1ac912bf"

    # Infura URLs for RPC and Gas Price API
    #INFURA_RPC_URL = f"https://polygon-mainnet.g.alchemy.com/v2/JU3_TwEZDx6bPNyDc1AgrRZWphXoPEVk"
    INFURA_GAS_API_URL = f"https://gas.api.infura.io/v3/{INFURA_API_KEY}/networks/{CHAIN_ID}/suggestedGasFees"

class ETHER :
    # RPC URL for connecting to Polygon mainnet
    ALCHEMY_API_KEY = ALCHEMY_API_KEY
    ALCHEMY_RPC_URL = f"https://eth-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}"
    #TATUM_API_KEY = "t-6722ee17eac5621e6ae170eb-c8f714a9b5284645a001f7ee"

    CHAIN_ID = "1"
    CHAIN_NAME = "ethereum"
    NATIVE_TOKEN = "0x0000000000001fF3684f28c67538d4D072C22734"

    # Paths to your wallet and address files
    KYBERSWAP_API_ROUTE = os.path.join(KYBERSWAP_API_BASE + CHAIN_NAME  + "/api/v1/routes")
    KYBERSWAP_API_BUILD = os.path.join(KYBERSWAP_API_BASE + CHAIN_NAME  + "/api/v1/route/build")
    KYBERSWAP_API_ENCODE = os.path.join(KYBERSWAP_API_BASE + CHAIN_NAME  + "/route/encode")
    
    # Paths to your wallet and address files
    WALLET_FILE = os.path.join(BASE_PATH,"wallet.txt") #private keys
    CONTRACTS_FILE = os.path.join(BASE_PATH, "ETHER", "contracts.txt") #token_contracts
    TOKENS_KYBER_FILE = os.path.join(BASE_PATH, "ETHER", "tokens_kyber.txt") #tokens


    TOKEN_ABI = '''[
        {
            "constant": false,
            "inputs": [
                {"name": "_to", "type": "address"},
                {"name": "_value", "type": "uint256"}
            ],
            "name": "transfer",
            "outputs": [{"name": "", "type": "bool"}],
            "type": "function"
        }
    ]'''

    # Infura Gas API Key for gas price estimation
    INFURA_API_KEY = INFURA_API_KEY
    INFURA_API_KEY2 = "ae375268a0ed49eab2313e2f1ac912bf"

    # Infura URLs for RPC and Gas Price API
    #INFURA_RPC_URL = f"https://polygon-mainnet.g.alchemy.com/v2/JU3_TwEZDx6bPNyDc1AgrRZWphXoPEVk"
    INFURA_GAS_API_URL = f"https://gas.api.infura.io/v3/{INFURA_API_KEY}/networks/{CHAIN_ID}/suggestedGasFees"
    
MODULE_PATH = Path(__file__).resolve().parent / "modules"
