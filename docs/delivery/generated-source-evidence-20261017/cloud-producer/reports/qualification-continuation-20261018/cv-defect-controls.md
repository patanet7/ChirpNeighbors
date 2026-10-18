The seven controls behaved as expected; aggregate **FAIL is not a harness failure**.

| Control | Measured result |
|---|---|
| Crow selected12 | Raster PASS; zero partial alpha or registration residual |
| Crow raw grip | Expected FAIL: **8,182 partial-alpha pixels** |
| Bath mismatch | WARN: silhouette widths **118→165–175**; lower-window baseline deltas **+29/+29/+3/+4** |
| Valid Sparrow head motion | Protected-body residual **0**; no false jitter failure |
| Unintended translation | Expected FAIL: observed/residual **(4,3)** |
| Declared translation | PASS: observed **(4,3)**, residual **(0,0)** |
| Declared root travel | PASS: image residual **0**, projected world travel **20** |

Bath jitter was **not evaluated** without a stable region. Its widths and lower-image window do not establish anatomy or sole contact.

The valid Sparrow receives a white/noise **WARN** from one existing tiny component per frame, despite zero bright-boundary or partial-alpha pixels. Treating that warning as bad art would be a false rejection. Bath edge touches and raw-image antialiasing likewise remain proxies.

All seven codec evaluations were **NOT_RUN**. Action completeness, anatomy, physical support and subjective quality remain **NOT_EVALUATED**.

Exact SHA-256 pins:

```text
tool        ae795cbb5e181d8275cb9cbe046db0cbce92c40e778587f4ac94d2d5f7f28a1a
config      e1ccb70063a2a658c0d786c830ee124a92378160c4897766f9c711b3552c2371
report      c507bd9958757b0cd554e54c5c1bbf5c6c258e6ba68809c66dac4344bfa655f7
calibration ab4fe81a4970ffadf223d4a93f6574b5332d52e2549e7a2892d954ab96dfa3e5
case000     871f6e32be9eb04733a19e993cf1b860191116a3242d498d9036c66936eae828
case001     f26104306216427c50f87b3d05eefe7f62553436ab6880a3bdc9f1019b047237
case002     b0faf401770730e77de8d71d93c5241f43e2cbf58024b8e6d9dfb38636eb3668
case003     76a30c69164adcef6be17f22a7c0ebf67248d888f234cb66ef0602d9ab1619eb
case004     0e3235aef779ccefb3017f2b1c7bdc0a28a11a2de09695aeea1ce50dc7c9ea7e
case005     50a57f29979027c545664fb1163043eb5b5552a662e7f2a84f04d76bba056353
case006     94e539c029ed3f9b19100db9b04f09ceb9e1bd21180933eaf9fd1b13c5d12a48
```

No golden reruns, original edits or threshold changes. Hash-only verification confirmed all pinned files remain exact. Runtime admission is not claimed.
