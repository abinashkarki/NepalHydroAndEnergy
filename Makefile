.PHONY: wiki-index validate serve figures

wiki-index:
	python scripts/build_wiki_page_index.py
	python scripts/build_wiki_page_meta.py
	python scripts/build_backlinks.py

validate:
	python scripts/validate_repo.py
	git diff --check

serve:
	./wiki/explorer/serve.sh 8765

figures:
	python scripts/build_research_figures.py
