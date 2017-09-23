env3:
	if [ -d env3 ]; then \
		echo "Now switch to env3"; \
		source env3/bin/activate; \
	fi

requirements-freeze.txt: env3
	pip freeze > $@

freeze: requirements-freeze.txt

AQs/AQs/test_utf8.jl: env3
	export CURDIR=$$(dirname $@) && echo "In $$CURDIR" && \
		cd $$CURDIR && make $$(basename $@)
