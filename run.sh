#!/bin/bash
source ~/.bashrc

#migrate
echo "migrate"
uv run areich upgrade
echo "성~~~공~~띠~~~"

#uvicorn
echo "uvicorn Server Run"
uv run uvicorn main:app --host 0.0.0.0 --port 8000
echo "앙 ~ 띠~~₩"