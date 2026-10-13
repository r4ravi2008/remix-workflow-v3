export interface ProductionScope {
  tenantId: string
  releaseId: string
  jobId: string
  attempt: number
  leaseHash: string
}
export const productionAssetPrefix = (releaseId: string) => `p_${releaseId}_`
