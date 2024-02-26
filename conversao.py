import yaml
import json
import glob

# Carrega todos os arquivos YAML no diretório atual
yaml_files = glob.glob('*.yml')
data = {}

for file in yaml_files:
    with open(file, 'r') as f:
        yaml_data = yaml.safe_load(f)
        data.update(yaml_data)

# Escreve o resultado em um arquivo JSON
with open('swagger.json', 'w') as f:
    json.dump(data, f, indent=4)
