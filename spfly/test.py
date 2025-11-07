import requests
import json
from urllib.parse import urljoin

BASE = "https://demmeltransportes.brudam.com.br/api/v1/"  # sem caminho extra
USUARIO = "7f9029a79a92bd78f1a62b77d42eb3d3"
SENHA = "e2611bbbdeff13ddfc32f133c8b0fc0e519a116bd9a2a3cf424e534d98f5ee97"

def get_jwt_token(base_url: str, usuario: str, senha: str, timeout=20) -> str:
    login_url = urljoin(base_url, "acesso/auth/login")
    payload = {"usuario": usuario, "senha": senha}
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    r = requests.post(login_url, json=payload, headers=headers, timeout=timeout)
    r.raise_for_status()
    body = r.json()
    token = None
    if isinstance(body, dict):
        token = body.get("data", {}).get("access_key") or body.get("data", {}).get("token") \
                or body.get("access_key") or body.get("token")
    if not token:
        raise ValueError(f"Token não encontrado na resposta de login: {json.dumps(body, ensure_ascii=False)}")
    return token

def get_ocorrencias_nfe(base_url: str, token: str, chave: str, comprovante: int = 0, timeout=20):
    url = urljoin(base_url, "tracking/ocorrencias/cnpj/nf")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    params = {"documento": documento, "numero": numero, "comprovante": comprovante}
    r = requests.get(url, headers=headers, params=params, timeout=timeout)
   
    return r

numero  = "30340" 
documento = "17809524000392"
comprovante = 1  


def main():
    try:
        print("Fazendo login para obter token...")
        token = get_jwt_token(BASE, USUARIO, SENHA)
        print("Token obtido (início):", token[:40] + "..." if token else "<vazio>")

    except Exception as e:
        print("Falha no login:", e)
        return

 

    try:
        resp = get_ocorrencias_nfe(BASE, token, documento, numero, comprovante)
        print("Status:", resp.status_code)
        
        try:
            body = resp.json()
            print(json.dumps(body, indent=2, ensure_ascii=False))
        except Exception:
            print(resp.text)

      
        with open("ocorrencias_nfe_response.json", "w", encoding="utf-8") as f:
            f.write(resp.text)
        print("Resposta salva em ocorrencias_nfe_response.json")

    except requests.exceptions.RequestException as e:
        print("Erro na requisição:", e)

if __name__ == "__main__":
    main()
