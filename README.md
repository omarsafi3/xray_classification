# X-ray Classification Backend (Spring Boot)

This is a backend application built with **Spring Boot** to serve predictions for X-ray image classification.

## ⚙️ Tech Stack

- Java 17
- Spring Boot 3+
- Maven
- RESTful APIs

## 📁 Project Structure

```
├── src/
│   ├── main/
│   │   ├── java/com/example/xray/        # Source code
│   │   └── resources/                    # Application config
├── python/                               # Python scripts (e.g., heatmap.py)
├── requirements.txt                      # Python dependencies
├── pom.xml                               # Maven project file
└── README.md                             # Project documentation
```

## 📦 Prerequisites

- Java 17 or higher
- Maven 3.8+
- IntelliJ IDEA (recommended)
- [Anaconda/Miniconda](https://www.anaconda.com/products/distribution) or Python 3.8+

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/omarsafi3/xray_classification.git
cd xray_classification
```

### 2. Set Up Python Environment

Create and activate a virtual environment with required dependencies:

```bash
conda create -n xray_env python=3.8
conda activate xray_env
pip install -r requirements.txt
```

### 3. Update Python Script Path in Java Code

In your Java backend code, make sure to update the Python executable path in the `ProcessBuilder` inside [`HeatmapController.java`](https://github.com/omarsafi3/xray_classification/blob/main/xray_classification_backend/src/main/java/com/example/xray_classification_backend/controller/HeatmapController.java):

```java
String pythonScriptPath = "C:\Users\<your-username>\xray_classification\python\heatmap.py";

ProcessBuilder builder = new ProcessBuilder(
    "C:\Users\<your-username>\anaconda3\envs\xray_env\python.exe",
    pythonScriptPath,
    "--img_path", tempImage.getAbsolutePath()
);
```

✅ Replace `<your-username>` with your actual Windows username and make sure that:

- The path to the Python environment points to where you installed the dependencies from `requirements.txt`.
- The `heatmap.py` script path is accurate based on your local folder structure.

Replace `<your-username>` with your actual username.

### 4. Open in IntelliJ

1. Open IntelliJ IDEA.
2. Choose **File > Open** and select the project directory.
3. IntelliJ will automatically detect the Maven configuration and import the project.

### 5. Build the Project

```bash
mvn clean install
```

### 6. Run the Server

```bash
mvn spring-boot:run
```

Server will start at:

```
http://localhost:8080
```


