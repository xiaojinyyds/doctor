import { AppRouteRecord } from '@/types/router'

/**
 * 医生专用路由（B2B升级）
 */
export const doctorRoutes: AppRouteRecord = {
  path: '/doctor',
  name: 'Doctor',
  component: '/index/index',
  redirect: '/doctor/pending',
  meta: {
    title: '医生工作台',
    icon: '&#xe734;', // 医生图标
    roles: ['doctor', 'admin'], // 医生和管理员可访问
    keepAlive: true
  },
  children: [
    {
      path: '/doctor/pending',
      name: 'DoctorPending',
      component: '/doctor/pending-list',
      meta: {
        title: '待审核列表',
        icon: '&#xe621;',
        roles: ['doctor', 'admin'],
        keepAlive: true
      }
    },
    {
      path: '/doctor/diagnosis',
      name: 'DoctorDiagnosis',
      component: '/doctor/diagnosis-workbench',
      meta: {
        title: '诊断工作台',
        icon: '&#xe621;',
        roles: ['doctor', 'admin'],
        keepAlive: true
      }
    }
  ]
}

