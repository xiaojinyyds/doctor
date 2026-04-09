import request from '@/utils/http'

/**
 * 获取完整知识图谱
 */
export function fetchKnowledgeGraph() {
  return request.get<any>({
    url: '/api/v1/knowledge/graph'
  })
}

/**
 * 获取用户个性化风险图谱
 * @param assessmentId 评估记录ID
 */
export function fetchUserRiskGraph(assessmentId: string) {
  return request.get<any>({
    url: `/api/v1/knowledge/user-risk-graph/${assessmentId}`
  })
}

/**
 * 获取疾病详细信息
 * @param diseaseId 疾病ID
 */
export function fetchDiseaseInfo(diseaseId: string) {
  return request.get<any>({
    url: `/api/v1/knowledge/disease/${diseaseId}`
  })
}

