# X-ray Classification Backend (Spring Boot)

This is a backend application built with **Spring Boot** to serve predictions for X-ray image classification.

## ⚙️ Tech Stack

- Java 17
- Spring Boot 3+
- Maven
- RESTful APIs


## 📦 Prerequisites

- Java 17 or higher
- Maven 3.8+
- IntelliJ IDEA (recommended)

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/omarsafi3/xray_classification.git
cd xray_classification
```

### 2. Open in IntelliJ

1. Open IntelliJ IDEA.
2. Choose **File > Open** and select the project directory.
3. IntelliJ will automatically detect the Maven configuration and import the project.

### 3. Build the Project

In IntelliJ terminal or your command line:

```bash
mvn clean install
```

### 4. Run the Server

Using IntelliJ:

- Locate the main class (e.g., `XrayClassificationApplication.java`) and run it directly.

Or via terminal:

```bash
mvn spring-boot:run
```

The server will start at:

```
http://localhost:8080
```

## 🧪 API Endpoints (Example)

- `POST /api/predict` — Submit an X-ray image and receive the classification result.

## 🗂 Notes

This backend is intended to work with a frontend or a model-serving layer for X-ray classification. Ensure that your prediction logic is properly wired (e.g., using TensorFlow model or REST call to a Python server).

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---

Feel free to contribute or raise issues via [GitHub Issues](https://github.com/omarsafi3/xray_classification/issues).

