#!/usr/bin/env python3
"""
Test script - Captura foto da webcam e envia pra Roboflow
"""

import requests
import base64

# Configuração
API_KEY = "YHhYv8VymcHjYEUcjdWS"
PROJECT_ID = "detect-people-wqfy8" 
MODEL_VERSION = 2

def test_with_image_file(image_path: str):
    """Testa detecção com um arquivo de imagem."""
    print(f"📸 Testando com imagem: {image_path}")
    
    # Lê a imagem
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")
    
    # Chama API Roboflow
    url = f"https://detect.roboflow.com/{PROJECT_ID}/{MODEL_VERSION}"
    params = {"api_key": API_KEY}
    
    print(f"🌐 Chamando API: {url}")
    
    try:
        response = requests.post(
            url,
            data=image_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            params=params,
            timeout=10
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # Mostra resultado
            print("\n✅ Detecções encontradas:")
            print("=" * 50)
            
            predictions = result.get("predictions", [])
            print(f"Total: {len(predictions)} objetos detectados\n")
            
            for pred in predictions:
                class_name = pred.get("class", "unknown")
                confidence = pred.get("confidence", 0)
                print(f"  • {class_name.upper()}: {confidence:.1%}")
            
            print("=" * 50)
            return True
        else:
            print(f"❌ Erro: {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
        return False


def test_with_webcam():
    """Testa capturando da webcam."""
    print("📷 Capturando foto da webcam...")
    
    try:
        import cv2
    except ImportError:
        print("❌ OpenCV não instalado!")
        print("   Execute: pip install opencv-python")
        return False
    
    # Abre webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Não consegui abrir a webcam")
        return False
    
    # Captura um frame
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("❌ Falha ao capturar frame")
        return False
    
    # Salva temporariamente
    temp_path = "/tmp/roboflow_test.jpg"
    cv2.imwrite(temp_path, frame)
    print(f"✓ Foto salva: {temp_path}")
    
    # Testa com a imagem
    return test_with_image_file(temp_path)


if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("🎥 ROBOFLOW TEST - Camera Guardian")
    print("=" * 50 + "\n")
    
    print(f"API Key: {API_KEY[:10]}...{API_KEY[-5:]}")
    print(f"Project: {PROJECT_ID}")
    print(f"Version: {MODEL_VERSION}\n")
    
    # Tenta com webcam primeiro
    print("Opção 1: Testar com WEBCAM")
    print("-" * 50)
    #success = test_with_webcam()
    success = False
    
    if not success:
        print("\n⚠️ Webcam falhou. Tente com uma imagem local.")
        print("\nOpção 2: Testar com ARQUIVO")
        print("-" * 50)
        image_path = input("Caminho da imagem (ex: /home/usuario/foto.jpg): ").strip()
        if image_path:
            success = test_with_image_file(image_path)
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Teste bem-sucedido!")
    else:
        print("❌ Teste falhou")
    print("=" * 50 + "\n")