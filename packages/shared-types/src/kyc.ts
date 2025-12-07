export interface KYCRequest {
  id: string
  userId: string
  status: "pending" | "approved" | "rejected"
  documentType: string
  submittedAt: string
  reviewedAt?: string
  reviewerId?: string
}

export interface KYCReviewRequest {
  status: "approved" | "rejected"
  notes?: string
}
