import sys
import time
import random
from network import UDPNetwork
from colorama import init, Fore, Style

init(autoreset=True)

PORTS = [5000, 5001, 5002, 5003]

def deploy_update():
    print(f"{Fore.CYAN}- DEPLOYMENT CONSOLE{Style.RESET_ALL}")
    print("Preparing to push Firmware v2.0 to the cluster...")
    
    # Pick a random target to "update" first (Canary deployment style)
    target = random.choice(PORTS)
    
    print(f"Targeting Canary Node: Cell-{target}")
    print("Pushing update package...")
    time.sleep(1)
    
    net = UDPNetwork(4998) # Deployment tool port
    
    # Send the "SABOTAGE" command which now mimics a bad update
    net.send_message(target, 'SABOTAGE', {})
    net.close()
    
    print(f"\n{Fore.GREEN}- Update Pushed.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}⚠️  Monitoring logs for stability...{Style.RESET_ALL}")

if __name__ == "__main__":
    deploy_update()
