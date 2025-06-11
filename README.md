# MWswap
Automates low-fee, multi-wallet ERC20 swaps on KyberSwap with built-in gas safety

# KyberSwap Bulk Transfer Script

This repository contains a **Python script** that automates **swap** ERC‑20 transfers via **KyberSwap**.

## Features
- Signs and sends each transfer in sequence (safe gas handling)  
- Built‑in retry logic and basic logging  
- Works on most EVM chains supported by KyberSwap  
- Handles multiple‑wallet swap management  
- Low fee

---

## Quick Start

```bash
# 1. Clone repo
git clone https://github.com/yourusername/kyberswap-transfer.git
cd kyberswap-transfer

# 2. Run the setup script
./setup.sh
```

### 3. Configure environment

1. The setup script creates `.env` from `env.example` if it does not already exist.
2. Open `.env` and fill in **all** required keys ([Getting API Keys](#getting-api-keys) below.

### 4. Run

```bash
python main_runner.py
```

---

## Environment Variables

| Var | Description |
|-----|-------------|
| `ALCHEMY_API_KEY` | Your Alchemy HTTP key for the desired network |
| `INFURA_API_KEY`  | (Optional) Your Infura API key |

---

## Getting API Keys

### Alchemy

1. Go to <https://alchemy.com>, sign up (free tier is fine).  
2. Click **“Create App”**, choose the desired chain and network (e.g., `Ethereum Mainnet`).  
3. In the app dashboard, copy the **HTTP API URL**—the long URL ends with something like `.../v2/ALCHEMY_API_KEY`.  
4. Paste the value after the last slash (`ALCHEMY_API_KEY`) into your `.env`:

   ```env
   ALCHEMY_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

### Infura

1. Visit <https://infura.io>, create an account, and make a **New Project**.  
2. Select the network (e.g., Mainnet) under **Endpoints**.  
3. Copy the **HTTPS URL**—it contains your project ID at the end (after `/v3/`).  
4. Put that ID in your `.env`:

   ```env
   INFURA_API_KEY=yyyyyyyyyyyyyyyyyyyyyyyyyyyyy
   ```

---

## Contracts

* KyberSwap represents the native token with the special address  
  `0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE`.  
  The router swaps this to the true native token behind the scenes.  
* You can specify token addresses manually via CLI **or** list them in  
  `/resources/<chain_name>/token_kyber.txt` (one `address,symbol` per line).

---

## Wallets

You can supply wallets interactively via CLI, or maintain a default list in  
`/resources/wallet.txt`.

---

## Contributing

Pull requests are welcome—open an issue first to discuss changes.

MIT License
