result=0
trap 'result=1' ERR

ruff format
ruff check --select I --fix
ruff check --fix

exit "$result"