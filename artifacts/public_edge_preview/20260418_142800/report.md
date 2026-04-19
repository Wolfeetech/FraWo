# Public Edge Preview Check

Generated from `public_edge_preview_check.py`.

- VM220 internal target: `10.1.0.22`
- VM220 global IPv6: `2a00:1e:ef80:7c01:be24:11ff:feaa:bbcc`
- current public IPv4 observed from StudioPC: `92.211.33.54`

## Result

- decision: `failed`
- failed_checks: `internal_www_root, internal_apex_redirect, internal_radio_player, global_ipv6_www_root`

## Probe Details

- `internal_www_root`: `failed`
  expectation: Host www.frawo-tech.de on 10.1.0.22 should return 200 and the FraWo homepage with radio CTA.
  observed_status: `200`
  log: `C:\Users\StudioPC\Workspace\FraWo\artifacts\public_edge_preview\20260418_142800\internal_www_root.log`
- `internal_apex_redirect`: `failed`
  expectation: Host frawo-tech.de on 10.1.0.22 should redirect to https://www.frawo-tech.de/.
  observed_status: `200`
  log: `C:\Users\StudioPC\Workspace\FraWo\artifacts\public_edge_preview\20260418_142800\internal_apex_redirect.log`
- `internal_radio_player`: `failed`
  expectation: Host www.frawo-tech.de on 10.1.0.22 /radio/public/frawo-funk should return the AzuraCast player.
  observed_status: `404`
  log: `C:\Users\StudioPC\Workspace\FraWo\artifacts\public_edge_preview\20260418_142800\internal_radio_player.log`
- `global_ipv6_www_root`: `failed`
  expectation: The global IPv6 of VM220 should already serve the FraWo homepage on HTTP with Host www.frawo-tech.de.
  observed_status: `none`
  log: `C:\Users\StudioPC\Workspace\FraWo\artifacts\public_edge_preview\20260418_142800\global_ipv6_www_root.log`
- `public_ipv4_hairpin`: `failed`
  expectation: direct HTTP to the current public IPv4 should only pass after router forwarding is active.
  observed_status: `none`
  log: `C:\Users\StudioPC\Workspace\FraWo\artifacts\public_edge_preview\20260418_142800\public_ipv4_hairpin.log`

## Cutover Notes

- public IPv4 hairpin to 92.211.33.54:80 still fails from StudioPC; likely no active router forward for 80/443 to VM220.