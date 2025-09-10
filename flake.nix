{
  description = "Remove old Nix generations with better arguments.";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  };

  outputs = {
    self,
    nixpkgs,
    ...
  }: let
    lib = nixpkgs.lib;
    forEachSystem = lib.genAttrs lib.systems.flakeExposed;

    nix-generation-trimmer-package = {python3}:
      python3.pkgs.buildPythonApplication {
        pname = "nix-generation-trimmer";
        version = self.shortRev or self.dirtyShortRev or "unknown";
        pyproject = true;

        src = ./.;

        build-system = with python3.pkgs; [hatchling];

        dependencies = with python3.pkgs; [python-dateutil];
      };
  in {
    packages = forEachSystem (system: rec {
      nix-generation-trimmer = nixpkgs.legacyPackages.${system}.callPackage nix-generation-trimmer-package {};
      default = nix-generation-trimmer;
    });
    overlays.default = final: _: {
      nix-generation-trimmer = final.callPackage nix-generation-trimmer-package {};
    };
  };
}
