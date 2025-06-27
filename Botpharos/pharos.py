import os, random, time, threading, sys, platform
from datetime import datetime
from dotenv import load_dotenv
from web3 import Web3
from eth_account import Account
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.table import Table
import requests

if platform.system() != "Windows":
    import select

load_dotenv()
console = Console()

RPC = "https://testnet.dplabs-internal.com"
CHAIN_ID = 688688
web3 = Web3(Web3.HTTPProvider(RPC))
TOKENS = {
    "WPHRS": web3.to_checksum_address("0x76aaada469d23216be5f7c596fa25f282ff9b364"),
    "USDC":  web3.to_checksum_address("0xad902cf99c2de2f1ba5ec4d642fd7e49cae9ee37"),
    "USDT":  web3.to_checksum_address("0xed59de2d7ad9c043442e381231ee3646fc3c2939"),
    "ROUTER": web3.to_checksum_address("0x0d13198F17cF160D432F862262eA72E7D43c3c8d")
}
PRIVATE_KEYS = [os.getenv("PRIVATE_KEY_1")]

USDT_DECIMALS = 6
tx_count = {"SWAP": 0, "WRAP": 0, "AIRDROP": 0, "LP": 0}
logs = []
start_time = time.time()
nonces = {}

def get_nonce_managed(address):
    if address not in nonces:
        nonces[address] = web3.eth.get_transaction_count(address, 'pending')
    else:
        nonces[address] += 1
    return nonces[address]

def get_random_delay():
    return random.uniform(7, 15)

def log(text, is_error=False):
    now = datetime.now().strftime("%H:%M:%S")
    line = f"[red][{now}] {text}[/red]" if is_error else f"[green][{now}] {text}[/green]"
    logs.append(line)
    if len(logs) > 20:
        logs.pop(0)
    with open("tx_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{now}] {text}\n")

def send_and_wait(tx_signed):
    try:
        tx_hash = web3.eth.send_raw_transaction(tx_signed.raw_transaction)
        log(f"[cyan]⏳ Waiting for confirmation...[/cyan]")
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        if receipt["status"] == 1:
            log(f"[green]✅ TX Success: {tx_hash.hex()}[/green]")
            return tx_hash
        else:
            log(f"[red]❌ TX Failed: {tx_hash.hex()}[/red]", is_error=True)
            return None
    except Exception as e:
        log(f"[red]❌ TX Error: {e}[/red]", is_error=True)
        return None

# === TX Functions ===
def wrap(acct):
    try:
        val_eth = random.uniform(0.001, 0.003)
        val = web3.to_wei(val_eth, "ether")
        abi = [{"name": "deposit", "type": "function", "inputs": [], "outputs": [], "stateMutability": "payable"}]
        c = web3.eth.contract(address=TOKENS["WPHRS"], abi=abi)
        tx = c.functions.deposit().build_transaction({
            "from": acct.address,
            "value": val,
            "gas": 100000,
            "gasPrice": web3.to_wei(1, "gwei"),
            "nonce": get_nonce_managed(acct.address),
            "chainId": CHAIN_ID
        })
        signed = acct.sign_transaction(tx)
        tx_hash = send_and_wait(signed)
        if tx_hash:
            tx_count["WRAP"] += 1
            log(f"💰 Wrapped {val_eth:.5f} PHRS | {tx_hash.hex()}")
    except Exception as e:
        log(f"[WRAP ERROR] {e}", is_error=True)

def approve(acct, token, spender):
    try:
        abi = [{"name": "approve", "type": "function", "inputs": [
            {"name": "spender", "type": "address"},
            {"name": "amount", "type": "uint256"}], "outputs": [{"name": "", "type": "bool"}]}]
        c = web3.eth.contract(address=token, abi=abi)
        tx = c.functions.approve(spender, 2**256-1).build_transaction({
            "from": acct.address,
            "gas": 60000,
            "gasPrice": web3.to_wei(1, "gwei"),
            "nonce": get_nonce_managed(acct.address),
            "chainId": CHAIN_ID
        })
        signed = acct.sign_transaction(tx)
        send_and_wait(signed)
    except Exception as e:
        log(f"[APPROVE ERROR] {e}", is_error=True)

def swap(acct, token_in, token_out):
    try:
        approve(acct, token_in, TOKENS["ROUTER"])
        amount_eth = random.uniform(0.00005, 0.0002)
        amount = web3.to_wei(amount_eth, "ether")
        abi = [{
            "name": "exactInputSingle", "type": "function",
            "inputs": [{"name": "params", "type": "tuple", "components": [
                {"name": "tokenIn", "type": "address"},
                {"name": "tokenOut", "type": "address"},
                {"name": "fee", "type": "uint24"},
                {"name": "recipient", "type": "address"},
                {"name": "deadline", "type": "uint256"},
                {"name": "amountIn", "type": "uint256"},
                {"name": "amountOutMinimum", "type": "uint256"},
                {"name": "sqrtPriceLimitX96", "type": "uint160"}]}],
            "outputs": [{"name": "amountOut", "type": "uint256"}]
        }]
        c = web3.eth.contract(address=TOKENS["ROUTER"], abi=abi)
        params = (token_in, token_out, 3000, acct.address, int(time.time())+600, amount, 0, 0)
        tx = c.functions.exactInputSingle(params).build_transaction({
            "from": acct.address,
            "gas": 300000,
            "gasPrice": web3.to_wei(1, "gwei"),
            "nonce": get_nonce_managed(acct.address),
            "chainId": CHAIN_ID
        })
        signed = acct.sign_transaction(tx)
        tx_hash = send_and_wait(signed)
        if tx_hash:
            tx_count["SWAP"] += 1
            log(f"🔁 Swap {token_in[-4:]} → {token_out[-4:]} | {amount_eth:.6f} PHRS | {tx_hash.hex()}")
    except Exception as e:
        log(f"[SWAP ERROR] {e}", is_error=True)

