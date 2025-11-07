tailwind: tailwindcss -i src/css/base.css -o src/css/compiled.css --watch
live-server: cd dist; live-server
builder: while inotifywait -rq -e modify -e create -e delete src; do ./dist.py; done
