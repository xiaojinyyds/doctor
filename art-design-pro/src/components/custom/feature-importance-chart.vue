<template>
  <ElCard class="feature-importance-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <h3>
          <i class="iconfont-sys">&#xe7a3;</i>
          特征重要性排行 Top {{ displayCount }}
        </h3>
        <p class="subtitle">影响风险评估的关键因素</p>
      </div>
    </template>

    <div class="chart-container">
      <ElSkeleton :loading="loading" :rows="5" animated>
        <template #default>
          <div v-if="features && features.length > 0" ref="chartRef" class="chart"></div>
          <ElEmpty v-else description="暂无数据" />
        </template>
      </ElSkeleton>
    </div>
  </ElCard>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'

interface Feature {
  factor: string
  contribution: number
  direction?: 'increase' | 'decrease'
  importance?: number
}

interface Props {
  features?: Feature[]
  loading?: boolean
  displayCount?: number
}

const props = withDefaults(defineProps<Props>(), {
  features: () => [],
  loading: false,
  displayCount: 10
})

const chartRef = ref<HTMLDivElement>()
let chartInstance: echarts.ECharts | null = null

// 特征名称中英文映射
const featureNameMap: Record<string, string> = {
  age: '年龄',
  gender: '性别',
  bmi: 'BMI指数',
  smoking_status: '吸烟状态',
  alcohol_status: '饮酒状态',
  exercise_level: '运动水平',
  genetic_risk: '遗传风险',
  family_history: '家族肿瘤史',
  stress_level_score: '压力水平',
  diet_quality_score: '饮食质量',
  comprehensive_risk: '综合风险因子',
  lifestyle_score: '生活方式评分',
  age_x_smoking: '年龄×吸烟',
  age_x_genetic: '年龄×遗传',
  tumor_marker_score: '肿瘤标志物',
  tissue_abnormality: '组织异常',
  screening_history_score: '筛查历史',
  reproductive_risk_score: '生育相关风险',
  occupational_exposure_score: '职业暴露',
  environmental_risk_score: '环境风险'
}

const initChart = () => {
  if (!chartRef.value || !props.features || props.features.length === 0) return

  if (chartInstance) {
    chartInstance.dispose()
  }

  chartInstance = echarts.init(chartRef.value)

  // 取前N个特征
  const topFeatures = props.features
    .sort((a, b) => Math.abs(b.contribution) - Math.abs(a.contribution))
    .slice(0, props.displayCount)
    .reverse()

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: (params: any) => {
        const data = params[0]
        const contribution = data.value
        const direction = contribution > 0 ? '增加' : '降低'
        const color = contribution > 0 ? '#f56c6c' : '#67c23a'
        return `
          <div style="padding: 8px;">
            <div style="font-weight: 600; margin-bottom: 4px;">${data.name}</div>
            <div style="color: ${color};">
              ${direction}风险: ${Math.abs(contribution).toFixed(4)}
            </div>
          </div>
        `
      }
    },
    grid: {
      left: '25%',
      right: '10%',
      top: '5%',
      bottom: '5%'
    },
    xAxis: {
      type: 'value',
      axisLabel: {
        formatter: (value: number) => value.toFixed(2)
      },
      splitLine: {
        lineStyle: {
          type: 'dashed',
          color: '#e4e7ed'
        }
      }
    },
    yAxis: {
      type: 'category',
      data: topFeatures.map((f) => featureNameMap[f.factor] || f.factor),
      axisLabel: {
        fontSize: 13,
        color: '#606266'
      }
    },
    series: [
      {
        name: '特征贡献度',
        type: 'bar',
        data: topFeatures.map((f) => f.contribution),
        itemStyle: {
          color: (params: any) => {
            return params.value > 0 ? '#f56c6c' : '#67c23a'
          },
          borderRadius: [0, 4, 4, 0]
        },
        label: {
          show: true,
          position: 'right',
          formatter: (params: any) => {
            return params.value > 0
              ? `+${params.value.toFixed(3)}`
              : params.value.toFixed(3)
          },
          fontSize: 12,
          color: '#606266'
        }
      }
    ]
  }

  chartInstance.setOption(option)
}

// 响应式调整
const handleResize = () => {
  chartInstance?.resize()
}

onMounted(() => {
  if (!props.loading && props.features && props.features.length > 0) {
    initChart()
  }
  window.addEventListener('resize', handleResize)
})

watch(
  () => [props.features, props.loading],
  () => {
    if (!props.loading && props.features && props.features.length > 0) {
      setTimeout(() => initChart(), 100)
    }
  },
  { deep: true }
)

onBeforeUnmount(() => {
  chartInstance?.dispose()
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped lang="scss">
.feature-importance-card {
  margin-bottom: 20px;
  border-radius: 12px;

  .card-header {
    h3 {
      margin: 0 0 8px 0;
      font-size: 18px;
      font-weight: 600;
      color: var(--art-text-gray-900);
      display: flex;
      align-items: center;
      gap: 8px;

      .iconfont-sys {
        color: var(--el-color-primary);
        font-size: 20px;
      }
    }

    .subtitle {
      margin: 0;
      font-size: 13px;
      color: var(--art-text-gray-500);
    }
  }

  .chart-container {
    min-height: 400px;
    padding: 10px 0;

    .chart {
      width: 100%;
      height: 400px;
    }
  }
}
</style>

