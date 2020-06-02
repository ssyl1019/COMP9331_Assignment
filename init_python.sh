#! /bin/bash
xterm -hold -title "Peer 2" -e "python3 P2P.py init 2 4 5 30" &
xterm -hold -title "Peer 4" -e "python3 P2P.py init 4 5 8 30" &
xterm -hold -title "Peer 5" -e "python3 P2P.py init 5 8 9 30" &
xterm -hold -title "Peer 8" -e "python3 P2P.py init 8 9 14 30" &
xterm -hold -title "Peer 9" -e "python3 P2P.py init 9 14 19 30" &
xterm -hold -title "Peer 14" -e "python3 P2P.py init 14 19 2 30" &
xterm -hold -title "Peer 19" -e "python3 P2P.py init 19 2 4 30" &
