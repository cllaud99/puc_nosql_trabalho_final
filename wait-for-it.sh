#!/usr/bin/env bash
# Aguarda o MySQL estar disponível antes de executar o comando

host="$1"
port="$2"
shift 2
cmd="$@"

until nc -z "$host" "$port"; do
  echo "⏳ Aguardando $host:$port..."
  sleep 2
done

echo "✅ $host:$port está disponível! Executando comando..."
exec $cmd
