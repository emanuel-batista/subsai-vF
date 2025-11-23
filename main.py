import runpod
import os
import urllib.request
from subsai import SubsAI

# 1. Inicialização Global
print("A carregar modelo...")
subs_ai = SubsAI()
# Pode usar 'turbo' para testes rápidos ou 'large' para qualidade máxima
model = subs_ai.create_model('openai/whisper', {'model_type': 'large'})
print("Modelo carregado!")

def handler(job):
    job_input = job["input"]
    
    # Aceita 'audio_url' ou 'video_url'
    audio_url = job_input.get("audio_url") or job_input.get("video_url")
    
    if not audio_url:
        return {"error": "Nenhum URL fornecido."}

    # Variável para saber se precisamos limpar ficheiro temporário no final
    is_temp_file = False

    try:
        # --- LÓGICA SIMPLIFICADA ---
        if audio_url.startswith("file://"):
            # MODO LOCAL: Não copia nada. Usa o caminho original.
            input_file = audio_url.replace("file://", "")
            print(f"Modo Local: Usando ficheiro original em: {input_file}")
            
            if not os.path.exists(input_file):
                return {"error": f"Ficheiro não encontrado no caminho: {input_file}"}
                
        else:
            # MODO WEB: Faz download
            print(f"Modo Web: A descarregar de {audio_url}")
            
            # Detetar extensão ou usar .webm por defeito
            root, extension = os.path.splitext(audio_url)
            if not extension: extension = ".webm"
            
            input_file = f"temp_download{extension}"
            urllib.request.urlretrieve(audio_url, input_file)
            is_temp_file = True # Marcamos para apagar depois
        # ---------------------------

        # Transcrever
        print(f"A transcrever: {input_file}")
        subs = subs_ai.transcribe(input_file, model)
        
        # Salvar resultado na pasta local
        final_srt_path = "/app/resultado_final.srt"
        subs.save(final_srt_path)
        print(f"Legenda salva com sucesso em: {final_srt_path}")

        with open(final_srt_path, "r", encoding="utf-8") as f:
            srt_content = f.read()

        # Limpeza: Só apaga se foi um download da web
        if is_temp_file and os.path.exists(input_file):
            os.remove(input_file)
            print("Ficheiro temporário de download removido.")

        return {"srt": srt_content}

    except Exception as e:
        print(f"Erro fatal: {str(e)}")
        return {"error": str(e)}

runpod.serverless.start({"handler": handler})