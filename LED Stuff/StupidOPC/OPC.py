"""(Very) Simple Implementation of Open Pixel Control.

Python Version: 3.6
Source: http://openpixelcontrol.org/
		https://github.com/scanlime/fadecandy/blob/master/doc/fc_protocol_opc.md


Protocol Specification
| Channel | Command | Length               | Data    |
|  -----  |  -----  |         -----        |  ----   |
| 0 - 255 | 0 - 255 | high byte | low byte | n bytes |

"""


import socket
from threading import Timer
from enum import Enum


class Devices(Enum):
	"""Defined devices, to use with sysex."""

	Fadecandy = 1
	Symmetry_Lab = 2


class StupidOPC():
	"""(Very) simple implementation of Open Pixel Control."""

	UDP_PORT = 7890

	def __init__(self, packet_size, targetIP='127.0.0.1', channel=0, command=0):
		"""Class Initialization."""
		# Instance variables
		self.TARGET_IP = targetIP
		self.CHANNEL = self.put_in_range(channel, 0, 255, False)
		self.COMMAND = command
		self.PACKET_SIZE = self.put_in_range(packet_size, 0, 65535, False)
		self.HEADER = bytearray()
		self.BUFFER = bytearray(packet_size)

		# UDP SOCKET
		self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		# Time
		self.fps = 30

		self.make_header()

	def __str__(self):
		"""Printable object state."""
		s = "===================================\n"
		s += "Stupid OPC initialized\n"
		s += "Target IP: {}:{} \n".format(self.TARGET_IP, self.UDP_PORT)
		s += "Channel: {} \n".format(self.CHANNEL)
		s += "Command: {} \n".format(self.COMMAND)
		s += "Packet Size: {} \n".format(self.PACKET_SIZE)
		s += "==================================="

		return s

	def make_header(self):
		"""Make packet header."""
		self.HEADER = bytearray()
		# 0 - channel
		self.HEADER.append(self.CHANNEL)
		# 2 - command
		self.HEADER.append(self.COMMAND)
		# 3 - packet lenght (high byte first)
		p = self.shift_this(self.PACKET_SIZE, True)			# convert to MSB / LSB
		self.HEADER.append(p[0])
		self.HEADER.append(p[1])

	def show(self):
		"""Finally send data."""
		packet = bytearray()
		packet.extend(self.HEADER)
		packet.extend(self.BUFFER)
		try:
			self.s.sendto(packet, (self.TARGET_IP, self.UDP_PORT))
		except Exception as e:
			print("ERROR: Socket error with exception: {}".format(e))

	def close(self):
		"""Close UDP socket."""
		self.s.close()

	##
	# THREADING
	##

	def start(self):
		"""Starts thread clock."""
		self.show()
		self.__clock = Timer((1000.0 / self.fps) / 1000.0, self.start)
		self.__clock.start()

	def stop(self):
		"""Stops thread clock."""
		self.__clock.cancel()

	##
	# SETTERS - HEADER
	##

	def set_channel(self, channel):
		"""Setter for channel value (0 - 255).

		0 is broadcast
		"""
		self.CHANNEL = self.put_in_range(channel, 0, 255, False)
		self.make_header()

	def set_command(self, command):
		"""Setter for command value (0 - 255).

		0   - 8 bit pixel colours
		2   - 16 bit pixel colours
		255 - System exclusive
			- 01 Fadecandy
			- 02 Symmetry Labs
		"""
		self.COMMAND = command
		self.make_header()

	def set_packet_size(self, packet_size):
		"""Setter for packet size (0 - 65535)."""
		self.PACKET_SIZE = self.put_in_range(packet_size, 0, 65535, False)
		self.make_header()

	def set_fps(self, fps):
		"""Setter for desired fps."""
		self.fps = fps

	##
	# SETTERS - DATA
	##

	def clear(self):
		"""Clear DMX buffer."""
		self.BUFFER = bytearray(self.PACKET_SIZE)

	def set(self, p):
		"""Set buffer."""
		if len(self.BUFFER) != self.PACKET_SIZE:
			print("ERROR: packet does not match declared packet size")
			return
		self.BUFFER = p

	def set_single_value(self, address, value):
		"""Set single value in DMX buffer."""
		if address > self.PACKET_SIZE:
			print("ERROR: Address given greater than defined packet size")
			return
		self.BUFFER[address - 1] = value

	def set_single_rem(self, address, value):
		"""Set single value while blacking out others."""
		if address > self.PACKET_SIZE:
			print("ERROR: Address given greater than defined packet size")
			return
		self.clear()
		self.BUFFER[address - 1] = value

	def set_rgb(self, address, r, g, b):
		"""Set 8 bit RGB from start address."""
		if address > self.PACKET_SIZE:
			print("ERROR: Address given greater than defined packet size")
			return
		self.BUFFER[address - 1] = r
		self.BUFFER[address] = g
		self.BUFFER[address + 1] = b

	def set_rgb16(self, address, r, g, b):
		"""Set 16 bit RGB from start address."""
		if address > self.PACKET_SIZE:
			print("ERROR: Address given greater than defined packet size")
			return
		self.BUFFER[address - 1] = r
		self.BUFFER[address] = g
		self.BUFFER[address + 1] = b

	##
	# AUX
	##

	def see_header(self):
		"""Show header values."""
		print(self.HEADER)

	def see_buffer(self):
		"""Show buffer values."""
		print(self.BUFFER)

	def blackout(self):
		"""Sends 0's all across."""
		self.clear()
		self.show()

	def flash_all(self):
		"""Sends 255's all across."""
		packet = bytearray(self.PACKET_SIZE)
		[255 for i in packet]
		self.set(packet)
		self.show()

	##
	# UTILS
	##

	@staticmethod
	def shift_this(number, high_first=True):
		"""Utility method: extracts MSB and LSB from number.

		Args:
		number - number to shift
		high_first - MSB or LSB first (true / false)

		Returns:
		(high, low) - tuple with shifted values

		"""
		low = (number & 0xFF)
		high = ((number >> 8) & 0xFF)
		if (high_first):
			return((high, low))
		else:
			return((low, high))
		print("Something went wrong")
		return False

	@staticmethod
	def put_in_range(number, range_min, range_max, make_even=True):
		"""Utility method: sets number in defined range.

		Args:
		number - number to use
		range_min - lowest possible number
		range_max - highest possible number
		make_even - should number be made even

		Returns:
		number - number in correct range

		"""
		if (number < range_min):
			number = range_min
		if (number > range_max):
			number = range_max
		if (make_even and number % 2 != 0):
			number += 1
		return number


