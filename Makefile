.PHONY: wiki-index validate serve figures test

wiki-index:
	python scripts/build_wiki_page_index.py
	python scripts/build_wiki_page_meta.py
	python scripts/build_backlinks.py
	python scripts/build_wiki_fact_index.py
	python scripts/build_wiki_search_index.py
	.venv/bin/python scripts/build_wiki_vector_index.py --local-files-only

validate:
	python scripts/validate_repo.py
	git diff --check

test:
	python -m unittest scripts.test_wiki_search_index scripts.test_extract_pdf_images scripts.test_explorer_performance

serve:
	./wiki/explorer/serve.sh 8765

figures:
	python scripts/build_research_figures.py
