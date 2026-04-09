import { AppRouteRecord } from '@/types/router'

/**
 * 医生专用路由
 */
export const doctorRoutes: AppRouteRecord = {
  path: '/doctor',
  name: 'Doctor',
  component: '/index/index',
  redirect: '/doctor/diagnosis',
  meta: {
    title: '医生工作台',
    icon: '&#xe734;', // 医生图标
    roles: ['doctor', 'admin'], // 医生和管理员可访问
    keepAlive: true
  },
  children: [
    {
      path: '/doctor/diagnosis',
      name: 'DoctorDiagnosis',
      component: '/doctor/diagnosis-workbench',
      meta: {
        title: '诊断审核',
        icon: '&#xe621;',
        roles: ['doctor', 'admin'],
        keepAlive: true
      }
    }
  ]
}

