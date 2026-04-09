import { AppRouteRecord } from '@/types/router'

/**
 * 知识图谱路由
 */
export const knowledgeRoutes: AppRouteRecord = {
  path: '/knowledge',
  name: 'KnowledgeGraph',
  component: '/dashboard/knowledge-graph',
  meta: {
    title: '知识图谱',
    icon: '&#xe753;',
    roles: ['user'],
    keepAlive: true
  }
}

