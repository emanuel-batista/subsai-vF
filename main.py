import runpod
import os
import urllib.request
from subsai import SubsAI

print("--- A INICIAR O SCRIPT ATUALIZADO ---")

# 1. Inicialização Global
print("A carregar modelo...")
subs_ai = SubsAI()
# Mudei para 'large' conforme pediu antes
model = subs_ai.create_model('openai/whisper', {'model_type': 'large'})
print("Modelo carregado!")

def handler(job):
    job_input = job["input"]
    
    # Pega o URL/Caminho
    audio_url = job_input.get("audio_url") or job_input.get("video_url")
    
    if not audio_url:
        return {"error": "Nenhum URL fornecido."}

    print(f"Processando input: {audio_url}")
    
    # Variável para controlar se devemos apagar o ficheiro no final
    file_to_remove = None

    try:
        # --- LÓGICA DIRETA: SEM CÓPIAS ---
        if audio_url.startswith("file://"):
            # Se for arquivo local, usamos o CAMINHO ORIGINAL
            # Remove 'file://' e fica com '/app/Screwdriver...'
            input_file = audio_url.replace("file://", "")
            
            if not os.path.exists(input_file):
                return {"error": f"ERRO: O ficheiro não existe no caminho: {input_file}"}
            
            print(f"Modo Local: Lendo direto de {input_file}")
            
        else:
            # Se for link da internet, aí sim baixamos para um temporário
            print("Modo Web: Iniciando download...")
            root, extension = os.path.splitext(audio_url)
            if not extension: extension = ".webm"
            
            input_file = f"temp_download{extension}"
            urllib.request.urlretrieve(audio_url, input_file)
            file_to_remove = input_file # Marcamos para deletar depois
        # ---------------------------------

        # Transcrever
        print(f"A transcrever: {input_file}")
        subs = subs_ai.transcribe(input_file, model)
        
        # Salvar resultado
        final_srt_path = "/app/resultado_final.srt"
        subs.save(final_srt_path)
        print(f"Legenda salva em: {final_srt_path}")

        with open(final_srt_path, "r", encoding="utf-8") as f:
            srt_content = f.read()

        # Só apaga se for arquivo baixado da internet
        if file_to_remove and os.path.exists(file_to_remove):
            os.remove(file_to_remove)

        return {"srt": srt_content}

    except Exception as e:
        print(f"ERRO FATAL: {str(e)}")
        return {"error": str(e)}

runpod.serverless.start({"handler": handler})