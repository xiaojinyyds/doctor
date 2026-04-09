<template>
  <div ref="chartRef" class="shap-waterfall-chart" :style="{ height: height }"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import type { EChartsOption } from 'echarts'

interface Factor {
  factor: string
  contribution: number // SHAP值
  direction: 'increase' | 'decrease'
  description: string
}

interface Props {
  factors: Factor[]
  baseline?: number
  height?: string
}

const props = withDefaults(defineProps<Props>(), {
  baseline: 50,
  height: '400px',
  factors: () => []
})

const chartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null

const initChart = () => {
  if (!chartRef.value || props.factors.length === 0) return

  chartInstance = echarts.init(chartRef.value)

  // 计算累计值
  let cumulative = props.baseline
  const data = props.factors.map((item) => {
    const value = item.contribution * 100 // 转为分数
    const start = cumulative
    cumulative += value
    return {
      name: item.factor,
      value: [start, cumulative],
      contribution: value,
      direction: item.direction,
      description: item.description
    }
  })

  // 添加基线和最终值
  const categories = ['基线', ...props.factors.map(f => f.factor), '最终分数']
  
  const option: EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: (params: any) => {
        const item = params[0]
        const factorData = props.factors.find(f => f.factor === item.name)
        if (factorData) {
          return `
            <strong>${item.name}</strong><br/>
            贡献度: ${factorData.contribution > 0 ? '+' : ''}${(factorData.contribution * 100).toFixed(1)}分<br/>
            ${factorData.description}
          `
        }
        return item.name
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: categories,
      axisLabel: {
        interval: 0,
        rotate: 30,
        fontSize: 12
      }
    },
    yAxis: {
      type: 'value',
      name: '风险分数',
      min: 0,
      max: 100,
      axisLabel: {
        formatter: '{value}分'
      }
    },
    series: [
      {
        type: 'bar',
        stack: 'total',
        itemStyle: {
          color: 'transparent'
        },
        data: [
          props.baseline,
          ...data.map(d => d.value[0])
        ]
      },
      {
        type: 'bar',
        stack: 'total',
        label: {
          show: true,
          position: 'top',
          formatter: (params: any) => {
            const index = params.dataIndex
            if (index === 0) {
              return props.baseline + '分'
            } else if (index <= props.factors.length) {
              const factor = props.factors[index - 1]
              const value = factor.contribution * 100
              return (value > 0 ? '+' : '') + value.toFixed(1)
            } else {
              return cumulative.toFixed(0) + '分'
            }
          }
        },
        itemStyle: {
          color: (params: any) => {
            const index = params.dataIndex
            if (index === 0 || index > props.factors.length) {
              return '#1890ff'
            }
            const factor = props.factors[index - 1]
            return factor.direction === 'increase' ? '#f5222d' : '#52c41a'
          }
        },
        data: [
          0,
          ...data.map(d => d.contribution),
          0
        ]
      }
    ]
  }

  chartInstance.setOption(option)
}

watch(
  () => props.factors,
  () => {
    if (chartInstance) {
      chartInstance.dispose()
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
.shap-waterfall-chart {
  width: 100%;
}
</style>

