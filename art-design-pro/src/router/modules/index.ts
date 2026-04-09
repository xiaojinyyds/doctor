import { AppRouteRecord } from '@/types/router'
import { dashboardRoutes } from './dashboard'
import { systemRoutes } from './system'
import { questionnaireRoutes, evaluatingRoutes } from './questionnaire'
import { reportRoutes } from './report'
import { historyRoutes } from './history'
import { resultRoutes } from './result'
import { exceptionRoutes } from './exception'
import { riskRoutes } from './risk'
import { knowledgeRoutes } from './knowledge'
import { medicalImageRoutes } from './medical-image'
import { doctorRoutes } from './doctor'

/**
 * 导出所有模块化路由
 */
export const routeModules: AppRouteRecord[] = [
  dashboardRoutes,
  questionnaireRoutes,
  evaluatingRoutes,
  medicalImageRoutes,
  doctorRoutes,  // 医生工作台
  reportRoutes,
  historyRoutes,
  knowledgeRoutes,
  systemRoutes,
  riskRoutes,
  resultRoutes,
  exceptionRoutes
]
