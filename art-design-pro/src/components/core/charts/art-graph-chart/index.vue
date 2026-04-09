<!-- 知识图谱 Graph Chart -->
<template>
  <div ref="chartRef" :style="{ height: props.height }" v-loading="props.loading"></div>
</template>

<script setup lang="ts">
  import type { EChartsOption } from '@/utils/echarts'
  import { useChartOps, useChartComponent } from '@/composables/useChart'

  interface GraphNode {
    id: string
    name: string
    type: string
    category: number
    size?: number
    symbolSize?: number
    description?: string
    itemStyle?: any
  }

  interface GraphEdge {
    source: string
    target: string
    relation?: string
    weight?: number
    lineStyle?: any
  }

  interface GraphCategory {
    name: string
    base?: string
  }

  interface GraphChartProps {
    height?: string
    loading?: boolean
    isEmpty?: boolean
    nodes?: GraphNode[]
    edges?: GraphEdge[]
    categories?: GraphCategory[]
    layout?: 'force' | 'circular' | 'none'
    roam?: boolean
    draggable?: boolean
    focusNodeAdjacency?: boolean
  }

  defineOptions({ name: 'ArtGraphChart' })

  const props = withDefaults(defineProps<GraphChartProps>(), {
    height: '600px',
    loading: false,
    isEmpty: false,
    nodes: () => [],
    edges: () => [],
    categories: () => [],
    layout: 'force',
    roam: true,
    draggable: true,
    focusNodeAdjacency: true
  })

  // 使用图表组件抽象
  const { chartRef, isDark, getAnimationConfig } = useChartComponent({
    props,
    checkEmpty: () => {
      return !props.nodes?.length
    },
    watchSources: [() => props.nodes, () => props.edges, () => props.categories],
    generateOptions: (): EChartsOption => {
      // 节点颜色配置（根据类别）
      const categoryColors = [
        '#ff4d4f', // 疾病 - 红色
        '#ffa940', // 风险因素 - 橙色
        '#1890ff', // 症状 - 蓝色
        '#52c41a', // 筛查方法 - 绿色
        '#722ed1' // 用户 - 紫色
      ]

      // 处理节点数据
      const nodes = props.nodes.map((node) => ({
        ...node,
        symbolSize: node.symbolSize || node.size || 40,
        label: {
          show: true,
          color: isDark.value ? '#fff' : '#333',
          fontSize: 12,
          fontWeight: (node.type === 'disease' || node.type === 'user' ? 'bold' : 'normal') as any
        },
        itemStyle: {
          color: node.itemStyle?.color || categoryColors[node.category] || '#1890ff',
          borderColor: isDark.value ? '#444' : '#fff',
          borderWidth: 2,
          shadowBlur: 10,
          shadowColor: 'rgba(0, 0, 0, 0.2)'
        },
        emphasis: {
          itemStyle: {
            borderWidth: 3,
            shadowBlur: 20
          },
          label: {
            fontSize: 14,
            fontWeight: 'bold' as any
          }
        }
      }))

      // 处理边数据
      const edges = props.edges.map((edge) => ({
        ...edge,
        label: {
          show: true,
          formatter: edge.relation || '',
          fontSize: 10,
          color: isDark.value ? '#aaa' : '#666'
        },
        lineStyle: {
          color: edge.lineStyle?.color || (isDark.value ? '#666' : '#ccc'),
          width: edge.lineStyle?.width || 2,
          type: edge.lineStyle?.type || 'solid',
          curveness: 0.2,
          opacity: 0.8
        },
        emphasis: {
          lineStyle: {
            width: (edge.lineStyle?.width || 2) + 1,
            opacity: 1
          },
          label: {
            fontSize: 12,
            fontWeight: 'bold' as any
          }
        }
      }))

      return {
        title: {
          show: false
        },
        tooltip: {
          trigger: 'item',
          formatter: (params: any) => {
            if (params.dataType === 'node') {
              const node = params.data
              return `
                <div style="padding: 8px;">
                  <div style="font-weight: bold; font-size: 14px; margin-bottom: 4px;">${node.name}</div>
                  ${node.description ? `<div style="color: #666; font-size: 12px;">${node.description}</div>` : ''}
                  <div style="color: #999; font-size: 11px; margin-top: 4px;">类型: ${props.categories[node.category]?.name || '未知'}</div>
                </div>
              `
            } else if (params.dataType === 'edge') {
              const edge = params.data
              return `
                <div style="padding: 8px;">
                  <div style="font-size: 12px;">${edge.source} → ${edge.target}</div>
                  ${edge.relation ? `<div style="color: #666; font-size: 12px; margin-top: 4px;">关系: ${edge.relation}</div>` : ''}
                  ${edge.weight ? `<div style="color: #999; font-size: 11px; margin-top: 2px;">权重: ${edge.weight}</div>` : ''}
                </div>
              `
            }
            return ''
          },
          backgroundColor: isDark.value ? 'rgba(0, 0, 0, 0.8)' : 'rgba(255, 255, 255, 0.95)',
          borderColor: isDark.value ? '#444' : '#ddd',
          borderWidth: 1,
          textStyle: {
            color: isDark.value ? '#fff' : '#333'
          }
        },
        legend: {
          show: false
        },
        series: [
          {
            type: 'graph',
            layout: props.layout,
            data: nodes,
            links: edges,
            categories: props.categories,
            roam: props.roam,
            draggable: props.draggable,
            emphasis: {
              focus: props.focusNodeAdjacency ? 'adjacency' : 'none'
            },
            edgeSymbol: ['none', 'arrow'],
            edgeSymbolSize: [0, 8],
            label: {
              show: true,
              position: 'bottom'
            },
            force: {
              repulsion: 500,
              edgeLength: [100, 200],
              gravity: 0.1,
              friction: 0.3,
              layoutAnimation: true
            },
            ...getAnimationConfig(500, 2000)
          }
        ] as any
      }
    }
  })
</script>

<style lang="scss" scoped>
  // 样式
</style>

