FROM python:3.10-slim

WORKDIR /

# Install dependencies
RUN apt-get update && apt-get install -y ffmpeg git build-essential

# Install PyTorch with CUDA support
RUN pip install --no-cache-dir torch==2.2.0+cu118 torchaudio==2.2.0+cu118 --index-url https://download.pytorch.org/whl/cu118

# Install RunPod and SubsAI
RUN pip install --no-cache-dir runpod git+https://github.com/absadiki/subsai

# Download Models (Turbo, Large, Medium, Base)
# Usamos um loop em Python para iniciar e baixar cada um deles
RUN python3 -c "from subsai import SubsAI; \
subs_ai = SubsAI(); \
models = ['turbo', 'large', 'medium', 'base']; \
print('Downloading models:', models); \
[subs_ai.create_model('openai/whisper', {'model_type': m}) for m in models]; \
print('All models downloaded successfully!');"

# Copy your handler file
COPY main.py /

# Start the container
CMD ["python3", "-u", "main.py"]