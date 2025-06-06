
"""
RFM9x Node Simulation Script
=============================

This script runs a simulated RFM9x LoRa node that can act as a transmitter, receiver, or both.
It connects to the central LoRa simulation server and exchanges packets based on configured parameters.

Usage:
------
Start a receiver node:
    python3 rfm9x_simulation_node.py --simulate --id=1 --location=0,0 --mode=rx

Start a transmitter node (sends a message every 2s, sends data to node 1):
    python3 rfm9x_simulation_node.py --simulate --id=2 --location=1,1 --mode=tx --interval=2 --destination=1

Start a transmitter node (sends a message every 2s, sends data to all nodes):
    python3 rfm9x_simulation_node.py --simulate --id=2 --location=1,1 --mode=tx --interval=2 --broadcast

"""

import argparse
import time
from simulated_rfm9x import SimulatedRFM9x

# ========================== CONFIGURABLE DEFINES ==========================
MESSAGE = "Hello"
TX_POWER = 23  # dBm
# ==========================================================================

def run_tx(rfm9x, interval=5, broadcast=True):
    """
    Transmit MESSAGE at given interval. Optionally broadcast to all.
    """
    print(f"[TX-{rfm9x.node}] Starting transmission loop every {interval}s...")
    while True:
        print(f"[TX-{rfm9x.node}] Sending: '{MESSAGE}'")
        rfm9x.send(MESSAGE.encode('utf-8'), destination=0xFF if broadcast else rfm9x.destination)
        time.sleep(interval)

def run_rx(rfm9x):
    """
    Continuously listen for messages.
    """
    print(f"[RX-{rfm9x.node}] Listening for messages...")
    while True:
        msg = rfm9x.receive(timeout=1.0, with_header=True)
        if msg:
            header = msg[:4]
            payload = msg[4:].decode()
            print(f"[RX-{rfm9x.node}] Received: '{payload}' | From: {header[1]} | RSSI: {rfm9x.last_rssi:.2f} | SNR: {rfm9x.last_snr:.2f}")

def main():
    parser = argparse.ArgumentParser(description="Simulated RFM9x Node")
    parser.add_argument("--id", type=int, required=True, help="Node ID")
    parser.add_argument("--location", type=str, default="0,0", help="Node location in km (x,y)")
    parser.add_argument("--mode", choices=["tx", "rx"], required=True, help="Node mode: transmitter or receiver")
    parser.add_argument("--interval", type=float, default=5.0, help="Transmission interval in seconds")
    parser.add_argument("--broadcast", action="store_true", help="Enable broadcast mode for TX")
    parser.add_argument("--destination", type=int, help="Destination Node ID for unicast")
    parser.add_argument("--frequency", type=float, default=915.0, help="Communication frequency of the Node")

    args = parser.parse_args()

    # Enforce mutual exclusivity between destination and broadcast
    if args.mode == "tx":
        if not args.destination and not args.broadcast:
            parser.error("Transmitter mode requires either --destination or --broadcast")
        if args.destination and args.broadcast:
            parser.error("Provide only one of --destination or --broadcast")
    if not args.id:
        parser.error('Please provide node id --id')

    # Parse location
    x, y = map(float, args.location.split(","))
    location = (x, y)

    try:
        rfm9x = SimulatedRFM9x()
        rfm9x.tx_power = TX_POWER
        rfm9x.node = args.id
        rfm9x.destination = args.destination if args.destination else 0XFF
        rfm9x.location = location
        rfm9x.frequency = args.frequency
        rfm9x.enable_crc = False
        rfm9x.initialize()

        if args.mode == "tx":
            run_tx(rfm9x, interval=args.interval, broadcast=args.broadcast)
        else:
            run_rx(rfm9x)
    except ConnectionRefusedError:
        print("[X ERROR] Please run simulated_server.py file first.")

if __name__ == "__main__":
    main()
