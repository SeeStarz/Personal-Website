 let
   nixpkgs = fetchTarball "https://github.com/NixOS/nixpkgs/archive/ca534a76c4afb2bdc07b681dbc11b453bab21af8.tar.gz"; # NixOS 25.05
   pkgs = import nixpkgs {};
 in

 pkgs.mkShellNoCC {
   packages = with pkgs; [
    python313
    python313Packages.pip
    nodejs_24
    git
    hivemind
    inotify-tools
   ];

   shellHook = ''
     if [ ! -d env ]; then
       echo "Creating Python virtualenv..."
       python -m venv env
       source env/bin/activate

       echo "Installing Python deps..."
       pip install jinja2
       pip freeze > requirements.lock
     else
       source env/bin/activate
     fi

     if [ ! -d node_modules ]; then
       echo "Installing Node deps..."
       npm install tailwindcss @tailwindcss/cli live-server
     fi

     export PATH="$(realpath ./node_modules/.bin):$PATH"
   '';
 }
