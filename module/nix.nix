{self, ...}: {
  lib,
  pkgs,
  config,
  ...
}: let
  cfg = config.nix.gc.generationTrimmer;
in {
  imports = [(import ./opts.nix ["system"])];
  config = lib.mkIf cfg.enable {
    systemd.services = {
      # Make built-in service depend on the generation selector
      nix-gc.wants = ["${cfg.serviceName}.service"];
      # Generation selector for garbage collection
      ${cfg.serviceName} = {
        description = "Generation selector for garbage collection";
        serviceConfig.Type = "oneshot";
        script = builtins.concatStringsSep " " (
          # Command
          ["exec" "${self.packages.${pkgs.stdenv.hostPlatform.system}.default}/bin/nix-generation-trimmer"]
          # `nix-env` path
          ++ ["--nix-env-path" "${config.nix.package}/bin/nix-env"]
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
        );
      };
    };
  };
}
