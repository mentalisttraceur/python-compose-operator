default:
	python setup.py sdist
	python setup.py bdist_wheel

clean:
	rm -rf __pycache__ build *.egg-info dist
	rm -f *.py[oc] MANIFEST

test:
	pytest test.py
	PYTHONPATH=. pytest README.rst
