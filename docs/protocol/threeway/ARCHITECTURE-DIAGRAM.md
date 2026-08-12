# Threeway Topology

```mermaid
flowchart LR
  U["User or authorized parent"] --> A["Provider adapter"]
  A --> R["Explicit mailbox role (optional)"]
  R --> M["Committed mailbox (current default)"]
  A --> H["Parent-scoped helpers"]
  H --> A

  M -. "read-only shadow projection" .-> E["Signed event refs"]
  E --> V["Signature and schema verification"]
  V --> D["Effective-state reducer"]
  D --> G["Exact merge gate"]
  G --> P["Protected runner effect"]

  K["Signer registry and private keys"] --> V
  C["Independent CI attestation"] --> D
  X["Explicit activation authority"] --> E
```

Seats are provider-neutral addresses, not permanent provider assignments.
Helpers do not become roles. Mailbox roles do not become signed principals.
The dotted migration edge becomes authoritative when one separately authorized
cutover creates the coherent refs consumed by readers. There is no later marker;
protected deployment still requires direct post-action proof.
