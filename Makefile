activate:
	if [ -d env3 ]; then \
		echo "Now switch to env3"; \
		source env3/bin/activate; \
	fi

requirements-freeze.txt: activate
	pip freeze > $@

freeze: requirements-freeze.txt
