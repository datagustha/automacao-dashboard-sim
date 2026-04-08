import os # Importamos 'os' para ler as variáveis de ambiente (como senhas secretas)
from sqlalchemy import create_engine # 'create_engine' é a função do SQLAlchemy que cria a conexão central com o banco de dados
from dotenv import load_dotenv # 'load_dotenv' carrega as senhas que colocamos no arquivo oculto .env

# Carregamos as variáveis de ambiente definidas no arquivo .env
# Isso é uma boa prática para não deixar senhas soltas no código que vai para o Github
load_dotenv()

# Pegamos as variáveis de ambiente e guardamos em variáveis do Python
DB_HOST = os.getenv("DB_HOST", "192.168.100.200") # Pega o IP, se não achar no .env usa o padrão
DB_USER = os.getenv("DB_USER", "simfacilita")     # Usuário do banco
DB_PASS = os.getenv("DB_PASS", "NVjv*Ae2GPQ01.AK") # Senha do banco
DB_NAME = os.getenv("DB_NAME", "dbsimfacilita")   # Nome do banco de dados

# Montamos a "String de Conexão". O SQLAlchemy precisa dessa URL para saber onde se conectar.
# Usamos o 'mysql+pymysql' que é o driver oficial recomendado para conversar com o MySQL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}?charset=utf8mb4"

# Criamos o Engine. O Engine é o coração do SQLAlchemy, é ele que vai enviar os comandos SQL para o banco.
# O parâmetro pool_recycle=3600 evita que o MySQL feche a conexão por inatividade após 1 hora (boas práticas)
# O parâmetro echo=False desativa o log de todos os comandos SQL executados (mude para True se quiser ver o SQL gerado no terminal para debug)
engine = create_engine(DATABASE_URL, pool_recycle=3600, echo=False)
