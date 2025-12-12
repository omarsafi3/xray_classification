# 🩺 X-ray Classification System

A **Federated Learning-based medical image classification system** for detecting respiratory conditions from chest X-ray images. The system classifies X-rays into four categories: **COVID-19**, **Normal**, **Bacterial Pneumonia**, and **Viral Pneumonia**.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15-orange.svg)
![Spring Boot](https://img.shields.io/badge/Spring%20Boot-3.5-green.svg)
![Flower](https://img.shields.io/badge/Flower-Federated%20Learning-purple.svg)

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    X-ray Classification System                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   Client 1   │    │   Client 2   │    │   Client N   │       │
│  │  (Hospital)  │    │  (Hospital)  │    │  (Hospital)  │       │
│  │  Local Data  │    │  Local Data  │    │  Local Data  │       │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘       │
│         │                   │                   │                │
│         └───────────────────┼───────────────────┘                │
│                             │                                    │
│                             ▼                                    │
│                   ┌──────────────────┐                          │
│                   │  Flower Server   │                          │
│                   │  (Aggregation)   │                          │
│                   │   Port: 8081     │                          │
│                   └────────┬─────────┘                          │
│                            │                                     │
│                            ▼                                     │
│                   ┌──────────────────┐      ┌──────────────┐    │
│                   │  Spring Boot API │◄────►│    MySQL     │    │
│                   │   Port: 8080     │      │   Database   │    │
│                   └────────┬─────────┘      └──────────────┘    │
│                            │                                     │
│                            ▼                                     │
│                   ┌──────────────────┐                          │
│                   │  Frontend/Client │                          │
│                   │   Application    │                          │
│                   └──────────────────┘                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

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

- **Java 17** or higher
- **Maven 3.8+**
- **Python 3.8+** (Anaconda/Miniconda recommended)
- **MySQL 8.0+**
- **Docker** (optional, for containerized clients)

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/omarsafi3/xray_classification.git
cd xray_classification
```

### 2. Set Up MySQL Database

```sql
CREATE DATABASE xray_metrics;
```

### 3. Set Up Python Environment

```bash
# Using Conda (recommended)
conda create -n xray_env python=3.8
conda activate xray_env
pip install -r python/requirements.txt

# Or using venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r python/requirements.txt
```

### 4. Configure Environment Variables

Create environment-specific configuration:

```bash
# Linux/Mac
export DB_PASSWORD=your_mysql_password
export JWT_SECRET=your_secure_jwt_secret_key
export TEST_DATA_PATH=/path/to/test/dataset
export MODEL_SAVE_DIR=/path/to/saved_models
export PYTHON_EXECUTABLE=/path/to/python
export PYTHON_HEATMAP_SCRIPT=/path/to/python/heatmap.py

# Windows (Command Prompt)
set DB_PASSWORD=your_mysql_password
set TEST_DATA_PATH=C:\path\to\test\dataset
set PYTHON_EXECUTABLE=C:\Users\username\anaconda3\envs\xray_env\python.exe
```

### 5. Build and Run the Spring Boot Backend

```bash
cd xray_classification_backend
mvn clean install
mvn spring-boot:run
```

The API will be available at: `http://localhost:8080`

### 6. Start the Federated Learning Server

```bash
cd python
python server.py
```

The FL server will listen on: `localhost:8081`

### 7. Start Federated Learning Clients

```bash
# Run client with local dataset
python client.py --dataset_path /path/to/client/data

# Or use Docker
docker build -t xray-client .
docker run --gpus all -v /path/to/data:/data xray-client --dataset_path /data
```

## 📁 Project Structure

```
xray_classification/
├── python/
│   ├── server.py          # Federated Learning server with custom aggregation
│   ├── client.py          # FL client for distributed training
│   ├── heatmap.py         # GradCAM visualization for predictions
│   ├── requirements.txt   # Python dependencies
│   ├── Dockerfile         # GPU-enabled container for clients
│   └── saved_models/      # Trained model checkpoints
│
├── xray_classification_backend/
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
└── README.md
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

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_PASSWORD` | MySQL database password | `0000` |
| `JWT_SECRET` | Secret key for JWT signing | (default key) |
| `TEST_DATA_PATH` | Path to central test dataset | `test` |
| `MODEL_SAVE_DIR` | Directory for model checkpoints | `saved_models` |
| `PYTHON_EXECUTABLE` | Path to Python interpreter | `python` |
| `PYTHON_HEATMAP_SCRIPT` | Path to heatmap.py | `python/heatmap.py` |

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

## 🐳 Docker Deployment

### Build Client Image
```bash
cd python
docker build -t xray-client .
```

### Run with GPU Support
```bash
docker run --gpus all \
  -v /path/to/local/data:/data \
  -e DATASET_PATH=/data \
  xray-client --dataset_path /data
```

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