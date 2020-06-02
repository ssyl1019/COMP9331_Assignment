# Python Version : 3.6.4

# Just type ./init_python.sh in a terminal to initialize a P2P network.
# Before doing that, you can change the number of the last column to modify the PING_INTERVAL.

# The title of each terminal represents the name of this Peer.

# By executing command of ./join_python.sh, a specific new Peer will be created
# and it will automatically join into the pre-existing network.
# The last two columns of this script represents known pre-existing Peer and PING_INTERVAL.

# Within each terminal named "Peer n",the executable commands are listed here :
	1. quit : to leave the network with notifying other Peers.
	2. store xxxx : xxxx is a number of 4 digits. Info showed in other terminals shows
		the location of this specific file.
	3. request xxxx : xxxx is also a number of 4 digits. The corresponding file will be sent 
		to this Peer. However, all the Peers work in the same dir, which means this peer will
		create a new file named 'received_xxxx'.
		<!-- To test the file sending-receiving progress, I only offered one sample of '4103.pdf'. -->
	4. Ctrl + C is also allowed in the terminals. It raises a KeyboardInterrupt to simulate a
		abruption without notification.
# COMP9331_Assignment
