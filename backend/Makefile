run:
	uvicorn backend.api.main:app --reload --port 8000

install:
	pip install -r requirements.txt && python -m spacy download en_core_web_sm

test:
	pytest tests/ -v
