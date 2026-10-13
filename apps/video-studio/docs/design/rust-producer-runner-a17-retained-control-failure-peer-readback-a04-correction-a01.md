# A17 retained-control A04 failed-attempt correction addendum

This addendum corrects one evidence identity and records the expanded failed-control disposition. It preserves the original peer report unchanged:

- Original report: `apps/video-studio/docs/design/rust-producer-runner-a17-retained-control-failure-peer-readback-a04.md`
- Original bytes: `8,240`
- Original SHA-256: `bcd5b5149a8b090983d73e3927de9024449e691893650f13f6b9bba93134b1a6`

The independent root readback is:

- `artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-runner-a17-retained-a04-failure-root-readback-a01.json`
- Bytes: `702,970`
- SHA-256: `bf6babf40e7ff00222b4453c0d33d7ca46cd26a9f886f481fb4a5e19660f49ae`

## Corrected sentinel identity

The focused authorization-path-collision case contains the exact bytes `b'authorization-collision-sentinel\n'`:

`artifacts/scratch-video-goal-20261005/native-project-a01/native-text-unit-a01/rust-producer-runner-a17-build-attempt-a01/control-attempt-a17/focused/cases/authorization_path_collision/output-parent/collision-run/authorization.json`

The file is 33 bytes. Its independently rehashed SHA-256 is:

`a3b8e30e1f8de716401feff51dc0589442e7f4012d17905883bd24eb1a776916`

The fourth-sentinel SHA in the original peer report was incorrect. This value supersedes that single identity claim. The original report remains preserved for audit history.

## Corrected inventory count

The retained control root has 279 descendant directories. This excludes the control root itself. The inclusive directory count is 280. The independent root readback records:

- Regular files: `560`
- Regular-file bytes: `60,627,297`
- Malformed JSON files: `4`

The directory count and sentinel hash are independent file-system measurements. They do not claim that the failed attempt qualifies the driver.

## Expanded control disposition

The saved control results remain failed overall:

| Control group | Result | Evidence disposition |
| --- | ---: | --- |
| A04 lifecycle | `9/10` passed | `fifo_authority_rejected_nonblocking` failed with `elapsed_millis=997` and `stage_or_report_failed` |
| Focused controls | `4/15` passed | Eleven focused mutations failed their expected control assertions |
| Suspended launch variants | `6/11` passed | `allControlsPassed=false` |

The eleven focused failures were:

- `qualification_subject_final_mutation`: `focused_variant_failed`
- `qualification_postflight_revalidation_drift`: `authorization_review_drift`
- `authorization_run_name_mutation`: `focused_variant_failed`
- `authorization_parent_mutation`: `authorization_identity_failed`
- `authorization_executable_mutation`: `authorization_review_mismatch`
- `authorization_command_mutation`: `cancelled`
- `authorization_environment_mutation`: `authorization_review_mismatch`
- `authorization_policy_mutation`: `focused_variant_failed`
- `authorization_false_flag_mutation`: `focused_variant_failed`
- `authorization_review_hash_mismatch`: `review_reference_mutation_failed`
- `authorization_path_anchor_mutation`: `failed`

The `different_executable` launch mutation is a material control failure. The result has:

- `passed=false`
- `observedCode=completed`
- `allowedCodes=["loaded_executable_vnode_ambiguous"]`
- `childStarted=true`
- `resumed=true`
- `reaped=true`
- `return_code=0`
- `runnerError=null`

The mutated executable therefore resumed and completed. The expected pre-resume rejection was absent. Correcting the malformed-report allowlist cannot qualify this driver.

The retained readback classifies the attempt as `closed_failed_preserved`. It records caller and driver exit code `1`, caller failure `unparsed_actual_report_json`, `controlsExecuted=true`, `nestedClosureAccepted=false`, and `outerClosureComplete=true`. Native execution, native result acceptance, and product integration remain false.

## Scope

This addendum changes no source, media, metadata, state, or control output. It records read-only measurements from the preserved failed attempt. It makes no native producer, product, watched, heard, or creative acceptance claim.
