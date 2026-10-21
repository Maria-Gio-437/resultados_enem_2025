import json
import unicodedata
import redis

# Conecta ao Redis que subiu no Docker na porta 6379
try:
    cliente_redis = redis.Redis(
        host="localhost",
        port=6379,
        db=0,
        decode_responses=True,
        socket_connect_timeout=1
    )
    cliente_redis.ping()
except Exception:
    cliente_redis = None

def normalizar_texto(texto: str) -> str:
    """Remove acentos, converte para maiúsculas e troca espaços por sublinhados."""
    if not texto:
        return ""
    nfkd = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join([c for c in nfkd if not unicodedata.combining(c)])
    return sem_acento.strip().upper().replace(" ", "_")

def buscar_com_cache(chave: str, funcao_busca_sqlite, ttl_segundos: int = 86400):
    """
    Fluxo Cache-Aside:
    1. Tenta buscar no Redis (HIT).
    2. Se não existir (MISS), consulta o SQLite, grava no Redis com TTL e retorna.
    """
    if cliente_redis is None:
        return funcao_busca_sqlite(), "SQLITE (SEM CACHE)"

    try:
        dados_em_cache = cliente_redis.get(chave)
        if dados_em_cache is not None:
            # Cache HIT: retorno instantâneo da memória RAM
            return json.loads(dados_em_cache), "REDIS (HIT)"
    except redis.RedisError:
        pass

    # Cache MISS: consulta na fonte da verdade (SQLite)
    dados_banco = funcao_busca_sqlite()

    # Grava o resultado no Redis com TTL de segurança
    try:
        cliente_redis.setex(chave, ttl_segundos, json.dumps(dados_banco))
    except redis.RedisError:
        pass

    return dados_banco, "SQLITE (MISS)"

def invalidar_chaves(chaves: list):
    """Executa o comando DEL nas chaves afetadas no momento da escrita."""
    if cliente_redis is None or not chaves:
        return
    try:
        cliente_redis.delete(*chaves)
    except redis.RedisError:
        pass

def limpar_todo_cache():
    """Remove todas as chaves criadas pelo sistema no Redis."""
    if cliente_redis is None:
        return
    try:
        chaves = cliente_redis.keys("enem:*")
        if chaves:
            cliente_redis.delete(*chaves)
    except redis.RedisError:
        pass