# 🏥 FL Client Setup Guide

This guide helps you set up an FL client at your hospital to participate in federated training.

---

## 📋 Requirements

- **NVIDIA GPU** with drivers installed
- **Docker** with NVIDIA Container Toolkit (or Python 3.8+)
- **Network access** to the central server (port 8081)

---

## 🚀 Quick Start with Docker

### Step 1: Get the code

```bash
git clone https://github.com/omarsafi3/xray_classification.git
cd xray_classification/python
```

### Step 2: Configure

```bash
# Create config file
cp .env.client.example .env

# Edit the file
nano .env
```

Set these values in `.env`:
```
FL_SERVER_ADDRESS=YOUR_SERVER_IP:8081
DATASET_PATH=/path/to/your/xray/images
```

### Step 3: Run

```bash
docker compose -f docker-compose.client.yml up
```

**Done!** The client will connect to the server and start training.

---

## 🐍 Quick Start with Python

```bash
# Install dependencies
pip install -r requirements.txt

# Run
export FL_SERVER_ADDRESS=YOUR_SERVER_IP:8081
python client.py --dataset_path /path/to/your/xray/images
```

---

## 📁 Dataset Format

Organize your X-ray images like this:

```
your_dataset/
├── Covid/
│   └── *.png
├── Normal/
│   └── *.png
├── Pneumonia-Bacterial/
│   └── *.png
└── Pneumonia-Viral/
    └── *.png
```

---

## 🖥️ GPU Setup

### Linux

```bash
# Install NVIDIA Container Toolkit
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
  sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# Test
docker run --rm --gpus all nvidia/cuda:11.0.3-base-ubuntu20.04 nvidia-smi
```

### Windows

1. Install [Docker Desktop](https://docs.docker.com/desktop/install/windows-install/)
2. Enable WSL2 backend
3. Install [NVIDIA drivers](https://www.nvidia.com/Download/index.aspx)
4. GPU works automatically!

---

## 🔧 Troubleshooting

### Can't connect to server

```bash
# Test connection
nc -zv YOUR_SERVER_IP 8081

# If blocked, ask server admin to open port 8081
```

### GPU not detected

```bash
# Check NVIDIA drivers
nvidia-smi

# Check Docker GPU access
docker run --rm --gpus all nvidia/cuda:11.0.3-base-ubuntu20.04 nvidia-smi
```

### Out of GPU memory

Edit `client.py` and reduce `BATCH_SIZE` from 32 to 16 or 8.

---

## 📞 Need Help?

Contact the server administrator or open an issue on GitHub.
