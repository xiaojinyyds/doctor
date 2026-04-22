/**
 * 风险评估 API
 * 适配后端增强模型和扩展问卷
 */
import request from '@/utils/http'

/**
 * 问卷请求数据类型
 */
export interface QuestionnaireV2Request {
  // ==================== 基础信息 ====================
  age: number
  gender: '男' | '女'
  height: number
  weight: number

  // ==================== 生活习惯 ====================
  smoking_status: 0 | 1 | 2  // 0=从不, 1=曾经, 2=目前
  smoking_years?: number
  smoking_amount?: number
  alcohol_frequency: string  // 从不/偶尔/经常/每天
  alcohol_amount?: number
  exercise_hours_per_week: number
  exercise_intensity: string  // 低/中/高
  sleep_hours: number
  sleep_quality: string  // 差/一般/良好

  // ==================== 详细饮食习惯 ====================
  vegetable_fruit_intake: string  // 很少/偶尔/经常/每天
  red_meat_intake: string  // 很少/每周1-2次/每周2-3次/每天
  processed_food_intake: string  // 很少/偶尔/经常/每天
  pickled_food_intake: string  // 很少/偶尔/经常/每天
  dairy_intake: string  // 很少/偶尔/经常/每天

  // ==================== 疾病史 ====================
  chronic_diseases: string[]
  family_cancer_history: {
    has_history: boolean
    relation?: string
    cancer_types?: string[]
  }
  personal_cancer_history: 0 | 1
  surgery_history: string[]
  medication_history: string[]

  // ==================== 环境与职业暴露 ====================
  occupational_exposure: {
    has_exposure: boolean
    types?: string[]
  }
  environmental_factors: {
    air_quality: string
    pollution_exposure: boolean
  }
  living_environment: string  // 城市/农村/工业区

  // ==================== 女性特有因素（可选） ====================
  menstrual_status?: string  // 正常/异常/绝经
  pregnancy_history?: {
    pregnancy_count: number
    first_pregnancy_age?: number
  }
  breastfeeding_history?: {
    has_breastfed: boolean
    total_months?: number
  }
  hormone_therapy?: {
    contraceptive_use: boolean
    hrt_use: boolean
    duration_years?: number
  }

  // ==================== 精神压力与作息 ====================
  stress_level: string  // 低/中/高
  work_rest_pattern: string  // 规律/一般/不规律/经常熬夜
  mental_health: string  // 良好/一般/焦虑/抑郁

  // ==================== 体检与筛查历史 ====================
  screening_history: {
    last_checkup?: string
    tumor_markers?: boolean
    imaging?: boolean
    endoscopy?: boolean
  }
  abnormal_results_history: Array<{
    type: string
    date: string
    description: string
  }>
  last_checkup: string  // 从未/3年以上/1-3年/1年内/半年内

  // ==================== 症状自查 ====================
  symptoms: string[]
  recent_abnormalities: string[]

  // ==================== 备注 ====================
  notes?: string
}

/**
 * 评估响应数据类型
 */
export interface AssessmentV2Response {
  assessment_id: string
  questionnaire_id: string
  report_id: string

  assessment_result: {
    overall_risk: {
      score: number
      level: string
      percentile: number
    }
    category_risks: Record<
      string,
      {
        score: number
        level: string
      }
    >
    key_factors: Array<{
      factor: string
      contribution: number
      direction: 'increase' | 'decrease'
      description: string
      importance: number
    }>
    recommendations: Array<{
      category: string
      title: string
      content: string
      priority: number
    }>
    ai_recommendation: string  // DeepSeek 生成的 AI 建议
  }

  user_profile: {
    age: number
    gender: string
    bmi: number
    smoking_status: number
    exercise_level: number
    stress_level: string
  }

  feature_importance: Array<{
    factor: string
    contribution: number
  }>

  shap_analysis: {
    values: number[]
    feature_values: Record<string, number>
  }

  model_info: {
    version: string
    feature_count: number
    inference_time_ms: number
    accuracy: number
    auc: number
  }

  created_at: string
}

/**
 * 提交问卷并获取风险评估
 */
export async function submitAssessmentV2(data: QuestionnaireV2Request) {
  console.log('API层 - 发送请求到:', '/api/v1/assessment/submit-v2')
  console.log('API层 - 请求数据:', data)
  
  try {
    const result = await request.post<AssessmentV2Response>({
      url: '/api/v1/assessment/submit-v2',
      data,
      showSuccessMessage: false,
      timeout: 60000  // 评估接口超时设置为 60 秒（1分钟）
    })
    
    console.log('API层 - 收到响应:', result)
    console.log('API层 - 响应类型:', typeof result)
    console.log('API层 - 是否为空:', result === null || result === undefined)
    
    if (!result) {
      console.error('API层 - 响应为空！这不正常，请检查：')
      console.error('   1. 后端是否正确返回了 data 字段')
      console.error('   2. 后端返回的 code 是否为 200')
      console.error('   3. 请在浏览器 Network 面板查看原始响应')
      throw new Error('后端返回数据为空')
    }
    
    return result
  } catch (error: any) {
    console.error('API层 - 请求失败:', error)
    console.error('错误详情:', {
      message: error.message,
      code: error.code,
      stack: error.stack
    })
    throw error
  }
}

/**
 * 获取评估历史记录（V2接口）
 */
export function fetchAssessmentHistoryV2(params: { page: number; page_size: number }) {
  return request.get<any>({
    url: '/api/v1/assessment/history-v2',
    params,
    timeout: 30000  // 30秒超时
  })
}

/**
 * 获取单个评估详情（V2接口）
 */
export function fetchAssessmentDetailV2(assessment_id: string) {
  return request.get<AssessmentV2Response>({
    url: `/api/v1/assessment/detail-v2/${assessment_id}`,
    timeout: 30000  // 30秒超时
  })
}

/**
 * 导出评估报告（V2格式）
 */
export function exportAssessmentV2(assessment_id: string) {
  return request.get<any>({
    url: `/api/v1/assessment/export-v2/${assessment_id}`,
    responseType: 'blob',
    timeout: 60000  // 导出PDF可能较慢，设置60秒超时
  })
}

