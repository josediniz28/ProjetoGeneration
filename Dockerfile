# Use uma imagem oficial do Python como base
FROM python:3.12.0-slim

# Defina o diretório de trabalho no container
WORKDIR /app

# Copie os arquivos do projeto para o diretório de trabalho
COPY . .

# Instale as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Exponha a porta que sua aplicação usará
EXPOSE   5000

# Comando para iniciar a aplicação
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]

