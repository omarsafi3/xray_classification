FROM tensorflow/tensorflow:2.15.0-gpu
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt  # tensorflow-gpu and dependencies
ENTRYPOINT ["python", "client.py"]