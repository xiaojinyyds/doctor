<template>
  <div class="medical-image-statistics-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">
        <i class="iconfont-sys">&#xe61b;</i>
        影像分析统计
      </h1>
      <el-select v-model="timePeriod" @change="loadData" class="period-select">
        <el-option label="最近7天" :value="7" />
        <el-option label="最近30天" :value="30" />
        <el-option label="最近90天" :value="90" />
        <el-option label="最近一年" :value="365" />
      </el-select>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="16" class="stats-cards">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon" style="background: rgba(103, 194, 58, 0.1)">
            <i class="iconfont-sys stat-icon-item" style="color: #67c23a">&#xe667;</i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ statistics.total_images || 0 }}</div>
            <div class="stat-label">总影像数</div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon" style="background: rgba(64, 158, 255, 0.1)">
            <i class="iconfont-sys stat-icon-item" style="color: #409eff">&#xe621;</i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ statistics.analyzed_images || 0 }}</div>
            <div class="stat-label">已分析</div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon" style="background: rgba(245, 108, 108, 0.1)">
            <i class="iconfont-sys stat-icon-item" style="color: #f56c6c">&#xe86e;</i>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ statistics.high_risk_count || 0 }}</div>
            <div class="stat-label">高风险</div>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-icon" style="background: rgba(103, 194, 58, 0.1)">
            <i class="iconfont-sys stat-icon-item" style="color: #67c23a">&#xe7a5;</i>
          </div>
          <div class="stat-content">
            <div class="stat-value">
              {{ statistics.average_confidence ? (statistics.average_confidence * 100).toFixed(1) + '%' : '-' }}
            </div>
            <div class="stat-label">平均置信度</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="16">
      <!-- 分类分布饼图 -->
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>分类分布</span>
            </div>
          </template>
          <div ref="distributionChartRef" class="chart" style="height: 350px"></div>
        </el-card>
      </el-col>

      <!-- 风险趋势折线图 -->
      <el-col :xs="24" :lg="12">
        <el-card class="chart-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>风险趋势</span>
            </div>
          </template>
          <div ref="trendChartRef" class="chart" style="height: 350px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 详细统计表格 -->
    <el-card class="table-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <i class="iconfont-sys">&#xe7b5;</i>
          <span>详细分析数据</span>
        </div>
      </template>
      <el-table :data="recentAnalyses" stripe>
        <el-table-column label="序号" type="index" width="60" align="center" />
        <el-table-column label="预测类别" prop="predicted_class" min-width="120">
          <template #default="{ row }">
            <div class="class-cell">
              <i class="iconfont-sys" :style="{ color: getClassColor(row.predicted_class) }">&#xe667;</i>
              <span>{{ row.predicted_class }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="置信度" min-width="120">
          <template #default="{ row }">
            <el-progress 
              :percentage="parseFloat((row.confidence * 100).toFixed(2))" 
              :color="getConfidenceColor(row.confidence)"
              :stroke-width="8"
            >
              <span class="progress-text">{{ (row.confidence * 100).toFixed(2) }}%</span>
            </el-progress>
          </template>
        </el-table-column>
        <el-table-column label="风险等级" min-width="100">
          <template #default="{ row }">
            <el-tag :type="getRiskTagType(row.risk_level)" size="default" effect="light">
              <i class="iconfont-sys">&#xe86e;</i>
              {{ row.risk_level }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="分析时间" min-width="180">
          <template #default="{ row }">
            <div class="time-cell">
              <i class="iconfont-sys">&#xe7a3;</i>
              <span>{{ formatDateTime(row.analyzed_at) }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="影像ID" min-width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" type="info">{{ row.id || '-' }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { medicalImageAPI } from '@/api/medical-image'
import * as echarts from 'echarts'

// 状态
const timePeriod = ref(30)
const statistics = ref<any>({})
const trendData = ref<any[]>([])
const recentAnalyses = ref<any[]>([])

// 图表引用
const distributionChartRef = ref<HTMLElement>()
const trendChartRef = ref<HTMLElement>()
let distributionChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null

// 加载数据
const loadData = async () => {
  try {
    // 加载统计数据（HTTP工具已自动提取data字段）
    const statsResponse: any = await medicalImageAPI.getStatistics(timePeriod.value)
    statistics.value = statsResponse.statistics

    // 加载趋势数据
    const trendResponse: any = await medicalImageAPI.getRiskTrend(timePeriod.value)
    trendData.value = trendResponse.trend

    // 加载仪表板数据（包含最近分析）
    const dashboardResponse: any = await medicalImageAPI.getDashboard()
    recentAnalyses.value = dashboardResponse.recent_analyses

    // 更新图表
    await nextTick()
    initCharts()
  } catch (error) {
    ElMessage.error('加载数据失败')
    console.error(error)
  }
}

// 初始化图表
const initCharts = () => {
  initDistributionChart()
  initTrendChart()
}

// 初始化分类分布饼图
const initDistributionChart = () => {
  if (!distributionChartRef.value) return

  if (distributionChart) {
    distributionChart.dispose()
  }

  distributionChart = echarts.init(distributionChartRef.value)

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center'
    },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}\n{d}%'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        data: [
          {
            value: statistics.value.distribution?.['正常'] || 0,
            name: '正常',
            itemStyle: { color: '#67C23A' }
          },
          {
            value: statistics.value.distribution?.['良性肿瘤'] || 0,
            name: '良性肿瘤',
            itemStyle: { color: '#E6A23C' }
          },
          {
            value: statistics.value.distribution?.['恶性肿瘤'] || 0,
            name: '恶性肿瘤',
            itemStyle: { color: '#F56C6C' }
          }
        ]
      }
    ]
  }

  distributionChart.setOption(option)
}