def signal_handler(signal, frame):
	"""Quit gracefully."""
	sys.exit(0)


if __name__ == '__main__':
	import time
	import signal
	import sys

	print("===================================")
	print("Usage Recommendation")

	# add signal handler for SIGINT
	signal.signal(signal.SIGINT, signal_handler)

	# Define settings
	target_ip = '127.0.0.1'         # Address of the OPC Server
	num_leds = 60
	packet_size = num_leds * 3		# typical scenario with RGB leds
	data = bytearray(packet_size)

	# An OPC instance holds a target IP and a buffer of <packet_size>
	o = StupidOPC(packet_size, target_ip)

	# Print shows settings
	print(o)

	# Create and set the whole buffer
	data = [0, 255, 190] * num_leds		# is this some sort of turquoise?
	o.set(data)

	# ... or set single values (address, red value, green value, blue value)
	o.set_rgb(13, 255, 255, 0)			# set pixel 13 to yellow

	# send data once
	o.show()							# data is sent on show()

	# you can also send the data persistently
	o.start()

	time.sleep(3)   					# give it some time for demonstration purpose

	# ...  and update as you go
	o.set_rgb(13, 0, 255, 255)

	time.sleep(3)

	# dont forget to stop sending
	o.stop()

	# ... and close server
	o.close()
