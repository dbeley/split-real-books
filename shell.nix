with import <nixpkgs> { };
pkgs.mkShell {
  buildInputs = [
    python3
    python3Packages.pypdf
    python3Packages.pyyaml
  ];

}
