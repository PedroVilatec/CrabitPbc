echo "Arquivo = $1  Host = $2.local/update"
curl -v -F filename=$1 -F upload=@$1 "$2.local/update"