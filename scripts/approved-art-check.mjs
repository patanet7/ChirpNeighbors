#!/usr/bin/env node
// Kept for existing callers: the approved-art checks now live in `node scripts/assets.mjs check`.
import { main } from './assets.mjs';

await main(['check']);
