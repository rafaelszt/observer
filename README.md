# Observer
Detecção de entrada não autorizada, utilizando processamento de faces em vídeo.
Projeto desenvolvido por Rafael Teixeira, para o Trabalho de Conclusão de Curso da Ciência da Computação na PUCPR.

# Instalação

1. Faça o download do código 

2. Instale python3.6

3. Execute o comando:

        pip install requirements.txt

# Configuração

1. Inclua as seguintes variáveis de sistema:

    * `OBS_EMAIL_USER`: Usuário do email que será usado, normalmente é o próprio email

    * `OBS_EMAIL_PASSWD`: Senha do email

    * `OBS_EMAIL_FROM`: Email que será usado para enviar os emails de alerta


2. Copie os modelos pré-treinados para a pasta `models` na raiz do aplicativo

3. Altere as configurações necessárias no arquivo `instance/config.py`

4. Altere as configurações de host e port no arquivo `run.py`

# Execução

1. Execute o comando `python3 ./run.py`

2. Acesse o servidor a partir do browser no endereço http://localhost:5000/ nas configurações padrões.

3. Credenciais padrão são:

       usuário: admin@local
       senha: admin

