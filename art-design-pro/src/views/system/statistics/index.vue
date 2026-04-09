<template>
  <div class="statistics-page">
    <!-- 统计卡片 -->
    <ElRow :gutter="20" class="stats-cards">
      <ElCol :xs="24" :sm="12" :md="6">
        <ElCard shadow="hover" class="stat-card">
          <div class="stat-content">
            <div
              class="stat-icon"
              style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
            >
              <i class="iconfont-sys">&#xe7ae;</i>
            </div>
            <div class="stat-data">
              <div class="stat-value">{{ statistics.totalUsers }}</div>
              <div class="stat-label">总用户数</div>
              <div class="stat-trend">
                <span style="color: #52c41a">{{ statistics.todayNewUsers }}</span> 今日新增用户
              </div>
            </div>
          </div>
        </ElCard>
      </ElCol>
      <ElCol :xs="24" :sm="12" :md="6">
        <ElCard shadow="hover" class="stat-card">
          <div class="stat-content">
            <div
              class="stat-icon"
              style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%)"
            >
              <i class="iconfont-sys">&#xe7b5;</i>
            </div>
            <div class="stat-data">
              <div class="stat-value">{{ statistics.totalScreenings }}</div>
              <div class="stat-label">总筛查次数</div>
              <div class="stat-trend"> <span style="color: #52c41a">↑ 25%</span> 较上月 </div>
            </div>
          </div>
        </ElCard>
      </ElCol>
      <ElCol :xs="24" :sm="12" :md="6">
        <ElCard shadow="hover" class="stat-card">
          <div class="stat-content">
            <div
              class="stat-icon"
              style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)"
            >
              <i class="iconfont-sys">&#xe86e;</i>
            </div>
            <div class="stat-data">
              <div class="stat-value">{{ statistics.adminUsers }}</div>
              <div class="stat-label">管理员数量</div>
              <div class="stat-trend"> <span style="color: #1890ff">Admin</span> 角色 </div>
            </div>
          </div>
        </ElCard>
      </ElCol>
      <ElCol :xs="24" :sm="12" :md="6">
        <ElCard shadow="hover" class="stat-card">
          <div class="stat-content">
            <div
              class="stat-icon"
              style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)"
            >
              <i class="iconfont-sys">&#xe86e;</i>
            </div>
            <div class="stat-data">
              <div class="stat-value">{{ statistics.normalUsers }}</div>
              <div class="stat-label">普通用户数量</div>
              <div class="stat-trend"> <span style="color: #52c41a">User</span> 角色 </div>
            </div>
          </div>
        </ElCard>
      </ElCol>
    </ElRow>

    <!-- 图表区域 -->
    <ElRow :gutter="20">
      <!-- 风险等级分布 -->
      <ElCol :xs="24" :sm="24" :md="12">
        <ElCard shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <i class="iconfont-sys">&#xe7a5;</i>
              <span>风险等级分布</span>
            </div>
          </template>
          <div ref="riskDistChartRef" class="chart-container"></div>
        </ElCard>
      </ElCol>

      <!-- 筛查趋势 -->
      <ElCol :xs="24" :sm="24" :md="12">
        <ElCard shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <i class="iconfont-sys">&#xe7b5;</i>
              <span>筛查趋势（近30天）</span>
            </div>
          </template>
          <div ref="trendChartRef" class="chart-container"></div>
        </ElCard>
      </ElCol>
    </ElRow>

    <!-- 高危因素排行 -->
    <ElRow :gutter="20">
      <ElCol :span="24">
        <ElCard shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <i class="iconfont-sys">&#xe7a3;</i>
              <span>Top10 高危因素排行</span>
            </div>
          </template>
          <div ref="factorsChartRef" class="chart-container" style="height: 400px"></div>
        </ElCard>
      </ElCol>
    </ElRow>
  </div>
</template>