// 初始化风险趋势折线图
const initTrendChart = () => {
  if (!trendChartRef.value) return

  if (trendChart) {
    trendChart.dispose()
  }

  trendChart = echarts.init(trendChartRef.value)

  // 处理趋势数据
  const dates = trendData.value.map((item) => item.date)
  const riskScores = trendData.value.map((item) => (item.risk_score * 100).toFixed(2))
  const confidences = trendData.value.map((item) => (item.confidence * 100).toFixed(2))

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['风险分数', '置信度']
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100,
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series: [
      {
        name: '风险分数',
        type: 'line',
        data: riskScores,
        smooth: true,
        itemStyle: { color: '#F56C6C' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(245, 108, 108, 0.3)' },
            { offset: 1, color: 'rgba(245, 108, 108, 0.05)' }
          ])
        }
      },
      {
        name: '置信度',
        type: 'line',
        data: confidences,
        smooth: true,
        itemStyle: { color: '#409EFF' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
          ])
        }
      }
    ]
  }

  trendChart.setOption(option)
}

// 获取风险标签类型
const getRiskTagType = (riskLevel: string) => {
  if (riskLevel === '低风险') return 'success'
  if (riskLevel === '中风险') return 'warning'
  return 'danger'
}

// 格式化日期时间
const formatDateTime = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

// 获取分类颜色
const getClassColor = (className: string) => {
  if (className?.includes('正常')) return '#67c23a'
  if (className?.includes('良性')) return '#e6a23c'
  if (className?.includes('恶性')) return '#f56c6c'
  return '#909399'
}

// 获取置信度颜色
const getConfidenceColor = (confidence: number) => {
  if (confidence >= 0.9) return '#67c23a'
  if (confidence >= 0.7) return '#409eff'
  if (confidence >= 0.5) return '#e6a23c'
  return '#f56c6c'
}

// 页面挂载
onMounted(() => {
  loadData()

  // 响应式处理
  window.addEventListener('resize', () => {
    distributionChart?.resize()
    trendChart?.resize()
  })
})

// 页面卸载
onUnmounted(() => {
  distributionChart?.dispose()
  trendChart?.dispose()
  window.removeEventListener('resize', () => {})
})
</script>

<style scoped lang="scss">
.medical-image-statistics-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;

  .page-title {
    font-size: 24px;
    font-weight: 600;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .period-select {
    width: 150px;
  }
}

.stats-cards {
  margin-bottom: 24px;

  .stat-card {
    :deep(.el-card__body) {
      display: flex;
      align-items: center;
      gap: 16px;
      padding: 20px;
    }

    .stat-icon {
      width: 60px;
      height: 60px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;

      .stat-icon-item {
        font-size: 28px;
        line-height: 1;
      }
    }

    .stat-content {
      flex: 1;

      .stat-value {
        font-size: 28px;
        font-weight: 600;
        color: var(--el-text-color-primary);
        margin-bottom: 4px;
      }

      .stat-label {
        font-size: 14px;
        color: var(--el-text-color-secondary);
      }
    }
  }
}

.chart-card,
.table-card {
  margin-bottom: 16px;

  .card-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 16px;
    font-weight: 600;

    .iconfont-sys {
      font-size: 18px;
      color: var(--el-color-primary);
    }
  }

  .chart {
    width: 100%;
  }
}

// 表格样式优化
.class-cell {
  display: flex;
  align-items: center;
  gap: 8px;

  .iconfont-sys {
    font-size: 16px;
  }
}

.time-cell {
  display: flex;
  align-items: center;
  gap: 6px;

  .iconfont-sys {
    font-size: 14px;
    color: var(--el-text-color-secondary);
  }
}

.progress-text {
  font-size: 12px;
  font-weight: 500;
}

:deep(.el-table) {
  .el-table__row {
    &:hover {
      background-color: var(--el-fill-color-light);
    }
  }

  .el-tag {
    .iconfont-sys {
      font-size: 12px;
      margin-right: 4px;
    }
  }
}
</style>