def phrs_transfer(acct):
    try:
        to = Account.create().address
        amount_phrs = random.uniform(0.001, 0.005)
        value = web3.to_wei(amount_phrs, "ether")

        balance = web3.eth.get_balance(acct.address)
        if balance < value + web3.to_wei(0.0001, "ether"):
            log(f"[yellow]⚠️ Skip PHRS transfer. Not enough balance for {amount_phrs:.4f} PHRS[/yellow]")
            return

        tx = {
            "to": to,
            "value": value,
            "gas": 21000,
            "gasPrice": web3.to_wei(1, "gwei"),
            "nonce": get_nonce_managed(acct.address),
            "chainId": CHAIN_ID
        }

        signed_tx = acct.sign_transaction(tx)
        tx_hash = send_and_wait(signed_tx)
        if tx_hash:
            tx_count["AIRDROP"] += 1
            log(f"🎯 PHRS Transfer: {amount_phrs:.4f} PHRS → {to[:6]}... | {tx_hash.hex()}")
    except Exception as e:
        log(f"[AIRDROP ERROR] {e}", is_error=True)

def lp_sim(acct):
    tx_count["LP"] += 1
    log("📈 Simulated LP mint WPHRS/USDC")

# === UI ===
def render_ui(acct):
    layout = Layout()
    layout.split(Layout(name="header", size=5), Layout(name="body"))
    layout["body"].split_row(Layout(name="left", size=40), Layout(name="right"))
    run_time = time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time))
    total_tx = sum(tx_count.values())

    header_grid = Table.grid(expand=True)
    header_grid.add_column(justify="left")
    header_grid.add_column(justify="right")
    header_grid.add_row(
        "[bold cyan]Pharos Bot Auto Tx[/bold cyan]\n[white]By : Ajoika_Feb @CTeam[/white]",
        "[green]Bot otomatis untuk transaksi di jaringan Testnet Pharos\n(Q untuk berhenti)[/green]"
    )
    header_panel = Panel(header_grid, title="🚀", border_style="bright_magenta")
    layout["header"].update(header_panel)

    info = Table.grid(padding=(0,1))
    info.add_column(justify="left")
    info.add_row(f"[bold cyan]Wallet:[/bold cyan] {acct.address}")
    info.add_row(f"[green]✔ Wrap:[/green] {tx_count['WRAP']}")
    info.add_row(f"[cyan]✔ Swap:[/cyan] {tx_count['SWAP']}")
    info.add_row(f"[magenta]✔ PHRS Transfers:[/magenta] {tx_count['AIRDROP']}")
    info.add_row(f"[blue]✔ LP:[/blue] {tx_count['LP']}")
    info.add_row(f"[bold yellow]⭐ Total TX:[/bold yellow] {total_tx}")
    info.add_row(f"[yellow]⏱ Running:[/yellow] {run_time}")
    layout["left"].update(Panel(info, title="📊 [bold green]Status[/bold green]", border_style="bright_green"))

    log_panel = Table.grid()
    for line in logs:
        log_panel.add_row(line)
    layout["right"].update(Panel(log_panel, title="🧾 [bold cyan]Log[/bold cyan]", border_style="bright_cyan"))

    return layout

# === Runner ===
def bot_runner(acct):
    while True:
        wrap(acct)
        swap(acct, TOKENS["WPHRS"], TOKENS["USDC"])
        swap(acct, TOKENS["USDC"], TOKENS["WPHRS"])
        phrs_transfer(acct)
        lp_sim(acct)
        wait_time = get_random_delay()
        log(f"[yellow]⏳ Next cycle in {wait_time:.1f}s...[/yellow]")
        time.sleep(wait_time)

def main():
    with open("tx_log.txt", "w", encoding="utf-8") as f:
        f.write("")
    for key in PRIVATE_KEYS:
        if not key: continue
        acct = Account.from_key(key)
        log(f"🔐 Wallet: {acct.address}")
        thread = threading.Thread(target=bot_runner, args=(acct,))
        thread.start()
        with Live(render_ui(acct), refresh_per_second=2, screen=True) as live:
            while thread.is_alive():
                live.update(render_ui(acct))
                if platform.system() == "Windows":
                    import msvcrt
                    if msvcrt.kbhit():
                        key = msvcrt.getwch()
                        if key.lower() == "q":
                            log("[red]❌ Bot dihentikan oleh pengguna (Q)[/red]")
                            os._exit(0)
                else:
                    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                        command = sys.stdin.readline().strip()
                        if command.lower() == "q":
                            log("[red]❌ Bot dihentikan oleh pengguna (Q)[/red]")
                            os._exit(0)
                time.sleep(0.5)

if __name__ == "__main__":
    main()
