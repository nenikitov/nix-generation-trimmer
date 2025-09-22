# Nix Generation Trimmer

Remove old Nix generations with better arguments.

## Usage

The flake provides `nix-generation-trimmer` executable. You can use `--help` to list all available arguments.

> [!WARNING]
> Although I run this on my main systems, use it at your own risk.

## Installation

1. Add as a flake input
    ```nix
    {
      inputs = {
        # ...
        generationTrimmer = {
          url = "github:nenikitov/nix-generation-trimmer";
          inputs.nixpkgs.follows = "nixpkgs";
        };
      };
    }
    ```
2. Use
    - Package
        1. In your configuration, add the overlay to get access to the package
            ```nix
            inputs: {
              nixpkgs.overlays = [
                inputs.generationTrimmer.overlays.default
              ];
            }
            ```
        2. Install
            - NixOS
                ```nix
                {pkgs, ...}: {
                  environment.systemPackages = with pkgs; [nix-generation-trimmer];
                }
                ```
            - Home Manager
                ```nix
                {pkgs, ...}: {
                  home.packages = with pkgs; [nix-generation-trimmer];
                }
                ```
    - Module for automatic garbage collection
        1. In your configuration, add a module
            - NixOS
                ```nix
                nixosSystem {
                    modules = [
                        # ...
                        inputs.generationTrimmer.nixosModules.default
                    ]
                }
                ```
            - Home Manager
                ```nix
                homeManagerConfiguration {
                    modules = [
                        # ...
                        inputs.generationTrimmer.homeModules.default
                    ]
                }
                ```
        2. Enable the module
            ```nix
            {
                config.nix.gc.generationTrimmer = {
                    enable = true;
                    keepAtLeast = 10;
                    keepAtMost = 50;
                    olderThan = "7d";
                };
            }
            ```
## Inspirations

- [This bash script](https://gist.github.com/MaxwellDupre/3077cd229490cf93ecab08ef2a79c852)
- [An example of a systemd service running before built-in garbage collection](https://github.com/NixOS/nix/issues/9455#issuecomment-2987325585)
