.PHONY: all validate form templates slides contract test

all: validate form templates slides contract

validate:
	python3 scripts/validate_items.py

form:
	python3 scripts/build_form.py
	python3 scripts/build_form.py --site form/site

templates:
	python3 scripts/build_templates.py

slides:
	python3 scripts/build_slides.py

contract:
	python3 scripts/build_contract.py --site contract/site

test:
	python3 -m pytest -q
