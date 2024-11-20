import socket
import struct
import argparse

def parse_args():
	parser = argparse.ArgumentParser(description='Send WOL packet to host')
	parser.add_argument('-m', '--macaddress', required=True, help='Format: XX:XX:XX:XX:XX:XX')
	parser.add_argument('-b', '--broadcast', required=True, default='192.168.0.255')
	return parser.parse_args()

if __name__ == "__main__":
	args = parse_args()

	mac_address = args.macaddress.replace(args.macaddress[2], '')
	data = ''.join(['FFFFFFFFFFFF', mac_address * 20])  # Pad the synchronization stream.
	send_data = b''
	
	for i in range(0, len(data), 2):  # Split up the hex values and pack.
		send_data = b''.join([send_data, struct.pack('B', int(data[i: i + 2], 16))])
	
	wol_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Broadcast it to the LAN.
	wol_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	wol_sock.sendto(send_data, (args.broadcast, 7))
	
	print(f'WOL packet has been sent to "{args.macaddress}" to turn on host')
