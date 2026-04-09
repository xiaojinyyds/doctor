import { AppRouteRecord } from '@/types/router'

/**
 * 健康问卷路由
 * 所有登录用户都可以访问（user, doctor, admin）
 */
export const questionnaireRoutes: AppRouteRecord = {
  path: '/questionnaire',
  name: 'Questionnaire',
  component: '/questionnaire/index',
  meta: {
    title: '健康问卷',
    icon: '&#xe788;', // 文档图标
    roles: ['user', 'doctor', 'admin'],
    keepAlive: false
  }
}

/**
 * 问卷评估中页面（独立路由）
 */
export const evaluatingRoutes: AppRouteRecord = {
  path: '/questionnaire/evaluating',
  name: 'Evaluating',
  component: '/questionnaire/evaluating',
  meta: {
    title: '评估中',
    keepAlive: false,
    isHide: true,
    isHideTab: true
  }
}
