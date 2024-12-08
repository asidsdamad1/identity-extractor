FROM python:3.11

RUN apt-get update && apt-get install -y \
    libzbar0 \
    libzbar-dev \
    libgl1-mesa-glx \
    libglib2.0-0

WORKDIR /app

COPY . /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir huggingface_hub==0.16.4

ENV PYTHONUNBUFFERED=1

CMD ["python", "run.py"]
