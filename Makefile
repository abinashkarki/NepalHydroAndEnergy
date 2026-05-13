.PHONY: wiki-index validate serve figures wiki-figures lead1-outputs test mcp deficit-model briefs wiki-build

wiki-index:
	python scripts/build_wiki_page_index.py
	python scripts/build_wiki_page_meta.py
	python scripts/build_backlinks.py
	python scripts/build_wiki_fact_index.py
	python scripts/build_claim_governance.py
	python scripts/build_wiki_search_index.py
	.venv/bin/python scripts/build_wiki_vector_index.py --local-files-only

briefs:
	python scripts/build_briefs.py --write --inject --packs

validate:
	python scripts/validate_repo.py
	git diff --check

test:
	python -m unittest scripts.test_wiki_search_index scripts.test_extract_pdf_images scripts.test_explorer_performance scripts.test_claim_integrity scripts.test_source_used_by
	python scripts/evaluate_search_benchmark.py --strict

serve:
	./wiki/explorer/serve.sh 8765

mcp:
	python scripts/wiki_mcp_server.py

figures: wiki-figures
	python scripts/build_research_figures.py

wiki-figures:
	python scripts/build_wiki_figures.py

lead1-outputs:
	python scripts/build_lead1_trade_outputs.py

wiki-build: briefs wiki-figures wiki-index

.PHONY: deficit-model
deficit-model: data/winter_deficit_model/solar_monthly_cf_profile.csv data/winter_deficit_model/storage_hydro_pipeline.csv
	python scripts/build_winter_deficit_model.py --write --validate
