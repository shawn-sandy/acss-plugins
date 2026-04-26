// Intentional contract violations. The harness must catch BOTH of these:
//   1. Banned import (`@fpkit/acss`).
//   2. (Implicit) the file is in the known-bad/ tree and must trip
//      the validators when run against it.
//
// If validate_components.mjs ever extracts and validates this without
// failing, the validator's import-allowlist regex has regressed.
import { Button } from '@fpkit/acss'

export const KnownBad = () => <Button type="button">bad</Button>
