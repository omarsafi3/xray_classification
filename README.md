# 🩺 X-ray Classification System

A **Federated Learning-based medical image classification system** for detecting respiratory conditions from chest X-ray images. The system classifies X-rays into four categories: **COVID-19**, **Normal**, **Bacterial Pneumonia**, and **Viral Pneumonia**.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15-orange.svg)
![Spring Boot](https://img.shields.io/badge/Spring%20Boot-3.5-green.svg)
![Flower](https://img.shields.io/badge/Flower-Federated%20Learning-purple.svg)

## 🏗️ Architecture Overview

This is a **distributed federated learning system**. The server runs centrally, and clients run on separate machines at different hospitals.

```
                         ☁️ CENTRAL SERVER (Cloud/Data Center)
┌─────────────────────────────────────────────────────────────────┐
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   MySQL     │  │   Backend   │  │  Frontend   │              │
│  │   :3306     │  │   :8080     │  │   :4200     │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
│                          ▲                                       │
│  ┌───────────────────────┴───────────────────────┐              │
│  │           FL Server :8081                      │              │
│  │      (Aggregates model updates)               │              │
│  └───────────────────────┬───────────────────────┘              │
└──────────────────────────┼──────────────────────────────────────┘
                           │ Internet/VPN
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
  🏥 Hospital 1      🏥 Hospital 2      🏥 Hospital 3
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  FL Client  │    │  FL Client  │    │  FL Client  │
│  (GPU PC)   │    │  (GPU PC)   │    │  (GPU PC)   │
│ Local Data  │    │ Local Data  │    │ Local Data  │
│ NEVER LEAVES│    │ NEVER LEAVES│    │ NEVER LEAVES│
└─────────────┘    └─────────────┘    └─────────────┘
```

**Privacy**: Raw patient data NEVER leaves the hospital. Only model weights are exchanged!

## ✨ Features

- **Federated Learning**: Train models across distributed data sources without sharing sensitive patient data
- **SE-ResNet50V2 Model**: Custom architecture with Squeeze-and-Excitation blocks for improved feature extraction
- **GradCAM Heatmaps**: Visual explanations highlighting regions influencing predictions
- **JWT Authentication**: Secure REST API with token-based authentication
- **Real-time Metrics**: Track training progress (accuracy, loss, sensitivity, specificity) per round
- **Model Versioning**: Automatic saving of best-performing models

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **ML Framework** | TensorFlow 2.15 / Keras |
| **Federated Learning** | Flower (flwr) |
| **Backend API** | Spring Boot 3.5.3 (Java 17) |
| **Database** | MySQL 8 |
| **Authentication** | JWT (JSON Web Tokens) |
| **Containerization** | Docker |

## 📦 Prerequisites

### Central Server
- **Docker & Docker Compose**
- **Public IP or domain** accessible by clients
- **Open port 8081** for FL clients

### Client Machines (Hospitals)
- **Python 3.8+** or **Docker with NVIDIA Container Toolkit**
- **NVIDIA GPU** with drivers installed
- **NVIDIA Container Toolkit** (for Docker GPU support)
- **Network access** to central server port 8081

#### Install NVIDIA Container Toolkit (Linux)
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

# Test
docker run --rm --gpus all nvidia/cuda:11.0.3-base-ubuntu20.04 nvidia-smi
```

#### Install NVIDIA Container Toolkit (Windows)

**Option 1: Docker Desktop with WSL2 (Recommended)**
1. Install [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
2. Enable WSL2 backend in Docker Desktop settings
3. Install [NVIDIA drivers for Windows](https://www.nvidia.com/Download/index.aspx)
4. GPU support works automatically with Docker Desktop + WSL2

```powershell
# Test GPU access
docker run --rm --gpus all nvidia/cuda:11.0.3-base-ubuntu20.04 nvidia-smi
```

**Option 2: Native Python (No Docker)**
```powershell
# Install Miniconda from https://docs.conda.io/en/latest/miniconda.html

# Create environment
conda create -n xray_client python=3.8
conda activate xray_client

# Install CUDA-enabled TensorFlow
pip install tensorflow[and-cuda]==2.15.0
pip install flwr numpy pillow

# Run client
$env:FL_SERVER_ADDRESS="<SERVER_IP>:8081"
python client.py --dataset_path C:\path\to\dataset
```

---

# 🖥️ Server Setup

## 1. Clone the Repository

```bash
git clone https://github.com/omarsafi3/xray_classification.git
cd xray_classification
```

## 2. Configure Environment

```bash
cp .env.example .env
nano .env  # Edit with your settings
```

## 3. Start Server with Docker Compose

```bash
# Start all server services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f fl-server
```

> **Note**: Use `docker compose` (with space) instead of `docker-compose` for Docker Compose V2.

## 4. Open Firewall for Clients

```bash
# Allow FL clients to connect
sudo ufw allow 8081/tcp
```

## 5. Access the System

| Service | URL |
|---------|-----|
| Frontend | http://your-server-ip:4200 |
| Backend API | http://your-server-ip:8080 |
| FL Server | your-server-ip:8081 (for clients) |

---

# 🏥 Client Setup (At Each Hospital)

Each hospital runs a client that connects to the central server.

## Option 1: Python (Direct)

```bash
# 1. Clone repository
git clone https://github.com/omarsafi3/xray_classification.git
cd xray_classification/python

# 2. Create environment
conda create -n xray_client python=3.8
conda activate xray_client
pip install -r requirements.txt

# 3. Run client (replace SERVER_IP with actual server IP)
export FL_SERVER_ADDRESS=<SERVER_IP>:8081
python client.py --dataset_path /path/to/local/xray/dataset
```

## Option 2: Docker (Recommended)

```bash
# 1. Clone repository
git clone https://github.com/omarsafi3/xray_classification.git
cd xray_classification/python

# 2. Build image
docker build -t xray-fl-client .

# 3. Run client with GPU
docker run --gpus all \
  -e FL_SERVER_ADDRESS=<SERVER_IP>:8081 \
  -v /path/to/local/dataset:/data:ro \
  xray-fl-client --dataset_path /data
```

> **Note**: If running client on the same machine as server, use `172.17.0.1:8081` as the server address.

## Option 3: Docker Compose

```bash
cd xray_classification/python

# Edit .env with your server IP and dataset path
cp .env.client.example .env
nano .env

# Run
docker compose -f docker-compose.client.yml up
```

See [python/README_CLIENT.md](python/README_CLIENT.md) for detailed client setup instructions.

---

## 📁 Project Structure

```
xray_classification/
├── python/
│   ├── server.py          # Federated Learning server with custom aggregation
│   ├── client.py          # FL client for distributed training
│   ├── heatmap.py         # GradCAM visualization for predictions
│   ├── requirements.txt   # Python dependencies
│   ├── Dockerfile         # GPU-enabled container for FL clients
│   ├── Dockerfile.server  # Container for FL server
│   └── saved_models/      # Trained model checkpoints
│
├── xray_classification_backend/
│   ├── Dockerfile         # Spring Boot container
│   ├── src/main/java/com/example/xray_classification_backend/
│   │   ├── controller/
│   │   │   ├── AuthController.java       # Login/Register endpoints
│   │   │   ├── HeatmapController.java    # Prediction with GradCAM
│   │   │   ├── GlobalMetricsController.java  # Training metrics
│   │   │   └── DownloadController.java   # File downloads
│   │   ├── model/
│   │   │   ├── User.java
│   │   │   ├── GlobalMetrics.java
│   │   │   └── HeatmapEntity.java
│   │   ├── security/
│   │   │   ├── JwtUtil.java
│   │   │   ├── AuthTokenFilter.java
│   │   │   └── AuthEntryPointJwt.java
│   │   └── config/
│   │       ├── WebSecurityConfig.java
│   │       └── WebConfig.java
│   └── src/main/resources/
│       └── application.properties
│
├── docker-compose.yml     # Orchestrates all services
├── .env.example           # Environment variables template
└── README.md

xray_classification_front/ (separate repo)
├── src/app/
│   ├── login/             # JWT authentication
│   ├── signup/            # User registration
│   ├── upload-image/      # X-ray upload & prediction
│   ├── global-metrics-list/  # Training metrics dashboard
│   ├── fl-client/         # FL client management
│   └── services/          # API services
├── Dockerfile             # Angular production container
└── nginx.conf             # Nginx reverse proxy config
```

## 🔌 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/signup` | Register new user |
| POST | `/api/v1/auth/signin` | Login and get JWT token |

### Predictions
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/heatmap/predict` | Upload X-ray and get prediction + heatmap |
| POST | `/api/v1/heatmap/upload` | Save heatmap with prediction |

### Metrics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/model/metrics/all` | Get all training metrics |
| GET | `/api/v1/model/metrics/latest` | Get latest training metrics |
| POST | `/api/v1/model/metrics/save` | Save new metrics (called by FL server) |

## ⚙️ Configuration Reference

### Server Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_PASSWORD` | MySQL database password | `0000` |
| `JWT_SECRET` | Secret key for JWT signing | (default key) |
| `TEST_DATA_PATH` | Path to central test dataset | `test` |
| `MODEL_SAVE_DIR` | Directory for model checkpoints | `saved_models` |
| `PYTHON_EXECUTABLE` | Path to Python interpreter | `python` |
| `PYTHON_HEATMAP_SCRIPT` | Path to heatmap.py | `python/heatmap.py` |
| `BACKEND_URL` | Backend API URL (for FL server) | `http://localhost:8080` |

### Client Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `FL_SERVER_ADDRESS` | Central FL server address | `192.168.1.100:8081` |
| `DATASET_PATH` | Path to local training data | `/data/xray_images` |

### application.properties

```properties
# Database
spring.datasource.url=jdbc:mysql://localhost:3306/xray_metrics
spring.datasource.username=root
spring.datasource.password=${DB_PASSWORD:0000}

# JWT
jwt.secret=${JWT_SECRET:your-secret-key}
jwt.expiration=3600000

# Python Integration
python.executable.path=${PYTHON_EXECUTABLE:python}
python.heatmap.script.path=${PYTHON_HEATMAP_SCRIPT:python/heatmap.py}
```

## 🧠 Model Architecture

The system uses a custom **SE-ResNet50V2** architecture:

- **Base**: ResNet50V2 pretrained on ImageNet
- **Enhancement**: Squeeze-and-Excitation (SE) blocks for channel attention
- **Output**: 4-class softmax (COVID-19, Normal, Bacterial Pneumonia, Viral Pneumonia)

### Training Metrics
- **Accuracy**: Overall classification accuracy
- **Sensitivity**: True positive rate (recall)
- **Specificity**: True negative rate

## 🐳 Docker Services

### Server-Side Services (Central Machine)

| Service | Port | Description |
|---------|------|-------------|
| `frontend` | 4200 | Angular web UI |
| `backend` | 8080 | Spring Boot REST API |
| `fl-server` | 8081 | Flower FL aggregation server |
| `mysql` | 3306 | MySQL database |

### Server Commands

```bash
# Start all server services
docker compose up -d

# View service logs
docker compose logs -f backend
docker compose logs -f fl-server

# Stop all services
docker compose down

# Stop and remove all data (clean start)
docker compose down -v
```

### Client-Side (Hospital Machines)

Each hospital runs a client container that connects to the central server:

```bash
cd python

# With Docker Compose
docker compose -f docker-compose.client.yml up

# Or direct Docker with GPU
docker run --gpus all \
  -e FL_SERVER_ADDRESS=<SERVER_IP>:8081 \
  -v /path/to/local/data:/data:ro \
  xray-fl-client --dataset_path /data
```

> **Local Testing**: Use `172.17.0.1:8081` as `FL_SERVER_ADDRESS` when running client on the same machine as server.

## 📊 Dataset Structure

Expected format for training/test data:

```
dataset/
├── Covid/
│   ├── image1.png
│   └── ...
├── Normal/
│   ├── image1.png
│   └── ...
├── Pneumonia-Bacterial/
│   ├── image1.png
│   └── ...
└── Pneumonia-Viral/
    ├── image1.png
    └── ...
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is for educational and research purposes.

## 👥 Authors

- **Omar Safi** - [GitHub](https://github.com/omarsafi3)
- **Fatma Rekik** - [Github](https://github.com/Fatma-R)

---

<p align="center">
  Made with ❤️ for advancing medical AI research
</p>