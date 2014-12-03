#!/bin/bash

echo "Collecting..." && ./github_pulls_collect.py && echo "Rendering..." && ./github_pulls_render.py && ./github_pulls_render_burndown.py && echo "Serving..." && python -m SimpleHTTPServer
