build:
	rm -rf dist/
	python3 -m build
test:
	python3 src/pysubsonic/api.py
upload: build
	python3 -m twine upload dist/*
docs:
	cd docs && sphinx-build source build