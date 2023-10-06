from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import os
from selenium.webdriver.common.keys import Keys
import urllib.parse
from webdriver_manager.chrome import ChromeDriverManager

def carregar_planilha():
    return pd.read_excel('Teste1.xlsx')

def obter_numeros(planilha):
    return planilha['numero'].tolist()

def enviar_link(numero, driver):
    link = f"https://web.whatsapp.com/send?phone={numero}&text="
    driver.get(link)

def enviar_mensagem(mensagem, driver):
    campo_mensagem = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]/p'))
    )
    campo_mensagem.click()
    time.sleep(2)
    campo_mensagem.send_keys(str(mensagem) + Keys.ENTER)

def chat_aberto(driver):
    try:
        campo_mensagem = driver.find_element(By.XPATH,
                                             '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]/p')
        return True
    except:
        return False

@app.route('/modo3')
def modo3():
    df = carregar_planilha()
    numeros = obter_numeros(df)
    return render_template('modo3.html', contatos=numeros)

@app.route('/automação/modo3.py', methods=['POST'])
def enviar_mensagens():
    # Ler as mensagens do formulário HTML
    mensagem_input = request.form['mensagem']
    mensagens_adicionadas = request.form.getlist('mensagens_adicionadas')

    # Combinar a mensagem do campo de entrada e as mensagens adicionadas
    mensagens = [mensagem_input] + mensagens_adicionadas

    # Ler a imagem do formulário HTML
    imagem = request.files['imagem']

    # Salvar a imagem na pasta 'uploads'
    pasta_uploads = 'uploads'
    if not os.path.exists(pasta_uploads):
        os.makedirs(pasta_uploads)

    caminho_imagem = os.path.join(pasta_uploads, imagem.filename)
    imagem.save(caminho_imagem)

    # Ler novamente a planilha para obter os contatos
    df = carregar_planilha()
    numeros = obter_numeros(df)

    # Abre o Chrome
    driver = webdriver.Chrome(executable_path='caminho_do_chromedriver')  # Substitua 'caminho_do_chromedriver' pelo caminho do seu chromedriver

    driver.get('https://web.whatsapp.com/')

    while len(driver.find_elements(By.ID, "side")) < 1:
        time.sleep(1)

    # Aguarda o login manual no WhatsApp Web
    # ...

    for numero in numeros:
        enviar_link(numero, driver)

        # Aguardar até que o chat esteja aberto
        timeout = 15  # Tempo máximo de espera em segundos
        start_time = time.time()

        while not chat_aberto(driver):
            elapsed_time = time.time() - start_time

            if elapsed_time > timeout:
                print(f"O chat não foi aberto para o número {numero}. Pulando para o próximo número.")
                break

            time.sleep(1)

        if not chat_aberto(driver):
            continue

        for mensagem in mensagens:
            enviar_mensagem(mensagem, driver)

        # Enviar a imagem
        campo_anexo = driver.find_element(By.XPATH, '//div[@title="Anexar"]')
        campo_anexo.click()

        campo_input = driver.find_element(By.XPATH, '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]')
        campo_input.send_keys(caminho_imagem)

        # Aguardar até que a imagem seja carregada
        timeout = 10  # Tempo máximo de espera em segundos
        start_time = time.time()

        while True:
            if time.time() - start_time > timeout:
                print(f"O envio da imagem para o número {numero} falhou. Pulando para o próximo número.")
                break

            try:
                # Verificar se o ícone de envio está habilitado
                driver.find_element(By.XPATH, '//span[@data-icon="send-light"]')
                break
            except:
                pass

            time.sleep(1)

        if time.time() - start_time > timeout:
            continue

        # Clicar no ícone de envio
        campo_enviar = driver.find_element(By.XPATH, '//span[@data-icon="send-light"]')
        campo_enviar.click()

        time.sleep(2)

    # Fechar o navegador
    driver.quit()

    return 'Mensagens e imagem enviadas com sucesso!'