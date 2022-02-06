all:
	black .
	-flake8 --ignore E501
	-pydocstyle