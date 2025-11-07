 let
   nixpkgs = fetchTarball "https://github.com/NixOS/nixpkgs/archive/ca534a76c4afb2bdc07b681dbc11b453bab21af8.tar.gz"; # NixOS 25.05
   pkgs = import nixpkgs {};
 in

 pkgs.mkShellNoCC {
   packages = with pkgs; [
    (python313.withPackages (ps: with ps; [ pip jinja2 ]))
    live-server
    tailwindcss_4
    git
    hivemind
    inotify-tools
   ];

  shellHook = ''
    pip freeze > requirements.lock
  '';
 }
