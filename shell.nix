let
  nixpkgs = fetchTarball {
    # NixOS 25.11
    url = "https://github.com/NixOS/nixpkgs/archive/50c5a4032a4a5017405e31873bb41b58ba4b4f03.tar.gz";
    sha256 = "114wfyg825yasf9fh61lvaqzqw8pg8ha7q8q9n7b4bl673f3z16m";
  };
  pkgs = import nixpkgs {};
in
  pkgs.mkShellNoCC {
    packages = with pkgs; [
      (python313.withPackages (ps: with ps;
        [ pip jinja2 markdown-it-py ])
      )
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
