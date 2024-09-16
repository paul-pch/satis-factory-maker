all: install integrate

install:
	pyinstaller --onefile satis.py

integrate:
	grep -q '$(CURDIR)' ~/.zshrc || echo 'export PATH=$(CURDIR)/dist:$$PATH' >> ~/.zshrc