<script setup lang="ts">
  import { ref, reactive, onMounted, onBeforeUnmount } from 'vue'
  import * as echarts from 'echarts'
  import { fetchGetStatisticsOverview, fetchDetail } from '@/api/system-statistic'

  const statistics = reactive({
    totalUsers: 0,
    totalScreenings: 0,
    todayNewUsers: 0,
    adminUsers: 0,
    normalUsers: 0
  })

  // 风险等级分布数据
  const riskLevelDistribution = ref<any[]>([])

  // 高危因素数据
  const topRiskFactors = ref<any[]>([])

  // 筛查趋势数据
  const dailyTrend = ref<any[]>([])

  const riskDistChartRef = ref<HTMLElement>()
  const trendChartRef = ref<HTMLElement>()
  const factorsChartRef = ref<HTMLElement>()

  let riskDistChart: echarts.ECharts | null = null
  let trendChart: echarts.ECharts | null = null
  let factorsChart: echarts.ECharts | null = null

  onMounted(() => {
    fetchStatistics()
    initCharts()
    fetchDetailnumber()
    window.addEventListener('resize', handleResize)
  })

  onBeforeUnmount(() => {
    window.removeEventListener('resize', handleResize)
    riskDistChart?.dispose()
    trendChart?.dispose()
    factorsChart?.dispose()
  })

  const fetchDetailnumber = async () => {
    try {
      const response = (await fetchDetail()) as any
      console.log('📊 统计数据详情:', response)

      // 处理风险等级分布数据
      if (response.risk_level_distribution) {
        riskLevelDistribution.value = response.risk_level_distribution
        updateRiskDistChart()
      }

      // 处理高危因素数据
      if (response.top_risk_factors) {
        topRiskFactors.value = response.top_risk_factors
        updateFactorsChart()
      }

      // 处理筛查趋势数据
      if (response.daily_trend) {
        dailyTrend.value = response.daily_trend
        updateTrendChart()
      }
    } catch (error) {
      console.error('❌ 获取统计数据详情失败:', error)
      ElMessage.error('获取统计数据详情失败')
    }
  }

  const fetchStatistics = async () => {
    try {
      const response = (await fetchGetStatisticsOverview()) as any
      console.log('📊 统计数据:', response)

      statistics.totalUsers = response.total_users || 0
      statistics.todayNewUsers = response.today_new_users || 0

      // 角色分布数据
      if (response.role_distribution) {
        statistics.adminUsers = response.role_distribution.admin || 0
        statistics.normalUsers = response.role_distribution.user || 0
      }
    } catch (error) {
      console.error('❌ 获取统计数据失败:', error)
      ElMessage.error('获取统计数据失败')
    }
  }

  // 更新风险等级分布图表
  const updateRiskDistChart = () => {
    if (!riskDistChart) return

    // 定义风险等级颜色映射
    const colorMap: Record<string, string> = {
      低风险: '#52c41a',
      中低风险: '#95de64',
      中风险: '#faad14',
      中高风险: '#fa8c16',
      高风险: '#ff4d4f',
      极高风险: '#f5222d'
    }

    // 转换数据格式
    const chartData = riskLevelDistribution.value.map((item) => ({
      value: item.count,
      name: item.level,
      itemStyle: { color: colorMap[item.level] || '#999' },
      // 在 tooltip 中显示百分比
      tooltip: {
        formatter: `{b}: {c}人 (${item.percentage}%)`
      }
    }))

    riskDistChart.setOption({
      series: [
        {
          data: chartData
        }
      ]
    })
  }

  // 更新筛查趋势图表
  const updateTrendChart = () => {
    if (!trendChart || !dailyTrend.value.length) return

    // 提取日期和数据
    const dates = dailyTrend.value.map((item) => {
      // 格式化日期为 MM-DD
      const date = new Date(item.date)
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      return `${month}-${day}`
    })

    const counts = dailyTrend.value.map((item) => item.count)
    const avgRiskScores = dailyTrend.value.map((item) => item.avg_risk_score)

    trendChart.setOption({
      tooltip: {
        trigger: 'axis',
        formatter: (params: any) => {
          let result = `${params[0].axisValue}<br/>`
          params.forEach((item: any) => {
            result += `${item.marker} ${item.seriesName}: ${item.value}${item.seriesName === '筛查次数' ? '次' : '分'}<br/>`
          })
          return result
        }
      },
      legend: {
        data: ['筛查次数', '平均风险分数'],
        top: 0
      },
      xAxis: {
        type: 'category',
        data: dates,
        boundaryGap: false
      },
      yAxis: [
        {
          type: 'value',
          name: '筛查次数',
          position: 'left'
        },
        {
          type: 'value',
          name: '平均分数',
          position: 'right',
          max: 1,
          min: 0
        }
      ],
      series: [
        {
          name: '筛查次数',
          data: counts,
          type: 'line',
          smooth: true,
          yAxisIndex: 0,
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(24, 144, 255, 0.3)' },
              { offset: 1, color: 'rgba(24, 144, 255, 0.05)' }
            ])
          },
          itemStyle: {
            color: '#1890ff'
          }
        },
        {
          name: '平均风险分数',
          data: avgRiskScores,
          type: 'line',
          smooth: true,
          yAxisIndex: 1,
          itemStyle: {
            color: '#f5222d'
          }
        }
      ]
    })
  }

  // 更新高危因素图表
  const updateFactorsChart = () => {
    if (!factorsChart) return

    // 中文因素名称映射
    const factorNameMap: Record<string, string> = {
      gender: '性别',
      tissue_abnormality: '组织异常',
      family_history: '家族史',
      性别: '性别',
      comprehensive_risk: '综合风险',
      screening_history_score: '筛查历史评分',
      tumor_marker_score: '肿瘤标志物评分',
      bmi_x_exercise: 'BMI×运动',
      pregnancy_count: '怀孕次数',
      体脂率: '体脂率'
    }

    // 转换数据格式 - 按频次排序（从大到小）
    const sortedFactors = [...topRiskFactors.value].sort((a, b) => b.frequency - a.frequency)

    const factorNames = sortedFactors.map((item) => factorNameMap[item.factor] || item.factor)
    const frequencies = sortedFactors.map((item) => item.frequency)

    // 计算最大值，并设置 X 轴最大值为实际最大值 + 10
    const maxFrequency = Math.max(...frequencies, 0)
    const xAxisMax = maxFrequency + 10

    factorsChart.setOption({
      xAxis: {
        max: xAxisMax
      },
      yAxis: {
        data: factorNames
      },
      series: [
        {
          data: frequencies
        }
      ]
    })
  }

  const initCharts = () => {
    if (riskDistChartRef.value) {
      riskDistChart = echarts.init(riskDistChartRef.value)
      riskDistChart.setOption({
        tooltip: {
          trigger: 'item'
        },
        legend: {
          orient: 'vertical',
          left: 'left'
        },
        series: [
          {
            type: 'pie',
            radius: '60%',
            data: [],
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            },
            label: {
              formatter: '{b}: {c}人'
            }
          }
        ]
      })
    }

    if (trendChartRef.value) {
      trendChart = echarts.init(trendChartRef.value)
      trendChart.setOption({
        tooltip: {
          trigger: 'axis'
        },
        legend: {
          data: ['筛查次数', '平均风险分数'],
          top: 0
        },
        grid: {
          top: 40,
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: [],
          boundaryGap: false
        },
        yAxis: [
          {
            type: 'value',
            name: '筛查次数',
            position: 'left'
          },
          {
            type: 'value',
            name: '平均分数',
            position: 'right',
            max: 1,
            min: 0
          }
        ],
        series: [
          {
            name: '筛查次数',
            data: [],
            type: 'line',
            smooth: true,
            yAxisIndex: 0,
            areaStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                { offset: 0, color: 'rgba(24, 144, 255, 0.3)' },
                { offset: 1, color: 'rgba(24, 144, 255, 0.05)' }
              ])
            },
            itemStyle: {
              color: '#1890ff'
            }
          },
          {
            name: '平均风险分数',
            data: [],
            type: 'line',
            smooth: true,
            yAxisIndex: 1,
            itemStyle: {
              color: '#f5222d'
            }
          }
        ]
      })
    }

    if (factorsChartRef.value) {
      factorsChart = echarts.init(factorsChartRef.value)
      factorsChart.setOption({
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          },
          formatter: (params: any) => {
            const data = params[0]
            return `${data.name}: ${data.value}次`
          }
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '10%',
          containLabel: true
        },
        xAxis: {
          type: 'value',
          name: '出现频次',
          nameLocation: 'end',
          nameGap: -10
        },
        yAxis: {
          type: 'category',
          data: []
        },
        series: [
          {
            type: 'bar',
            data: [],
            itemStyle: {
              color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                { offset: 0, color: '#1890ff' },
                { offset: 1, color: '#13c2c2' }
              ])
            },
            label: {
              show: true,
              position: 'right',
              formatter: '{c}次'
            }
          }
        ]
      })
    }
  }

  const handleResize = () => {
    riskDistChart?.resize()
    trendChart?.resize()
    factorsChart?.resize()
  }
</script>

<style scoped lang="scss">
  .statistics-page {
    padding: 20px;

    .stats-cards {
      margin-bottom: 20px;

      .stat-card {
        height: 100%;

        .stat-content {
          display: flex;
          gap: 20px;
          align-items: center;

          .stat-icon {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 60px;
            height: 60px;
            border-radius: 12px;

            .iconfont-sys {
              font-size: 32px;
              color: #fff;
            }
          }

          .stat-data {
            flex: 1;

            .stat-value {
              margin-bottom: 5px;
              font-size: 28px;
              font-weight: bold;
              color: var(--art-text-gray-800);
            }

            .stat-label {
              margin-bottom: 8px;
              font-size: 13px;
              color: var(--art-text-gray-500);
            }

            .stat-trend {
              font-size: 12px;
              color: var(--art-text-gray-500);
            }
          }
        }
      }
    }

    .chart-card {
      height: 100%;
      margin-bottom: 20px;

      .card-header {
        display: flex;
        gap: 8px;
        align-items: center;
        font-size: 16px;
        font-weight: 600;

        .iconfont-sys {
          font-size: 18px;
          color: var(--el-color-primary);
        }
      }

      .chart-container {
        height: 350px;
      }
    }
  }
</style>
