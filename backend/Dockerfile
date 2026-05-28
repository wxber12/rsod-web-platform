FROM python:3.11-slim

WORKDIR /app

# pip mirror (China)
ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
ENV PIP_TRUSTED_HOST=pypi.tuna.tsinghua.edu.cn
ENV PIP_DEFAULT_TIMEOUT=300

# Install system dependencies for opencv-python-headless
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# ★ Install CPU-only PyTorch FIRST (saves ~4GB vs default CUDA version)
# Then install remaining dependencies from requirements.txt
RUN pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure model files exist (must be present at build time)
RUN ls app/models/*.pt || echo "WARNING: No .pt model files found in app/models/"

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
