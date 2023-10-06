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
from selenium.webdriver.chrome.service import Service

app = Flask(__name__)


@app.route('/modo2.py', methods=['POST'])
def enviar_excel():
    excel_file = request.files['excel_file']

    if excel_file.filename.endswith('.xlsx'):
        # Cria o diretório temporário, se não existir
        if not os.path.exists('temp'):
            os.makedirs('temp')

        # Salva o arquivo temporariamente no diretório 'temp'
        file_path = os.path.join('temp', excel_file.filename)
        excel_file.save(file_path)

        # Leitura do arquivo Excel usando pandas
        contatos_df = pd.read_excel(file_path)

        navegador = webdriver.Chrome()  # Insira o caminho para o chromedriver
        navegador.get("https://web.whatsapp.com/")

        while len(navegador.find_elements(By.ID, "side")) < 1:
            time.sleep(2)

        # Já estamos com o login feito no WhatsApp Web
        for i, mensagem in enumerate(contatos_df['Mensagem']):
            pessoa = contatos_df.loc[i, "Pessoa"]
            numero = contatos_df.loc[i, "Número"]
            Codigo = contatos_df.loc[i, "Cod"]
            texto = urllib.parse.quote(f"""Empresária da beleza, quero te apresentar uma técnica totalmente inovadora vinda diretamente dos Estados Unidos 🇺🇸 que irá ampliar sua carta de serviços e o seu faturamento!

A técnica está revolucionando o mercado e é perfeita para quem já tem clientes ou para você que quer se destacar da concorrência e preencher aquela sala que está vazia. A técnica se chama se chama drenagem de Hollywood.



Meu nome é Josie Rushing e sou a massoterapeuta das celebridades de Hollywood, construí um império nos Estados Unidos 🇺🇸usando apenas as minhas mãos! 🙏🏽

Clique no link abaixo e tenha acesso a minha comunidade exclusiva de empresárias da área da beleza, por lá estou revelando por meio de Lives TODOS os meus segredos! 

https://drenagemdehollywood.com.br/convite-v3/
@josierushingbr


Hoje, às 20h08 temos um encontro marcado com o sucesso, espero você!
""")
            link = f"https://web.whatsapp.com/send?phone={numero}&text={texto}"
            navegador.get(link)
            # Aguarda 5 segundos para carregar a página do WhatsApp
            time.sleep(10)

            # Verifica se o chat foi aberto
            if len(navegador.find_elements(By.ID, "side")) < 1:
                print(
                    f"Não foi possível abrir o chat para o número {numero}. Pulando para o próximo número.")
                continue

            try:
                input_box = WebDriverWait(navegador, 40).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div/p'))
                )
                input_box.send_keys(Keys.ENTER)
                time.sleep(8)
            except:
                print(
                    f"Erro ao enviar mensagem para o número {numero}. Pulando para o próximo número.")
                continue

        # Fecha o navegador após o envio das mensagens
        navegador.quit()

        return "Mensagens enviadas com sucesso!"
    else:
        return "Por favor, selecione um arquivo Excel (.xlsx)"


if __name__ == '__main__':
    app.run(debug=True)
