# Gameplay logic:
- Invalid action (shoot at no bullet, grenade at no grenade, reload at > 0 bullet) -> action registers but no damage
- shield action always processed last

# To setup:
- Create a .env file. Then fill in the following details in `<>` and copy it to your `.env` file. template is provided in the `.env_sample` file too

```
XILINX_HOST = '<xilinx_ip>'
XILINX_PWD = '<xilinx_password>'
SUNFIRE_USER = '<stu_username>'
SUNFIRE_PWD = '<stu_password>'
```
- DONT USE PORT NUM < 2000

# To run:
0. Connect and run visualizer
1. ssh to stu account:
- `ssh username@stu.comp.nus.edu.sg`
2. ssh to xilinx:
- `ssh xilinx@192.168.246`
3. Run Eval code:
- `python eval_sever/eval_server.py <local_port> <group_num> <player_num>`
- Secret key: `1234567890123456`
4. Run ultra96 code:
- `sudo -i`
- `cd /home/xilinx`
- `python u96_modules/main.py <group_id> <eval_server_port> <eval_server_ip> <secret_key>`
5. Run relay laptop code: (can choose to run on different or same laptop)
- laptop 1: `python3 laptop_p1.py <local_port> <remote_u96_port> <group_id>`
- laptop 2: `python3 laptop_p2.py <local_port> <remote_u96_port> <group_id>`
6. Connect all hardware and pray it works! :pray:

# To kill proces in port: 
- fuser -k 10000/tcp 
- fuser -k 9000/tcp 
- fuser -k 8000/tcp

# Start virtual env
- `source <virtual_env_name>/bin/activate`
- `python3 eval_server.py <PORT> <GROUP_ID> <NUM_PLAYERS>`

# Eval Server details (provided at start of module)

JSON Format:
{
	"p1": Player_1_JSON,
	"p2": Player_2_JSON
}
Player_JSON
{
	"hp":           integer value of current player health,
	"action":       string representing the current action performed by the player
		        Taking values from "grenade, reload, shoot, logout, shield",
	"bullets":      integer value of number of bullets left in the magazine,
	"grenades":     integer value of number of grenades left,
	"shield_time": 	integer value of number of seconds remaining in the shield,
	"shield_health":integer value of amount damage the shield can take,
	"num_deaths":   integer value of number of times the player died,
	"num_shield":   integer value of number of shield left
}

eg:
{
	"p1": {
		"hp": 10,
		"action": "grenade",
		"bullets": 1,
		"grenades": 1,
		"shield_time": 0,
		"shield_health": 3,
		"num_deaths": 1,
		"num_shield": 0
	},
	"p2": {
		"hp": 100,
		"action": "shield",
		"bullets": 2,
		"grenades": 2,
		"shield_time": 1,
		"shield_health": 0,
		"num_deaths": 5,
		"num_shield": 2
	}
}

Packet Format, sent by eval_server: Len_JSON
1) "Len" is the length of "JSON#" sent as plain text
2) "JSON" is the JSON represented as string
3) "Len" and "JSON" are separated by a "_"
Kindly refer the function GameState.send_plaintext in GameState.py for more details.

Packet Format, received by eval_server: Len_crypt(JSON)
1) "Len" is the length of "JSON" sent as plain text
2) "JSON" is the JSON represented as string
3) crypt(JSON) is the AES encrypted form of JSON
4) "Len" and "crypt(JSON)" are separated by a "_"
5) AES encyption mode: CBC
Kindly refer the function Server.recv_game_state and Server.decrypt_message in eval_server.py for more details.

NOTE:
We have conciously avoided commenting our code, except for the "eval_server.py". ;-)
