.PHONY: sync validate build push

# Regenerate strips + mechanisms from plays.yaml, copy to miro-app/public/
sync:
	python3 compile_strips.py
	cp plays_strips.json plays_mechanisms.json plays_info.json miro-app/public/

# Validate all plays against JSON schema
validate:
	python3 validate_plays.py

# Full pipeline: sync → validate → miro-app build
build: sync validate
	cd miro-app && npm run build

# Typecheck only (faster than full build)
check:
	python3 validate_plays.py
	cd miro-app && npm run typecheck
