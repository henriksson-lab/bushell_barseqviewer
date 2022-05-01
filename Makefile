rung:
	gunicorn app:server -b :15590 -n barseq2
install:
	pip install -r requirements.txt
