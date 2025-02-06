{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.git
    pkgs.curl
    pkgs.python3
    pkgs.python3Packages.requests
  ];

  # Use pip inside the environment
  shellHook = ''
    alias vim="nvim"
    alias vi="nvim"
    alias v="nvim"


    echo "The python environment is ready!"
    echo ""
    echo "Packages installed:"
    echo " - git"
    echo " - curl"
    echo " - python3"
    echo " - python3.requests"
    echo ""
  '';
}
