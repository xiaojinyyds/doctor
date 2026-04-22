<template>
  <div ref="chartRef" class="risk-trend-chart" :style="{ height: height }"></div>
</template>

<script setup lang="ts">
  import { ref, onMounted, watch, onBeforeUnmount, computed } from 'vue'
  import * as echarts from 'echarts'
  import type { EChartsOption } from 'echarts'

  interface TrendDataItem {
    date: string
    month: string
    overall_score: number
    overall_level: string
    category_scores: {
      lung: number
      liver: number
      stomach: number
      colorectal: number
      breast: number
      esophageal: number
    }
  }

  interface Props {
    data: TrendDataItem[]
    height?: string
    showCategoryLines?: boolean
    markEvents?: Array<{
      index: number
      label: string
      type: 'positive' | 'negative' | 'neutral'
    }>
  }

  const props = withDefaults(defineProps<Props>(), {
    height: '450px',
    data: () => [],
    showCategoryLines: true,
    markEvents: () => []
  })

  const chartRef = ref<HTMLElement>()
  let chartInstance: echarts.ECharts | null = null

  // 分类风险名称映射
  const categoryNames: Record<string, string> = {
    lung: '肺癌',
    liver: '肝癌',
    stomach: '胃癌',
    colorectal: '肠癌',
    breast: '乳腺癌',
    esophageal: '食管癌'
  }

  // 分类风险颜色
  const categoryColors: Record<string, string> = {
    lung: '#ff6b6b',
    liver: '#feca57',
    stomach: '#48dbfb',
    colorectal: '#ff9ff3',
    breast: '#54a0ff',
    esophageal: '#5f27cd'
  }

  const getLevelColor = (level: string) => {
    switch (level) {
      case '低风险':
        return '#52c41a'
      case '中风险':
        return '#faad14'
      case '高风险':
        return '#f5222d'
      default:
        return '#1890ff'
    }
  }

  const initChart = () => {
    if (!chartRef.value || props.data.length === 0) return

    chartInstance = echarts.init(chartRef.value)

    const dates = props.data.map((item) => item.date)
    const months = props.data.map((item) => item.month)
    const overallScores = props.data.map((item) => (item.overall_score * 100).toFixed(1))

    // 构建 markPoint 数据
    const markPointData = props.markEvents.map((event) => ({
      coord: [event.index, overallScores[event.index]],
      value: event.label,
      itemStyle: {
        color:
          event.type === 'positive'
            ? '#52c41a'
            : event.type === 'negative'
              ? '#f5222d'
              : '#faad14'
      }
    }))

    const series: any[] = [
      {
        name: '综合风险',
        type: 'line',
        data: overallScores,
        smooth: true,
        symbol: 'circle',
        symbolSize: 10,
        lineStyle: {
          width: 4,
          color: '#1890ff'
        },
        itemStyle: {
          color: '#1890ff',
          borderWidth: 3,
          borderColor: '#fff'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            {
              offset: 0,
              color: 'rgba(24, 144, 255, 0.3)'
            },
            {
              offset: 1,
              color: 'rgba(24, 144, 255, 0.05)'
            }
          ])
        },
        markPoint: {
          data: markPointData,
          symbol: 'pin',
          symbolSize: 40,
          label: {
            show: true,
            formatter: '{c}',
            fontSize: 10
          }
        }
      }
    ]

    // 添加各分类风险线
    if (props.showCategoryLines) {
      const categories = ['lung', 'liver', 'stomach', 'colorectal', 'breast', 'esophageal']
      categories.forEach((cat) => {
        const catData = props.data.map((item) => (item.category_scores[cat] * 100).toFixed(1))
        series.push({
          name: categoryNames[cat],
          type: 'line',
          data: catData,
          smooth: true,
          symbol: 'circle',
          symbolSize: 6,
          lineStyle: {
            width: 2,
            type: 'dashed',
            color: categoryColors[cat]
          },
          itemStyle: {
            color: categoryColors[cat]
          }
        })
      })
    }

    const option: EChartsOption = {
      title: {
        text: '风险趋势追踪',
        left: 'center',
        top: 10,
        textStyle: {
          fontSize: 18,
          fontWeight: 'bold',
          color: '#333'
        }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross'
        },
        formatter: (params: any) => {
          const index = params[0].dataIndex
          const item = props.data[index]
          let html = `<div style="padding: 10px;">`
          html += `<div style="font-weight: bold; margin-bottom: 8px; font-size: 14px;">${item.date}</div>`
          html += `<div style="margin-bottom: 5px;">`
          html += `<span style="display: inline-block; width: 10px; height: 10px; background: #1890ff; border-radius: 50%; margin-right: 5px;"></span>`
          html += `综合风险: <strong>${(item.overall_score * 100).toFixed(1)}分</strong> (${item.overall_level})`
          html += `</div>`

          if (props.showCategoryLines) {
            html += `<div style="margin-top: 8px; padding-top: 8px; border-top: 1px dashed #eee; font-size: 12px; color: #666;">分类风险:</div>`
            Object.entries(item.category_scores).forEach(([key, value]) => {
              html += `<div style="margin: 3px 0; font-size: 11px;">`
              html += `<span style="display: inline-block; width: 8px; height: 8px; background: ${categoryColors[key]}; border-radius: 50%; margin-right: 5px;"></span>`
              html += `${categoryNames[key]}: ${(value * 100).toFixed(1)}分`
              html += `</div>`
            })
          }

          html += `</div>`
          return html
        }
      },
      legend: {
        data: ['综合风险', ...Object.values(categoryNames)],
        bottom: 0,
        icon: 'circle',
        itemWidth: 10,
        itemHeight: 10,
        textStyle: {
          fontSize: 12
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '15%',
        top: '15%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: dates,
        axisLabel: {
          rotate: 30,
          fontSize: 11,
          color: '#666'
        },
        axisLine: {
          lineStyle: {
            color: '#e5e5e5'
          }
        }
      },
      yAxis: {
        type: 'value',
        name: '风险评分',
        max: 100,
        axisLabel: {
          formatter: '{value}分',
          color: '#666'
        },
        splitLine: {
          lineStyle: {
            color: '#f0f0f0'
          }
        }
      },
      series: series
    }

    chartInstance.setOption(option)
  }

  const updateChart = () => {
    if (!chartInstance || props.data.length === 0) return
    initChart() // 重新初始化以更新完整配置
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

  watch(
    () => props.markEvents,
    () => {
      if (chartInstance) {
        updateChart()
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
  .risk-trend-chart {
    width: 100%;
  }
</style>
