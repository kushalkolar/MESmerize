# Clear any previous dist dir
rm -rf ./dist/

# create wheel
python setup.py sdist bdist_wheel

# upload to test pypi
twine upload --repository testpypi dist/*

