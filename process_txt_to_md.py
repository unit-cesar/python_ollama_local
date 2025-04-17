import os
import requests
import time
import argparse

# OLLAMA_LOG_LEVEL=debug ollama serve
# python process_txt_to_md.py --input-dir "./textos" --output-dir "./textos"

# pip install python-dotenv

# Configuração dos argumentos
parser = argparse.ArgumentParser(description='Processa arquivos .txt e gera .md via Ollama')
parser.add_argument('--input-dir', required=True, help='Diretório com arquivos .txt')
parser.add_argument('--output-dir', required=True, help='Diretório para salvar os arquivos .md')
args = parser.parse_args()

OLLAMA_API_URL = "http://localhost:11434/api/generate" # Comente a linha referente ao headers para usar local
INPUT_DIR = args.input_dir
OUTPUT_DIR = args.output_dir
TIMEOUT_SECONDS = 300  # 5 minutos

def read_text_files(directory):
    texts = {}
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            filepath = os.path.join(directory, filename)
            with open(filepath, "r", encoding="utf-8") as file:
                texts[filename] = file.read().strip()  # Remove espaços extras
    return texts

def split_text(text, chunk_size=1024):  # Chunks size
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]


def ask_ollama(prompt, model="deepseek-coder-v2"):  # Modelo
    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"num_ctx": 2048}  # Limite de contexto explícito
            },
            timeout=TIMEOUT_SECONDS
        )
        response.raise_for_status()
        return response.json().get("response", "Sem resposta.")
    except Exception as e:
        if hasattr(e, 'response') and e.response is not None:
            print("❌ Erro HTTP:", e.response.status_code)
            print("🔍 Corpo da resposta:", e.response.text)
        return f"Erro na API: {str(e)}"

def generate_markdown_file(filename, content):
    markdown_content = f"##### Cheat Sheet gerado automáticamente com sistema em Python via Ollama (deepseek-coder-v2) - Por CesarDev\n\n"
    chunks = split_text(content)
    
    for chunk in chunks:
        time.sleep(2)  # Evita flood na API
        prompt = f"Vamos lá...\n{chunk}"
        analysis = ask_ollama(prompt)
        markdown_content += f"{analysis}\n\n"

    markdown_content += "---\n"
    return markdown_content

def save_markdown(content, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(content)
    print(f"✅ Arquivo salvo em: {output_path}")

if __name__ == "__main__":
    texts = read_text_files(INPUT_DIR)
    if not texts:
        print("⚠️ Nenhum arquivo .txt encontrado.")
        exit()

    for txt_filename, txt_content in texts.items():
        base_name = os.path.splitext(txt_filename)[0]
        md_filename = f"{base_name}.md"
        md_filepath = os.path.join(OUTPUT_DIR, md_filename)

        markdown = generate_markdown_file(txt_filename, txt_content)
        save_markdown(markdown, md_filepath)
