result=0
trap 'result=1' ERR

ruff format --check && ruff check
mypy .

exit "$result"