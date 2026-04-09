import request from '@/utils/http'

export interface AssessmentHistoryParams {
  page: number
  page_size: number
}

export interface AssessmentSubmitPayload {
  age: number
  alcohol_intake: number
  cancer_history: number
  chronic_diseases: string[]
  family_history: string[]
  gender: string
  genetic_risk: number
  height: number
  notes: string
  physical_activity: number
  smoking: number
  symptoms: string[]
  weight: number
}

export function fetchAssessmentHistory(params: AssessmentHistoryParams) {
  return request.get<any>({
    url: '/api/v1/assessment/history',
    params
  })
}

export function submitAssessment(data: AssessmentSubmitPayload) {
  return request.post<any>({
    url: '/api/v1/assessment/submit',
    data,
    showSuccessMessage: false
  })
}

export function deleteAssessmentRecord(record_id: string) {
  return request.del<any>({
    url: `/api/v1/assessment/record/${record_id}`
  })
}

export function fetchAssessmentRecord(record_id: string) {
  return request.get<any>({
    url: `/api/v1/assessment/record/${record_id}`
  })
}

export function exportAssessment(record_id: string) {
  return request.get<any>({
    url: `/api/v1/assessment/export/${record_id}`
  })
}
