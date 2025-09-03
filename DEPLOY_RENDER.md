# Deploy no Render - Instruções

## Problemas Resolvidos

1. **psycopg2 incompatível com Python 3.13**: Atualizado para `psycopg[binary]==3.1.18`
2. **Porta não detectada**: Configurado gunicorn para usar `$PORT` do Render
3. **Servidor de desenvolvimento**: Substituído `runserver` por `gunicorn`

## Arquivos Criados/Modificados

- `build.sh`: Script de build para o Render
- `start.sh`: Script para iniciar a aplicação 
- `render.yaml`: Configuração automática do serviço
- `.env.example`: Exemplo de variáveis de ambiente
- `requirements.txt`: Atualizados os drivers de banco
- `settings.py`: Configurações de produção e DATABASE_URL

## Configuração no Render

### Opção 1: Usando render.yaml (Recomendado)
1. Faça commit e push dos arquivos
2. No Render, conecte o repositório
3. O `render.yaml` será detectado automaticamente

### Opção 2: Configuração Manual
1. **Build Command**: `./build.sh`
2. **Start Command**: `./start.sh` 
3. **Variáveis de Ambiente**:
   - `DEBUG=false`
   - `SECRET_KEY=sua_chave_secreta_aqui`
   - `DATABASE_URL` (será fornecida automaticamente se você conectar um banco PostgreSQL)

## Testando Localmente

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar build
chmod +x build.sh start.sh
./build.sh

# Iniciar aplicação
export PORT=8000
./start.sh
```

## Variáveis de Ambiente no Render

- `DEBUG`: false (para produção)  
- `SECRET_KEY`: Gere uma nova chave secreta
- `DATABASE_URL`: Conecte um banco PostgreSQL no Render
- `RENDER_EXTERNAL_HOSTNAME`: Será definido automaticamente

## Troubleshooting

Se ainda der erro de porta:
- Verifique se o gunicorn está bindando na porta correta
- Confirme que a variável `PORT` está sendo passada
- Verifique os logs do Render para erros de conexão com banco