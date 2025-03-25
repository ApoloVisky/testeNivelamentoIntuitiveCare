import os
import requests
import zipfile
from bs4 import BeautifulSoup


URL = "https://www.gov.br/ans/pt-br/acesso-a-informacao/participacao-da-sociedade/atualizacao-do-rol-de-procedimentos"
SAVE_DIR = "data/"  
ZIP_FILE = os.path.join(SAVE_DIR, "anexos.zip") 


os.makedirs(SAVE_DIR, exist_ok=True)


ANEXOS_DESEJADOS = ["Anexo I", "Anexo II"]

def get_pdf_links(url):
    """Obtém os links dos PDFs filtrando apenas Anexo I e II."""
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Erro ao acessar {url}")

    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a", href=True)

    pdf_links = []
    for link in links:
        href = link["href"]
        if href.endswith(".pdf") and any(anexo in link.text for anexo in ANEXOS_DESEJADOS):
            pdf_links.append(href)

    return pdf_links

def download_pdf(url, save_path):
    """Baixa um PDF e salva localmente."""
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(save_path, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"✅ Download concluído: {save_path}")
    else:
        print(f"❌ Erro ao baixar: {url}")

def zip_pdfs():
    """Compacta todos os PDFs baixados na pasta 'data/' em um único arquivo ZIP."""
    with zipfile.ZipFile(ZIP_FILE, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_name in os.listdir(SAVE_DIR):
            if file_name.endswith(".pdf"):  
                file_path = os.path.join(SAVE_DIR, file_name)
                zipf.write(file_path, arcname=file_name)
                print(f"📦 Adicionado ao ZIP: {file_name}")

    print(f"✅ Arquivo ZIP criado: {ZIP_FILE}")

def main():
    print("🔍 Buscando links dos Anexos I e II na página da ANS...")
    pdf_links = get_pdf_links(URL)

    if not pdf_links:
        print("❌ Nenhum anexo encontrado. Verifique se os nomes mudaram.")
        return

    for pdf_link in pdf_links:
        pdf_name = pdf_link.split("/")[-1]
        full_path = os.path.join(SAVE_DIR, pdf_name)

        
        full_url = pdf_link if pdf_link.startswith("http") else f"https://www.gov.br{pdf_link}"

        print(f"⬇️ Baixando {pdf_name}...")
        download_pdf(full_url, full_path)

    
    zip_pdfs()

if __name__ == "__main__":
    main()
