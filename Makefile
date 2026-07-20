PYTHON ?= python3

.PHONY: wiki-index validate serve figures test release-check release-record-check mcp deficit-model wiki-figures lead1-outputs wiki-build

wiki-index:
	$(PYTHON) scripts/build_wiki_page_index.py
	$(PYTHON) scripts/build_wiki_page_meta.py
	$(PYTHON) scripts/build_backlinks.py
	$(PYTHON) scripts/build_wiki_fact_index.py
	$(PYTHON) scripts/build_claim_governance.py
	$(PYTHON) scripts/build_wiki_search_index.py
	@if $(PYTHON) -c 'import sentence_transformers' >/dev/null 2>&1; then \
		$(PYTHON) scripts/build_wiki_vector_index.py --local-files-only; \
	else \
		echo "INFO: keeping the shipped vector index (install requirements-search.txt to rebuild it)"; \
	fi

validate:
	$(PYTHON) scripts/validate_repo.py
	$(PYTHON) scripts/check_source_used_by.py
	$(PYTHON) scripts/check_retired_claims.py
	git diff --check

test:
	$(PYTHON) -m unittest scripts.test_wiki_search_index scripts.test_explorer_search_runtime scripts.test_explorer_performance scripts.test_claim_integrity scripts.test_source_used_by tests.test_apply_doed_project_status_overlay tests.test_benchmark_hydromap_coverage tests.test_build_doed_hydropower_registry tests.test_build_doed_missing_operating_projects tests.test_build_doed_project_status_overlay tests.test_build_tributary_maps_capacity_authority
	node tests/test_wiki_search_intents.js

release-check: wiki-index validate test release-record-check
	$(PYTHON) scripts/check_generated_ownership.py

release-record-check:
	$(PYTHON) scripts/check_release_record.py

serve:
	./wiki/explorer/serve.sh 8765

mcp:
	$(PYTHON) scripts/wiki_mcp_server.py

figures:
	$(PYTHON) scripts/build_wiki_figures.py
	$(PYTHON) scripts/build_research_figures.py

wiki-figures:
	$(PYTHON) scripts/build_wiki_figures.py

lead1-outputs:
	$(PYTHON) scripts/build_lead1_trade_outputs.py

wiki-build: wiki-figures wiki-index

.PHONY: deficit-model
deficit-model: data/winter_deficit_model/solar_monthly_cf_profile.csv data/winter_deficit_model/storage_hydro_pipeline.csv
	$(PYTHON) scripts/build_winter_deficit_model.py --write --validate
