<template>
  <div ref="chartRef" class="risk-gauge-chart" :style="{ height: height }"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import type { EChartsOption } from 'echarts'

interface Props {
  value: number // 风险分数 0-100
  level: string // 风险等级
  height?: string
}

const props = withDefaults(defineProps<Props>(), {
  height: '300px'
})

const chartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null

// 根据风险等级获取颜色
const getRiskColor = (level: string): [number, string][] => {
  return [
    [0.4, '#52c41a'], // 低风险 - 绿色
    [0.6, '#faad14'], // 中风险 - 黄色
    [0.8, '#fa8c16'], // 高风险 - 橙色
    [1, '#f5222d']    // 极高风险 - 红色
  ]
}

const initChart = () => {
  if (!chartRef.value) return

  chartInstance = echarts.init(chartRef.value)

  const option: EChartsOption = {
    series: [
      {
        type: 'gauge',
        startAngle: 180,
        endAngle: 0,
        min: 0,
        max: 100,
        splitNumber: 4,
        center: ['50%', '75%'],
        radius: '90%',
        axisLine: {
          lineStyle: {
            width: 30,
            color: getRiskColor(props.level)
          }
        },
        pointer: {
          icon: 'path://M12.8,0.7l12,40.1H0.7L12.8,0.7z',
          length: '70%',
          width: 10,
          offsetCenter: [0, '-60%'],
          itemStyle: {
            color: 'auto'
          }
        },
        axisTick: {
          length: 12,
          lineStyle: {
            color: 'auto',
            width: 2
          }
        },
        splitLine: {
          length: 20,
          lineStyle: {
            color: 'auto',
            width: 3
          }
        },
        axisLabel: {
          color: '#464646',
          fontSize: 14,
          distance: -60,
          formatter: function (value) {
            if (value === 100) {
              return '极高'
            } else if (value === 80) {
              return '高'
            } else if (value === 60) {
              return '中'
            } else if (value === 40) {
              return '低'
            }
            return ''
          }
        },
        title: {
          offsetCenter: [0, '-20%'],
          fontSize: 18,
          color: '#999'
        },
        detail: {
          fontSize: 48,
          offsetCenter: [0, '0%'],
          valueAnimation: true,
          formatter: function (value) {
            return Math.round(value) + ''
          },
          color: 'auto'
        },
        data: [
          {
            value: props.value,
            name: '风险分数'
          }
        ]
      }
    ]
  }

  chartInstance.setOption(option)
}

const updateChart = () => {
  if (chartInstance) {
    chartInstance.setOption({
      series: [
        {
          data: [
            {
              value: props.value,
              name: '风险分数'
            }
          ]
        }
      ]
    })
  }
}

// 监听props变化
watch(
  () => props.value,
  () => {
    updateChart()
  }
)

// 监听窗口大小变化
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
.risk-gauge-chart {
  width: 100%;
}
</style>

