<template>
  <div ref="chartRef" class="risk-radar-chart" :style="{ height: height }"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import type { EChartsOption } from 'echarts'

interface CategoryRisk {
  name: string
  value: number // 0-100
  level: string
}

interface Props {
  data: CategoryRisk[]
  height?: string
}

const props = withDefaults(defineProps<Props>(), {
  height: '400px',
  data: () => []
})

const chartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null

const initChart = () => {
  if (!chartRef.value || props.data.length === 0) return

  chartInstance = echarts.init(chartRef.value)

  const indicator = props.data.map(item => ({
    name: item.name,
    max: 100
  }))

  const values = props.data.map(item => item.value)

  const option: EChartsOption = {
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        const data = params.data
        if (data && data.value) {
          return props.data
            .map(
              (item, index) =>
                `${item.name}: ${data.value[index]}分 (${item.level})`
            )
            .join('<br/>')
        }
        return ''
      }
    },
    radar: {
      indicator: indicator,
      shape: 'polygon',
      splitNumber: 4,
      center: ['50%', '50%'],
      radius: '65%',
      axisName: {
        color: '#666',
        fontSize: 14,
        fontWeight: 'bold'
      },
      splitLine: {
        lineStyle: {
          color: '#e5e5e5'
        }
      },
      splitArea: {
        show: true,
        areaStyle: {
          color: ['rgba(24, 144, 255, 0.05)', 'rgba(24, 144, 255, 0.1)', 'rgba(24, 144, 255, 0.05)', 'rgba(24, 144, 255, 0.1)']
        }
      },
      axisLine: {
        lineStyle: {
          color: '#e5e5e5'
        }
      }
    },
    series: [
      {
        type: 'radar',
        data: [
          {
            value: values,
            name: '风险评分',
            areaStyle: {
              color: new echarts.graphic.RadialGradient(0.5, 0.5, 1, [
                {
                  color: 'rgba(24, 144, 255, 0.4)',
                  offset: 0
                },
                {
                  color: 'rgba(24, 144, 255, 0.1)',
                  offset: 1
                }
              ])
            },
            lineStyle: {
              color: '#1890ff',
              width: 3
            },
            itemStyle: {
              color: '#1890ff',
              borderWidth: 3,
              borderColor: '#fff'
            },
            label: {
              show: true,
              formatter: (params: any) => {
                return params.value + '分'
              },
              color: '#1890ff',
              fontSize: 13,
              fontWeight: 'bold'
            }
          }
        ]
      }
    ]
  }

  chartInstance.setOption(option)
}

const updateChart = () => {
  if (!chartInstance || props.data.length === 0) return

  const indicator = props.data.map(item => ({
    name: item.name,
    max: 100
  }))

  const values = props.data.map(item => item.value)

  chartInstance.setOption({
    radar: {
      indicator: indicator
    },
    series: [
      {
        data: [
          {
            value: values
          }
        ]
      }
    ]
  })
}

watch(
  () => props.data,
  () => {
    if (chartInstance) {
      updateChart()
    } else {
      initChart()
    }
  },
  { deep: true }
)

const handleResize = () => {
  chartInstance?.resize()
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
})
</script>

<style scoped lang="scss">
.risk-radar-chart {
  width: 100%;
}
</style>
