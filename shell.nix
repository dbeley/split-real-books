{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python3
    python3Packages.pip
    python3Packages.pypdf
    python3Packages.pyyaml
    python3Packages.pytest
    python3Packages.pytest-cov
    prek
  ];
}
