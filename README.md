# 🎮 Snake Battle Arena

A real-time multiplayer Snake game that you can host on your computer and play with friends across the network!

## 🚀 Quick Start

### Option 1: Run the Executable (Easiest)
1. Double-click `SnakeBattleArena.exe` (if you have the built version)
2. The game server will start and your browser will open automatically
3. Share the network URL with friends to play together!

### Option 2: Run from Source Code
1. Double-click `run.bat` to start the server
2. Or manually run: `python launcher.py`

### Option 3: Build Your Own Executable
1. Double-click `build.bat` to create the executable
2. The executable will be created in the `dist` folder
3. You can then share the `dist` folder with others

## 🎯 How to Play

### Single Player
- Use **Arrow Keys** or **WASD** to control your snake
- Eat the red food to grow and score points
- Avoid hitting walls or your own tail

### Multiplayer
1. One person starts the server (host)
2. Host shares their network IP address with friends
3. Friends open the network URL in their browsers
4. Create or join game rooms using room IDs
5. Up to 4 players can play in each room
6. Last snake standing wins!

## 🌐 Network Setup

### For the Host:
- Start the game server
- Note the **Network access URL** shown in the console
- Share this URL with friends (e.g., `http://192.168.1.100:5000`)

### For Players:
- Open the network URL in any web browser
- Enter your name and join a room
- Use arrow keys or WASD to play

## 🔧 Technical Requirements

### To Run from Source:
- Python 3.7 or later
- Internet connection (for initial setup)
- Network connection for multiplayer

### To Run Executable:
- Windows 10 or later
- Network connection for multiplayer

## 🛠️ Building the Executable

To create a standalone executable:

```bash
# Install dependencies
pip install -r requirements.txt

# Build the executable
pyinstaller snake_game.spec --clean

# Or simply run:
build.bat
```

The executable will be created in the `dist` folder and can be run on any Windows computer without Python installed.

## 🔒 Firewall & Network Notes

- The server runs on port 5000
- Make sure this port isn't blocked by your firewall
- All players must be on the same local network (WiFi/LAN)
- For internet play, you'll need to configure port forwarding on your router

## 🎮 Game Features

- **Real-time multiplayer** - Up to 4 players per room
- **Beautiful modern UI** - Responsive design with smooth animations
- **Game lobbies** - Create and join rooms with unique IDs
- **Live scoreboard** - Real-time score tracking
- **Cross-platform** - Works on any device with a web browser
- **No installation required** - Players just need a web browser

## 🐛 Troubleshooting

### Players Can't Connect:
- Check if the host's firewall is blocking port 5000
- Ensure all players are on the same network
- Try using the host's actual IP address instead of localhost

### Game Runs Slowly:
- Close other applications to free up resources
- Check network connection quality
- Reduce the number of players if experiencing lag

### Server Won't Start:
- Make sure port 5000 isn't already in use
- Check if Python is properly installed (for source version)
- Try running as administrator

## 📝 License

This is a free, open-source game. Feel free to modify and share!

---

**Enjoy playing Snake Battle Arena! 🐍🎮**
