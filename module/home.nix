{self, ...}: {
  lib,
  pkgs,
  config,
  ...
}: let
  cfg = config.nix.gc.generationTrimmer;
in {
  imports = [(import ./opts.nix ["user" "channel" "home-manager"])];
  config = lib.mkIf cfg.enable {
    systemd.user.services = {
      # Make built-in service depend on the generation selector
      nix-gc.Unit.Wants = ["${cfg.serviceName}.service"];
      # Generation selector for garbage collection
      ${cfg.serviceName} = {
        Unit.Description = "Generation selector for garbage collection";
        Service = {
          Type = "oneshot";
          ExecStart = pkgs.writeShellScript cfg.serviceName (
            builtins.concatStringsSep " " (
              # Command
              ["exec" "${self.packages.${pkgs.stdenv.hostPlatform.system}.default}/bin/nix-generation-trimmer"]
              # `nix-env` path
              ++ [
                "--nix-env-path"
                "${
                  if config.nix.package != null
                  then config.nix.package
                  else pkgs.nix
                }/bin/nix-env"
              ]
              # Profiles
              ++ cfg.profiles
              # Older than
              ++ (
                if cfg.olderThan != null
                then ["--older-than" (lib.escapeShellArg cfg.olderThan)]
                else []
              )
              # Keep at least
              ++ (
                if cfg.keepAtLeast != null
                then ["--keep-at-least" (builtins.toString cfg.keepAtLeast)]
                else []
              )
              # Keep at most
              ++ (
                if cfg.keepAtMost != null
                then ["--keep-at-most" (builtins.toString cfg.keepAtMost)]
                else []
              )
              # Dry run
              ++ (
                if cfg.dryRun == true
                then ["--dry-run"]
                else []
              )
            )
          );
        };
      };
    };
  };
}
