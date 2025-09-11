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
2. In your configuration, add the overlay to get access to the package
    ```nix
    inputs: {
      nixpkgs.overlays = [
        inputs.generationTrimmer.overlays.default
      ];
    }
    ```
3. Use
    - Standalone use
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
    - Automatic garbage collection
        - NixOS
            ```nix
            {
              config,
              pkgs,
              ...
            }: {
              nix.gc = {
                automatic = true;
                dates = "daily";
              };

              systemd.services = {
                # Make built-in service depend on the generation selector
                nix-gc.wants = ["nix-gc-gen.service"];
                # Generation selector for garbage collection
                nix-gc-gen = {
                  description = "Generation selector for garbage collection";
                  serviceConfig.Type = "oneshot";
                  script = ''
                    exec "${pkgs.nix-generation-trimmer}/bin/nix-generation-trimmer" \
                      system                                                         \
                      --older-than 7d                                                \
                      --keep-at-least 10                                             \
                      --keep-at-most 50
                  '';
                  path = [config.nix.package.out];
                };
              };
            }
            ```
        - Home Manager
            ```nix
            {pkgs, ...}: {
              nix.gc = {
                automatic = true;
                dates = "daily";
              };

              systemd.user.services = {
                # Make built-in service depend on the generation selector
                nix-gc.Unit.Wants = ["nix-gc-gen.service"];
                # Generation selector for garbage collection
                nix-gc-gen = {
                  Unit.Description = "Generation selector for garbage collection";
                  Service = {
                    Type = "oneshot";
                    ExecStart = pkgs.writeShellScript "nix-gc-gen" ''
                      exec "${pkgs.nix-generation-trimmer}/bin/nix-generation-trimmer" \
                        user channel home-manager                                      \
                        --older-than 7d                                                \
                        --keep-at-least 10                                             \
                        --keep-at-most 50
                    '';
                  };
                };
              };
            }
            ```

## Inspirations

- [This bash script](https://gist.github.com/MaxwellDupre/3077cd229490cf93ecab08ef2a79c852)
- [An example of a systemd service running before built-in garbage collection](https://github.com/NixOS/nix/issues/9455#issuecomment-2987325585)
