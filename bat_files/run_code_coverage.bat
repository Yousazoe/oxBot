:: This script runs code coverage and outputs them in /htmlcov/ folder

cd ..

:: Remove previous results
RD /Q /S htmlcov

:: https://stackoverflow.com/a/54107094/10882657

:: Run pytest tests in /test/ folder
poetry run pytest --cov=./
:: Run a round with the autotest bot, -a parameter stands for append to existing coverage report
poetry run coverage run -a test/autotest_bot.py
poetry run coverage run -a test/upgradestest_bot.py
poetry run coverage run -a test/damagetest_bot.py

:: Combine collected results and output them in /htmlcov/ folder
poetry run coverage html

