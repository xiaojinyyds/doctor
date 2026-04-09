/**
 * 医学影像识别API接口
 */
import request from '@/utils/http'

/**
 * 医学影像上传和分析接口
 */
export const medicalImageAPI = {
  /**
   * 上传并分析医学影像（V2版本，使用OSS存储）
   */
  uploadAndAnalyze: (formData: FormData, params?: any) => {
    return request.post<any>({
      url: '/api/v1/medical-image-v2/upload-and-analyze',
      data: formData,
      params,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  /**
   * 分析已上传的影像（旧版本）
   */
  analyze: (formData: FormData) => {
    return request.post<any>({
      url: '/api/v1/medical-image/analyze',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  /**
   * 获取用户的影像历史记录
   */
  getHistory: (params?: {
    skip?: number
    limit?: number
    image_type?: string
  }) => {
    return request.get<any>({
      url: '/api/v1/medical-image-v2/history',
      params
    })
  },

  /**
   * 获取影像分析统计信息
   */
  getStatistics: (days: number = 30) => {
    return request.get<any>({
      url: '/api/v1/medical-image-v2/statistics',
      params: { days }
    })
  },

  /**
   * 获取风险趋势数据
   */
  getRiskTrend: (days: number = 30) => {
    return request.get<any>({
      url: '/api/v1/medical-image-v2/risk-trend',
      params: { days }
    })
  },

  /**
   * 对比两张影像的分析结果
   */
  compareImages: (imageId1: string, imageId2: string) => {
    return request.post<any>({
      url: '/api/v1/medical-image-v2/compare',
      data: {
        image_id_1: imageId1,
        image_id_2: imageId2
      }
    })
  },

  /**
   * 获取分析结果详情
   */
  getResultDetail: (resultId: string) => {
    return request.get<any>({
      url: `/api/v1/medical-image-v2/result/${resultId}`
    })
  },

  /**
   * 删除医学影像
   */
  deleteImage: (imageId: string) => {
    return request.del<any>({
      url: `/api/v1/medical-image-v2/image/${imageId}`
    })
  },

  /**
   * 医生审核分析结果
   */
  doctorReview: (resultId: string, data: { doctor_opinion: string; true_label?: string }) => {
    return request.post<any>({
      url: `/api/v1/medical-image-v2/result/${resultId}/review`,
      data
    })
  },

  /**
   * 获取仪表板数据
   */
  getDashboard: () => {
    return request.get<any>({
      url: '/api/v1/medical-image-v2/dashboard'
    })
  },

  /**
   * 获取模型信息
   */
  getModelInfo: () => {
    return request.get<any>({
      url: '/api/v1/medical-image/model/info'
    })
  },

  /**
   * 获取待审核影像列表（医生专用）
   */
  getPendingReview: (params?: { skip?: number; limit?: number }) => {
    return request.get<any>({
      url: '/api/v1/medical-image-v2/pending-review',
      params
    })
  },

  /**
   * 提交医生审核意见
   */
  submitReview: (resultId: string, data: { doctor_opinion: string; true_label?: string }) => {
    return request.post<any>({
      url: `/api/v1/medical-image-v2/result/${resultId}/review`,
      data
    })
  }
}

