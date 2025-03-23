#!/bin/bash
pipenv install
pipenv install --dev pytest
echo "Setup complete. Activate the environment with 'pipenv shell'"