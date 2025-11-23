import runpod
import os
import wget # Pode ser necessário adicionar ao Dockerfile ou usar requests
from subsai import SubsAI

# 1. Inicialização Global (Executado apenas uma vez quando o contentor arranca)
print("A carregar modelo...")
subs_ai = SubsAI()
# O modelo 'turbo' já foi descarregado no Dockerfile, por isso o carregamento será rápido
model = subs_ai.create_model('openai/whisper', {'model_type': 'turbo'})
print("Modelo carregado!")

# 2. Função Handler (Executada a cada pedido/job)
def handler(job):
    job_input = job["input"]
    
    # Obter o URL do áudio/vídeo enviado no pedido
    audio_url = job_input.get("audio_url")
    if not audio_url:
        return {"error": "Nenhum URL de áudio fornecido."}

    output_file = "temp_output.srt"
    input_file = "temp_input.webm"

    try:
        # Descarregar o ficheiro (exemplo simples)
        # Nota: Em produção, recomenda-se uma gestão de downloads mais robusta
        print(f"A descarregar: {audio_url}")
        import urllib.request
        urllib.request.urlretrieve(audio_url, input_file)

        # Transcrever
        print("A transcrever...")
        subs = subs_ai.transcribe(input_file, model)
        subs.save(output_file)

        # Ler o resultado para devolver como texto
        with open(output_file, "r", encoding="utf-8") as f:
            srt_content = f.read()

        # Limpar ficheiros temporários
        if os.path.exists(input_file): os.remove(input_file)
        if os.path.exists(output_file): os.remove(output_file)

        return {"srt": srt_content}

    except Exception as e:
        return {"error": str(e)}

# 3. Iniciar o RunPod
runpod.serverless.start({"handler": handler})