defaultProfiles: {lib, ...}: let
  inherit (lib) types;
in {
  options.nix.gc.generationTrimmer = {
    enable = lib.mkEnableOption "Generation selector for garbage collection";
    serviceName = lib.mkOption {
      description = "Name of the generation trimming service.";
      type = types.str;
      default = "nix-gc-generation-trimmer";
    };
    profiles = lib.mkOption {
      description = "Scope which should be cleaned up.";
      type = types.listOf (types.enum ["user" "channel" "home-manager" "system"]);
      default = defaultProfiles;
    };
    olderThan = lib.mkOption {
      description = ''
        Age of an oldest generation to keep.
        Should be composed out of 1 or more duration sections in decreasing order:
        - A section is '# duration' where '#' is a positive non-zero number and 'duration' is one of 'year', 'month', 'day', or 'hour'
        - Each duration specifier has a plural and a 1 letter version
        - Spaces are optional
      '';
      example = "10 years 5d";
      type = types.nullOr types.str;
      default = null;
    };
    keepAtLeast = lib.mkOption {
      type = types.nullOr types.ints.positive;
      description = "Minimum amount of generations to keep (not including the current one).";
      default = null;
    };
    keepAtMost = lib.mkOption {
      type = types.nullOr types.ints.positive;
      description = "Maximum amount of generations to keep (not including the current one).";
      default = null;
    };
    dryRun = lib.mkOption {
      type = types.nullOr types.bool;
      description = "Print the profile and the generations to be removed in a JSON format, do not delete them.";
      default = null;
    };
  };
}
