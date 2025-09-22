{
  description = "Remove old Nix generations with better arguments.";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  };

  outputs = {
    self,
    nixpkgs,
    ...
  } @ inputs: let
    lib = nixpkgs.lib;
    forEachSystem = lib.genAttrs lib.systems.flakeExposed;

    nix-generation-trimmer-package = {python3}:
      python3.pkgs.buildPythonApplication {
        pname = "nix-generation-trimmer";
        version = self.shortRev or self.dirtyShortRev or "unknown";

        src = ./package;
        pyproject = true;
        build-system = with python3.pkgs; [hatchling];
        dependencies = with python3.pkgs; [python-dateutil];
      };
  in {
    # Packages
    packages = forEachSystem (system: rec {
      default = nix-generation-trimmer;
      nix-generation-trimmer = nixpkgs.legacyPackages.${system}.callPackage nix-generation-trimmer-package {};
    });
    overlays.default = final: _: {
      nix-generation-trimmer = final.callPackage nix-generation-trimmer-package {};
    };

    # Modules
    nixosModules.default = import ./module/nix.nix inputs;
    homeModules.default = import ./module/home.nix inputs;
  };
}
