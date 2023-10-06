from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
from selenium.webdriver.common.keys import Keys
import urllib.parse

app = Flask(__name__)

@app.route('/modo1.py', methods=['POST'])
def enviar_mensagem():
    telefones = []
    mensagens = []
    for key in request.form.keys():
        if key.startswith('telefone-'):
            telefone = request.form[key]
            telefones.append(telefone)
        elif key.startswith('mensagem-'):
            mensagem = request.form[key]
            mensagens.append(mensagem)

    try:
        planilha = pd.read_excel('mensagens.xlsx')
    except FileNotFoundError:
        dados = {'Número': [], 'Mensagem': []}
        planilha = pd.DataFrame(dados)

    dados = {'Número': telefones, 'Mensagem': mensagens}
    df = pd.DataFrame(dados)
    planilha = pd.concat([planilha, df], ignore_index=True)
    planilha.to_excel('mensagens.xlsx', index=False)

    driver = webdriver.Chrome()  # Certifique-se de ter o ChromeDriver instalado e configurado corretamente
    driver.get('https://web.whatsapp.com')

    input('Faça o login no WhatsApp Web e pressione Enter para continuar...')

    for telefone, mensagem in zip(telefones, mensagens):
        texto = urllib.parse.quote(mensagem)
        link = f"https://web.whatsapp.com/send?phone={telefone}&text={texto}"
        driver.get(link)
        time.sleep(5)

        if len(driver.find_elements(By.ID, "side")) < 1:
            print(f"Não foi possível abrir o chat para o número {telefone}. Pulando para o próximo número.")
            continue

        try:
            input_box = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div/p'))
            )
            input_box.send_keys(Keys.ENTER)
            time.sleep(5)
        except:
            print(f"Erro ao enviar mensagem para o número {telefone}. Pulando para o próximo número.")
            continue

    driver.quit()

    return 'Mensagens enviadas com sucesso!'

if __name__ == '__main__':
    app.run(debug=True)
