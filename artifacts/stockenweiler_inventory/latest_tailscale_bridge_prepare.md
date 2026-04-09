# Stockenweiler Tailscale Bridge Prepare

- generated_at: 2026-03-31 16:08:15
- target: stock-pve
- action_taken: auth_pending_reused
- backend_state_before: NeedsLogin
- backend_state_after: NeedsLogin
- current_tailnet_before: -
- current_tailnet_after: -
- auth_url: https://login.tailscale.com/a/14bca4f701de61

## Notes

- Stockenweiler pve is prepared as a Tailscale subnet-router candidate for 192.168.178.0/24.
- IPv4/IPv6 forwarding baseline and vmbr0 UDP GRO tuning were applied before the rehome step.
- The WireGuard recovery path via stock-pve remains the fallback while Tailscale rehome is pending.
- The script is idempotent: it reuses an existing login URL instead of blindly resetting a pending join.

## tailscale up output

```text

```

## tailscale status after

```text
{
  "Version": "1.94.2-t0a29cf18b-g3f044c9f6",
  "TUN": true,
  "BackendState": "NeedsLogin",
  "AuthURL": "https://login.tailscale.com/a/14bca4f701de61",
  "TailscaleIPs": null,
  "Self": {
    "ID": "",
    "PublicKey": "nodekey:0000000000000000000000000000000000000000000000000000000000000000",
    "HostName": "pve",
    "DNSName": "",
    "OS": "linux",
    "UserID": 0,
    "TailscaleIPs": null,
    "Addrs": [
      "91.14.44.20:41641",
      "192.168.178.25:41641"
    ],
    "CurAddr": "",
    "Relay": "nue",
    "PeerRelay": "",
    "RxBytes": 0,
    "TxBytes": 0,
    "Created": "0001-01-01T00:00:00Z",
    "LastWrite": "0001-01-01T00:00:00Z",
    "LastSeen": "0001-01-01T00:00:00Z",
    "LastHandshake": "0001-01-01T00:00:00Z",
    "Online": false,
    "ExitNode": false,
    "ExitNodeOption": false,
    "Active": false,
    "PeerAPIURL": null,
    "TaildropTarget": 0,
    "NoFileSharingReason": "",
    "InNetworkMap": false,
    "InMagicSock": false,
    "InEngine": false
  },
  "Health": [
    "Unable to connect to the Tailscale coordination server to synchronize the state of your tailnet. Peer reachability might degrade over time."
  ],
  "MagicDNSSuffix": "",
  "CurrentTailnet": null,
  "CertDomains": null,
  "Peer": null,
  "User": null,
  "ClientVersion": null
}
```
