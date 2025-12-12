# 🏥 FL Client Setup Guide

This guide is for setting up a **Federated Learning client** at a hospital or data center.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    CENTRAL SERVER                                │
│                 (Cloud / Data Center)                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   MySQL     │  │   Backend   │  │  Frontend   │              │
│  │   :3306     │  │   :8080     │  │   :4200     │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│                          ▲                                       │
│  ┌───────────────────────┴───────────────────────┐              │
│  │              FL Server :8081                   │              │
│  │         (Aggregates model updates)            │              │
│  └───────────────────────┬───────────────────────┘              │
└──────────────────────────┼──────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │  Hospital 1 │ │  Hospital 2 │ │  Hospital 3 │
    │   Client    │ │   Client    │ │   Client    │
    │  (GPU PC)   │ │  (GPU PC)   │ │  (GPU PC)   │
    │ Local Data  │ │ Local Data  │ │ Local Data  │
    └─────────────┘ └─────────────┘ └─────────────┘
```

## Prerequisites

- **Python 3.8+** or **Docker with NVIDIA Container Toolkit**
- **NVIDIA GPU** with CUDA drivers installed
- **NVIDIA Container Toolkit** (for Docker GPU support - see installation below)
- **Network access** to the central FL server (port 8081)
- **Local X-ray dataset** in the correct format

### Install NVIDIA Container Toolkit (Linux)

```bash
# Add NVIDIA repo
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# Install
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit

# Configure Docker
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# Test GPU access in Docker
docker run --rm --gpus all nvidia/cuda:11.0.3-base-ubuntu20.04 nvidia-smi
```

### Windows Setup

**Option 1: Docker Desktop with WSL2 (Recommended)**
1. Install [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
2. Enable **WSL2 backend** in Docker Desktop → Settings → General
3. Install [NVIDIA drivers for Windows](https://www.nvidia.com/Download/index.aspx)
4. GPU support works automatically with Docker Desktop + WSL2

```powershell
# Test GPU access
docker run --rm --gpus all nvidia/cuda:11.0.3-base-ubuntu20.04 nvidia-smi
```

**Option 2: Native Python on Windows (No Docker)**
```powershell
# 1. Install Miniconda from https://docs.conda.io/en/latest/miniconda.html

# 2. Open Anaconda Prompt and create environment
conda create -n xray_client python=3.8
conda activate xray_client

# 3. Install dependencies
pip install tensorflow==2.15.0 flwr numpy pillow

# 4. Clone repo and run client
git clone https://github.com/omarsafi3/xray_classification.git
cd xray_classification\python

$env:FL_SERVER_ADDRESS="<SERVER_IP>:8081"
python client.py --dataset_path C:\path\to\your\dataset
```

## Dataset Format

Your local dataset should be structured like this:

```
/path/to/dataset/
├── Covid/
│   ├── image001.png
│   ├── image002.png
│   └── ...
├── Normal/
│   ├── image001.png
│   └── ...
├── Pneumonia-Bacterial/
│   ├── image001.png
│   └── ...
└── Pneumonia-Viral/
    ├── image001.png
    └── ...
```

## Setup Options

### Option 1: Run Directly with Python - Linux/macOS

```bash
# 1. Clone the repository
git clone https://github.com/omarsafi3/xray_classification.git
cd xray_classification/python

# 2. Create virtual environment
conda create -n xray_client python=3.8
conda activate xray_client

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the client
export FL_SERVER_ADDRESS=<SERVER_IP>:8081
python client.py --dataset_path /path/to/your/dataset
```

### Option 2: Run Directly with Python - Windows

```powershell
# 1. Clone the repository
git clone https://github.com/omarsafi3/xray_classification.git
cd xray_classification\python

# 2. Create virtual environment (using Anaconda Prompt)
conda create -n xray_client python=3.8
conda activate xray_client

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the client
$env:FL_SERVER_ADDRESS="<SERVER_IP>:8081"
python client.py --dataset_path C:\path\to\your\dataset
```

### Option 3: Run with Docker - Linux (Recommended for Production)

```bash
# 1. Clone the repository
git clone https://github.com/omarsafi3/xray_classification.git
cd xray_classification/python

# 2. Build the Docker image
docker build -t xray-fl-client -f Dockerfile .

# 3. Run the client with GPU
docker run --gpus all \
  -e FL_SERVER_ADDRESS=<SERVER_IP>:8081 \
  -v /path/to/your/dataset:/data:ro \
  xray-fl-client --dataset_path /data
```

> **Note**: If testing on the same machine as the server, use `172.17.0.1:8081` as the server address (Docker bridge network IP).

### Option 4: Run with Docker - Windows (Docker Desktop + WSL2)

```powershell
# 1. Clone the repository
git clone https://github.com/omarsafi3/xray_classification.git
cd xray_classification\python

# 2. Build the Docker image
docker build -t xray-fl-client -f Dockerfile .

# 3. Run the client with GPU
docker run --gpus all `
  -e FL_SERVER_ADDRESS=<SERVER_IP>:8081 `
  -v C:\path\to\your\dataset:/data:ro `
  xray-fl-client --dataset_path /data
```

> **Note**: Windows uses backticks (`) for line continuation instead of backslashes.

### Option 5: Use Docker Compose (Easiest)

```bash
# 1. Copy the client docker-compose
cd xray_classification/python
cp docker-compose.client.yml docker-compose.yml

# 2. Edit the .env file
cp .env.client.example .env
nano .env  # Set your server IP and data path

# 3. Run
docker compose up
```

## Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `FL_SERVER_ADDRESS` | Central FL server address | `192.168.1.100:8081` or `fl.example.com:8081` |
| `DATASET_PATH` | Path to local dataset | `/home/user/xray_data` |

### Testing Connection

Before training, verify you can reach the FL server:

```bash
# Test network connectivity
nc -zv <SERVER_IP> 8081

# Or with telnet
telnet <SERVER_IP> 8081
```

## Training Process

1. **Client starts** and loads local dataset
2. **Connects to FL server** at the specified address
3. **Receives global model** from server
4. **Trains locally** for 2 epochs on local data
5. **Sends model updates** (weights) back to server
6. **Server aggregates** updates from all clients
7. **Repeat** for N rounds

> ⚠️ **Privacy**: Only model weights are sent to the server. Your raw data never leaves your machine!

## Troubleshooting

### Connection Refused
```
Error: Connection to <SERVER_IP>:8081 refused
```
- Check if the server is running: `docker-compose logs fl-server`
- Check firewall on server: `sudo ufw status`
- Verify port is open: `sudo ufw allow 8081/tcp`

### CUDA Out of Memory
```
Error: CUDA out of memory
```
- Reduce batch size in client.py (default: 32)
- Close other GPU applications

### Dataset Not Found
```
Error: Dataset path does not exist
```
- Verify the path exists: `ls /path/to/dataset`
- Check folder structure has the 4 class folders

## Contact

If you need help setting up a client, contact the system administrator.
