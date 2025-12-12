# 🩺 X-ray Classification System

A **Federated Learning-based medical image classification system** for detecting respiratory conditions from chest X-ray images.

**Classes**: COVID-19 | Normal | Bacterial Pneumonia | Viral Pneumonia

![Python](https://img.shields.io/badge/Python-3.9-blue.svg)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.11-orange.svg)
![Spring Boot](https://img.shields.io/badge/Spring%20Boot-3.5-green.svg)

---

## 🏗️ How It Works

```
                    ☁️ CENTRAL SERVER
        ┌────────────────────────────────────┐
        │  Frontend  │  Backend  │ FL Server │
        │   :4200    │   :8080   │   :8081   │
        └─────────────────┬──────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
     🏥 Hospital 1   🏥 Hospital 2   🏥 Hospital 3
     [FL Client]     [FL Client]     [FL Client]
     (Data stays     (Data stays     (Data stays
      local!)         local!)         local!)
```

**Privacy**: Patient data NEVER leaves the hospital. Only model updates are shared!

---

# 🚀 Quick Start

## Server Setup (5 minutes)

Run these commands on your **central server**:

```bash
# 1. Clone the project
git clone https://github.com/omarsafi3/xray_classification.git
cd xray_classification

# 2. Create environment file
cp .env.example .env

# 3. Edit .env with your settings (optional)
nano .env

# 4. Start everything
docker compose up -d

# 5. Check it's running
docker compose ps
```

**That's it!** Your server is now running:
- 🌐 **Web App**: http://localhost:4200
- 🔌 **API**: http://localhost:8080
- 🤖 **FL Server**: localhost:8081 (for clients)

### Open Firewall for Remote Clients

```bash
# Allow FL clients to connect
sudo ufw allow 8081/tcp
```

---

## Client Setup (At Each Hospital)

### Option A: Docker (Recommended)

```bash
# 1. Clone the project
git clone https://github.com/omarsafi3/xray_classification.git
cd xray_classification/python

# 2. Create .env file
cp .env.client.example .env

# 3. Edit with your settings
nano .env
# Set FL_SERVER_ADDRESS=YOUR_SERVER_IP:8081
# Set DATASET_PATH=/path/to/your/xray/images

# 4. Run the client
docker compose -f docker-compose.client.yml up
```

### Option B: Python Direct

```bash
# 1. Clone and install
git clone https://github.com/omarsafi3/xray_classification.git
cd xray_classification/python
pip install -r requirements.txt

# 2. Run client
export FL_SERVER_ADDRESS=YOUR_SERVER_IP:8081
python client.py --dataset_path /path/to/your/xray/images
```

---

## 📁 Dataset Format

Your X-ray images should be organized like this:

```
your_dataset/
├── Covid/
│   ├── image1.png
│   └── image2.png
├── Normal/
│   └── ...
├── Pneumonia-Bacterial/
│   └── ...
└── Pneumonia-Viral/
    └── ...
```

---

# 📖 Detailed Documentation

## Server Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_PASSWORD` | MySQL password | `0000` |
| `JWT_SECRET` | JWT signing key | (auto-generated) |
| `MODEL_PATH` | Path to saved models | (see .env.example) |

## Client Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `FL_SERVER_ADDRESS` | Server IP and port | `192.168.1.100:8081` |
| `DATASET_PATH` | Your local dataset | `/data/xray_images` |

---

## 🐳 Docker Commands

### Server

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f

# Stop everything
docker compose down

# Full reset (removes data)
docker compose down -v
```

### Client

```bash
cd python

# Start training
docker compose -f docker-compose.client.yml up

# Stop
docker compose -f docker-compose.client.yml down
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/signup` | Register user |
| POST | `/api/v1/auth/signin` | Login |
| POST | `/api/v1/heatmap/predict` | Upload X-ray for prediction |
| GET | `/api/v1/model/metrics/all` | Get training metrics |

---

## 🖥️ GPU Support (Client)

### Linux
```bash
# Install NVIDIA Container Toolkit
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

### Windows
Use Docker Desktop with WSL2 - GPU support works automatically.

---

## 🔧 Troubleshooting

### Client can't connect to server
```bash
# Check server is running
docker compose ps

# Check port is open
sudo ufw status
sudo ufw allow 8081/tcp

# Test connection from client
nc -zv YOUR_SERVER_IP 8081
```

### GPU not detected
```bash
# Test GPU access
docker run --rm --gpus all nvidia/cuda:11.0.3-base-ubuntu20.04 nvidia-smi
```

### Reset everything
```bash
docker compose down -v
docker compose up -d
```

---

## 👥 Authors

- **Omar Safi** - [GitHub](https://github.com/omarsafi3)
- **Fatma Rekik** - [GitHub](https://github.com/Fatma-R)

---

<p align="center">Made with ❤️ for medical AI research</p>
