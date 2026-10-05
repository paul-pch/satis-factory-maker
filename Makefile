APP_NAME := satisfactory
ENTRYPOINT := satis.py
DIST_DIR := dist

.DEFAULT_GOAL := all
.PHONY: all sync test build integrate clean

all: sync build integrate

sync:
	uv sync
	@echo "Environment synced"

test:
	uv run pytest

build: sync
	uv run pyinstaller --clean --onefile --name=$(APP_NAME) $(ENTRYPOINT)
	@echo "Application built in $(DIST_DIR)/$(APP_NAME)"

integrate:
	grep -q '$(CURDIR)/$(DIST_DIR)' ~/.zshrc || echo 'export PATH=$(CURDIR)/$(DIST_DIR):$$PATH' >> ~/.zshrc
	@echo "Application integrated into PATH"
	@echo "-> Please reload your terminal"

clean:
	rm -rf $(DIST_DIR) build *.egg-info coverage-report .coverage .pytest_cache **/__pycache__ $(APP_NAME).spec
	rm -rf .venv
	@echo "Build artifacts removed"
