# Linux Command Line Guide

Linux is a Unix-like operating system kernel first released by Linus Torvalds in 1991. It powers servers, desktops, and embedded systems worldwide.

## File System Navigation

### Essential Commands

| Command | Description |
|---------|-------------|
| `pwd` | Print working directory |
| `ls` | List directory contents |
| `cd <dir>` | Change directory |
| `mkdir <dir>` | Create directory |
| `rmdir <dir>` | Remove empty directory |
| `rm -rf <dir>` | Remove directory recursively |
| `cp <src> <dst>` | Copy files |
| `mv <src> <dst>` | Move or rename files |
| `ln -s <target> <link>` | Create symbolic link |

### File Operations

```bash
# View files
cat file.txt       # Display entire file
less file.txt      # View with pagination
head -n 10 file    # First 10 lines
tail -n 10 file    # Last 10 lines

# Search
grep "pattern" file    # Search for pattern
find / -name "*.py"    # Find files by name

# Permissions
chmod 755 script.sh    # Set permissions
chown user:group file  # Change ownership
```

## Process Management

```bash
ps aux              # List all processes
top                 # Real-time process view
htop                # Enhanced process viewer
kill -9 PID         # Force kill process
nohup command &     # Run in background
```

## Networking

```bash
ping host           # Test connectivity
curl http://url     # Make HTTP request
wget http://url     # Download file
netstat -tuln       # List listening ports
ss -tuln            # Modern netstat replacement
ifconfig            # Network interface config
ip addr             # Modern ifconfig replacement
```

## Text Processing

```bash
sed 's/old/new/g' file     # Search and replace
awk '{print $1}' file       # Column extraction
sort file                   # Sort lines
uniq                        # Remove duplicates
wc -l file                  # Count lines
```

## Package Management

### Debian/Ubuntu
- `apt update` — Update package lists
- `apt install <pkg>` — Install package
- `apt upgrade` — Upgrade all packages

### RHEL/Fedora
- `dnf install <pkg>` — Install package

### macOS (Homebrew)
- `brew install <pkg>` — Install package
- `brew update` — Update Homebrew
- `brew upgrade` — Upgrade packages
