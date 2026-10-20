.PHONY: all validate form templates slides catalog test

all: validate form templates slides catalog

validate:
	python3 scripts/validate_items.py

form:
	python3 scripts/build_form.py
	python3 scripts/build_form.py --site form/site

templates:
	python3 scripts/build_templates.py

slides:
	python3 scripts/build_slides.py

catalog:
	python3 scripts/build_catalog.py

test:
	python3 -m pytest -q
