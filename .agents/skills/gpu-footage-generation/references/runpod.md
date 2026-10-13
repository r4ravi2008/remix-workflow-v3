# RunPod lifecycle and cost control

Discover the live RunPod integration/Executor connection or installed CLI and its schemas. Verify the account and read the current balance, all owned Pods including stopped ones, Pod disks, network/global volumes, Serverless endpoints, clusters, and their billing categories. Record this baseline inventory and the owner/purpose of each resource before allocating anything, so closeout can distinguish this run's resources from unrelated or shared ones. Credentials and old pod IDs are runtime state. Do not copy personal account names, IPs, SSH keys or prices from Urvashi scripts into a new run.

## Before allocation

Prepare the accepted sources, shot plan, graph/runner and return destination locally. Check the selected model's real repository/docs, licensing and current workflow support; a similarly named model is not interchangeable. Select a Pod-compatible image. Urvashi lost setup time on a Hub-authenticated Serverless image that could not boot as an ordinary Pod.

Honor the requested GPU and allowed alternatives. Reuse a compatible stopped owned pod only after checking its contents and the current price. A stopped host can lose capacity; a failed restart does not authorize a new GPU type. See [RunPod's restart guidance](https://docs.runpod.io/pods/troubleshooting/zero-gpus). Prices and availability must be refreshed for each allocation.

Choose storage deliberately. Container disk is ephemeral; volume disk survives stops but not pod termination; network and global volumes survive Pod termination. Check the current mount and persistence, rather than assuming `/workspace` means a particular storage type. RunPod bills a stopped Pod's volume disk until termination; independent volumes bill until separately deleted. Include their projected lifetime in the budget, and save irreplaceable outputs locally before deleting them. [RunPod storage options](https://docs.runpod.io/pods/storage/types) describe the current lifecycle.

## Prove connectivity before large transfers

Read the actual SSH connection details from the allocated pod. Full SSH supports SCP/SFTP; basic proxy SSH does not. Prefer full SSH for bulk models and footage. Test one small upload and download with hashes, then measure a representative larger transfer before committing paid setup time. [RunPod SSH documentation](https://docs.runpod.io/pods/configuration/use-ssh) distinguishes these methods.

If only interactive proxy access exists, use a supported authenticated transfer method with measured throughput. Do not paste a giant base64 archive into an interactive shell: Urvashi encountered shell-parsing delays and roughly 16 KB/s transfer while a GPU billed. Test a bounded stream or supported sync path, or stop the allocation within the setup deadline. Keep services private or authenticated; a temporary unauthenticated public upload server is not the default transfer solution.

Put model caches and outputs on verified persistent storage. A network filesystem can make Python startup or model loading slow even on a faster GPU. Measure I/O; keep a reproducible runtime on local scratch if needed while preserving pinned code/locks, models and outputs. Never upgrade a working runtime to “latest” during a resumed batch.

## Pilot economics

Record actual GPU rate plus storage, allocation-to-ready time, cold/warm sampling time, decode/save time, and download time. Use a representative short shot and the longest planned class when costs differ materially. Compute both dollars per generated second and dollars per accepted usable second. Rejected footage is a real cost. Larger VRAM does not prove multiple simultaneous workers will improve throughput; benchmark bounded concurrency only when authorized.

Before each job, require remaining credit and authorized budget to cover a conservative full job, final save, transfer and shutdown reserve. Enforce a setup cutoff and a wall-clock shutdown deadline through an owned, verified control-plane mechanism or active supervision. A runner deadline only stops submissions. Killing its process or printing `STOP_POD` does not stop billing.

Stop compute while waiting for approvals, researching alternatives, or blocked on sources/transfers. Do not run a model download indefinitely because the GPU is already allocated. Distinguish a slow live encoder or growing file from a failed job; inspect PID/log/file growth before interrupting it. Recheck the actual provider state after any stop request.

## Resource closeout

Treat cleanup of this run's billable resources as part of the authorized generation job. Do it promptly after the final transfer, including when the run fails, is cancelled, or exhausts its budget. Stopping compute is useful during review or recovery, but it is not final cleanup. Do not leave a stopped Pod for convenience without a recorded retention decision, cost, and end time.

1. Download originals, graphs, intents, receipts, histories, runtime recipe, model identifiers, and reports. Verify local file counts, sizes, hashes, and decode as applicable; record unresolved or intentionally discarded remote files. Keep the local manifest and production ledger before removing remote data.
2. Reconcile any uncertain submissions and running jobs. Stop each run-owned Pod and confirm the provider state. Confirm no run-owned Serverless workers/jobs, cluster members, or other compute allocations remain active. A stopped process or empty ComfyUI queue is not provider evidence.
3. Terminate every run-owned Pod, including stopped and failed allocations, once its data is accounted for. This also releases its attached volume disk. Re-list **all** Pods, not just running Pods, and verify the IDs are absent. [RunPod's Pod guidance](https://docs.runpod.io/pods/manage-pods) states that stopped Pods still incur volume-disk charges.
4. Inventory network volumes and global volumes separately. A Pod deletion does not remove them. Delete each run-owned volume after verifying its contents are local or reproducible and that no other workload uses it; read back the volume inventory. Check the Storage page as well if the integration does not expose a volume type. Remove run-created Serverless endpoints and clusters after their jobs, outputs, and dependencies are accounted for. Public model endpoints are pay per request; reconcile their job ledger and charges but do not delete unrelated catalog entries, templates, secrets, or credentials.
5. Compare final inventory with the baseline. Read the account's **current spend rate** and billing breakdown for Pod GPU, Pod disk, network/global storage, Serverless, public endpoints, and clusters. Require zero run-owned billable resources and zero run-attributable current rate for a closed run. If unrelated baseline resources still bill, identify them separately; if any run-owned resource is retained, record its owner, reason, hourly cost, and removal deadline and keep closeout pending. Billing reports can lag; record the readback time and recheck when charges settle. Do not infer zero cost from an empty Pod list alone.

If a required original cannot be recovered, stop its compute immediately, record the exact storage cost and recovery deadline, and mark closeout **pending**. Escalate the data decision rather than silently retaining a billed disk or deleting the only copy. Preserve completed work when credit expires, record exact gaps, and use only an already-authorized fallback. No automatic top-ups.

## Recover interrupted operations

An interrupted HTTP/API operation can have succeeded remotely. Reconcile by known pod/job ID before creating another. Remove or stop failed allocations within the authorized lifecycle after checking whether they contain needed data. Never retry allocation in an unbounded loop or leave unused replicas billing.
