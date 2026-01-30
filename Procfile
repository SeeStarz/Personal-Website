tailwind: tailwindcss -i src/data/css/base.css -o src/data/css/compiled.css --watch
live-server: cd dist; live-server --port 8080 --host localhost
builder: src/script/dist.py; while inotifywait -rq -e modify -e create -e delete src; do src/script/dist.py; done
