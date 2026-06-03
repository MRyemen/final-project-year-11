#Authert: Dvir Zilber


import socket
import threading

server_ip = "127.0.0.1"
port = 48674

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server_ip, port))
except socket.error as e:
    print(str(e))

s.listen(2)
print("Server Started. Waiting for a connection...")

player_positions = ["100,420,6,0", "650,420,6,0"]
connected_players = 0  # NEW: Track how many players have joined


def threaded_client(conn, player_index):
    global connected_players
    conn.send(str.encode(str(player_index)))

    while True:
        try:
            data = conn.recv(2048).decode('utf-8')
            if not data:
                break
            else:
                player_positions[player_index] = data
                other_player = 1 if player_index == 0 else 0

                # NEW: Add the connected_players count to the end of the data string!
                reply = player_positions[other_player] + f",{connected_players}"
                conn.sendall(str.encode(reply))
        except:
            break

    print(f"Lost connection to Player {player_index + 1}")
    connected_players -= 1  # NEW: Subtract if they leave
    conn.close()


current_player = 0
while True:
    conn, addr = s.accept()
    print("Connected to:", addr)
    connected_players += 1  # Add 1 when someone connects

    # NEW: Force the ID to only ever be 0 or 1, even if you restart players!
    if current_player % 2 == 0:
        id_to_give = 0
    else:
        id_to_give = 1
    thread = threading.Thread(target=threaded_client, args=(conn, id_to_give))
    thread.start()
    current_player += 1