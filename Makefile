build:
	rm -rf dist/
	python3 -m build
test:
	python3 src/pysubsonic/api.py
upload: build
	python3 -m twine upload dist/*
docs: PHONY
	cd docs && sphinx-build source build
docdeploy: docs
	rsync -avc docs/build/ xhec.dev:/var/www/main/pysubsonic/

PHONY: