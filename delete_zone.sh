#Elimina (ricorsivamente) nelle cartelle i file con Zone.Identifier
find . -type f -name '*Zone.Identifier'  -exec rm {} \;
