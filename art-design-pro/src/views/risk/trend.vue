<template>
  <div class="risk-trend-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <ElButton @click="goBack" text>
          <i class="iconfont-sys">&#xe625;</i>
          返回
        </ElButton>
        <h1 class="page-title">
          <i class="iconfont-sys">&#xe7a3;</i>
          风险趋势追踪
        </h1>
      </div>
      <div class="header-actions">
        <ElRadioGroup v-model="timeRange" size="small" @change="handleTimeRangeChange">
          <ElRadioButton :label="6">近6个月</ElRadioButton>
          <ElRadioButton :label="12">近1年</ElRadioButton>
          <ElRadioButton :label="24">近2年</ElRadioButton>
        </ElRadioGroup>
        <ElButton type="primary" size="small" @click="refreshData">
          <el-icon><Refresh /></el-icon>
          刷新
        </ElButton>
      </div>
    </div>

    <div class="trend-command">
      <div class="command-card">
        <span class="command-label">随访定位</span>
        <strong>长期健康管理驾驶舱</strong>
        <p>连续记录多次评估结果，观察风险变化与干预成效。</p>
      </div>
      <div class="command-card">
        <span class="command-label">观察周期</span>
        <strong>近 {{ timeRange }} 个月</strong>
        <p>支持按月度尺度观察波动、识别异常抬升和改善拐点。</p>
      </div>
      <div class="command-card">
        <span class="command-label">趋势结论</span>
        <strong>{{ trendHeadline }}</strong>
        <p>{{ trendSubline }}</p>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <ElSkeleton :rows="5" animated />
    </div>

    <!-- 空状态 -->
    <div v-else-if="!hasData" class="empty-container">
      <ElEmpty description="暂无评估数据">
        <template #image>
          <i class="iconfont-sys" style="font-size: 64px; color: #dcdfe6;">&#xe7a3;</i>
        </template>
        <ElButton type="primary" @click="goToQuestionnaire">立即评估</ElButton>
      </ElEmpty>
    </div>

    <!-- 数据展示 -->
    <template v-else>
      <!-- 统计概览卡片 -->
      <ElRow :gutter="20" class="stats-row">
        <ElCol :span="6" :xs="24" :sm="12" :md="6">
          <ElCard shadow="hover" class="stat-card">
            <div class="stat-item">
              <div class="stat-label">当前风险评分</div>
              <div class="stat-value" :style="{ color: getRiskColor(trendData?.latest_score) }">
                {{ (trendData?.latest_score * 100).toFixed(1) }}
                <span class="unit">分</span>
              </div>
              <ElTag :type="getRiskTagType(trendData?.latest_level)" size="small">
                {{ trendData?.latest_level }}
              </ElTag>
            </div>
          </ElCard>
        </ElCol>

        <ElCol :span="6" :xs="24" :sm="12" :md="6">
          <ElCard shadow="hover" class="stat-card">
            <div class="stat-item">
              <div class="stat-label">评估次数</div>
              <div class="stat-value primary">
                {{ trendData?.total_records }}
                <span class="unit">次</span>
              </div>
              <div class="stat-desc">{{ trendData?.time_range?.start }} 至今</div>
            </div>
          </ElCard>
        </ElCol>

        <ElCol :span="6" :xs="24" :sm="12" :md="6">
          <ElCard shadow="hover" class="stat-card">
            <div class="stat-item">
              <div class="stat-label">风险变化</div>
              <div class="stat-value" :class="getChangeClass(trendData?.total_change)">
                {{ trendData?.total_change > 0 ? '+' : '' }}{{ trendData?.change_percentage }}%
              </div>
              <div class="stat-desc">
                较{{ trendData?.time_range?.start }} {{ trendData?.trend_direction }}
              </div>
            </div>
          </ElCard>
        </ElCol>

        <ElCol :span="6" :xs="24" :sm="12" :md="6">
          <ElCard shadow="hover" class="stat-card">
            <div class="stat-item">
              <div class="stat-label">改善指标</div>
              <div class="stat-value success">
                {{ improvementCount }}
                <span class="unit">项</span>
              </div>
              <div class="stat-desc">风险下降的分类</div>
            </div>
          </ElCard>
        </ElCol>
      </ElRow>

      <div class="summary-ribbon">
        <div class="summary-item">
          <span class="summary-label">最高风险阶段</span>
          <strong>{{ highestRiskPoint.label }}</strong>
        </div>
        <div class="summary-item">
          <span class="summary-label">最佳改善幅度</span>
          <strong>{{ bestImprovement }}</strong>
        </div>
        <div class="summary-item">
          <span class="summary-label">随访建议</span>
          <strong>{{ followupSuggestion }}</strong>
        </div>
      </div>

      <!-- AI 洞察卡片 -->
      <ElCard shadow="hover" class="insight-card">
        <template #header>
          <div class="card-header">
            <div class="header-left">
              <el-icon><DataLine /></el-icon>
              <span>AI 趋势分析</span>
            </div>
          </div>
        </template>
        <div class="insight-content">
          <el-icon :size="24" color="#1890ff"><DataLine /></el-icon>
          <p class="insight-text">{{ trendData?.insights }}</p>
        </div>
      </ElCard>

      <!-- 趋势图表 -->
      <ElCard shadow="hover" class="chart-card">
        <template #header>
          <div class="card-header">
            <div class="header-left">
              <i class="iconfont-sys">&#xe7a1;</i>
              <span>风险趋势图</span>
            </div>
            <div class="header-right">
              <ElCheckbox v-model="showCategoryLines" size="small">显示分类风险</ElCheckbox>
            </div>
          </div>
        </template>
        <RiskTrendChart
          :data="trendData?.trend_data || []"
          :show-category-lines="showCategoryLines"
          :mark-events="markEvents"
          height="450px"
        />
      </ElCard>

      <!-- 详细数据表格 -->
      <ElCard shadow="hover" class="table-card">
        <template #header>
          <div class="card-header">
            <div class="header-left">
              <i class="iconfont-sys">&#xe7b9;</i>
              <span>评估历史详情</span>
            </div>
          </div>
        </template>
        <ElTable :data="trendData?.trend_data?.slice().reverse()" stripe>
          <ElTableColumn prop="date" label="日期" width="120" />
          <ElTableColumn label="综合风险" width="150">
            <template #default="{ row }">
              <div class="risk-cell">
                <span class="score">{{ (row.overall_score * 100).toFixed(1) }}分</span>
                <ElTag :type="getRiskTagType(row.overall_level)" size="small">
                  {{ row.overall_level }}
                </ElTag>
              </div>
            </template>
          </ElTableColumn>
          <ElTableColumn label="分类风险评分" min-width="400">
            <template #default="{ row }">
              <div class="category-scores">
                <span
                  v-for="(score, key) in row.category_scores"
                  :key="key"
                  class="category-tag"
                  :style="{ backgroundColor: getCategoryColor(key) + '20', color: getCategoryColor(key) }"
                >
                  {{ categoryNames[key] }}: {{ (score * 100).toFixed(0) }}
                </span>
              </div>
            </template>
          </ElTableColumn>
          <ElTableColumn label="操作" width="120" fixed="right">
            <template #default="{ row }">
              <ElButton type="primary" link size="small" @click="viewDetail(row.assessment_id)">
                查看报告
              </ElButton>
            </template>
          </ElTableColumn>
        </ElTable>
      </ElCard>
    </template>
  </div>
</template>

<script setup lang="ts">
  import { ref, onMounted, computed } from 'vue'
  import { useRouter } from 'vue-router'
  import { ElMessage } from 'element-plus'
  import { Refresh, DataLine } from '@element-plus/icons-vue'
  import { fetchRiskTrend } from '@/api/assessment'
  import RiskTrendChart from '@/components/custom/risk-trend-chart.vue'

  defineOptions({ name: 'RiskTrendPage' })

  const router = useRouter()
  const loading = ref(false)
  const hasData = ref(false)
  const trendData = ref<any>(null)
  const timeRange = ref(12)
  const showCategoryLines = ref(true)

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

  // 计算改善指标数量
  const improvementCount = computed(() => {
    if (!trendData.value?.improvements) return 0
    return trendData.value.improvements.filter((imp: { direction: string }) => imp.direction === '改善').length
  })

  const trendHeadline = computed(() => {
    if (!trendData.value?.trend_direction) return '等待趋势生成'
    if (trendData.value.trend_direction.includes('下降') || trendData.value.total_change < 0) {
      return '整体呈改善趋势'
    }
    if (trendData.value.trend_direction.includes('上升') || trendData.value.total_change > 0) {
      return '风险有抬升迹象'
    }
    return '趋势总体平稳'
  })

  const trendSubline = computed(() => {
    if (!trendData.value?.total_records) return '完成评估后可自动生成连续趋势洞察。'
    return `已累计 ${trendData.value.total_records} 次评估记录，可用于展示干预前后变化。`
  })

  const highestRiskPoint = computed(() => {
    const series = trendData.value?.trend_data || []
    if (!series.length) {
      return { label: '暂无数据', score: 0 }
    }
    const top = [...series].sort((a, b) => b.overall_score - a.overall_score)[0]
    return {
      label: `${top.date} / ${(top.overall_score * 100).toFixed(1)} 分`,
      score: top.overall_score
    }
  })

  const bestImprovement = computed(() => {
    const series = trendData.value?.trend_data || []
    if (series.length < 2) return '暂无可比较数据'
    let bestDrop = 0
    for (let i = 1; i < series.length; i += 1) {
      const delta = series[i - 1].overall_score - series[i].overall_score
      if (delta > bestDrop) bestDrop = delta
    }
    return bestDrop > 0 ? `下降 ${(bestDrop * 100).toFixed(1)} 分` : '暂无明显下降'
  })

  const followupSuggestion = computed(() => {
    const latest = trendData.value?.latest_level
    if (latest === '高风险') return '建议缩短复查周期'
    if (latest === '中风险') return '建议保持季度跟踪'
    if (latest === '低风险') return '建议维持年度复查'
    return '建议持续记录趋势'
  })

  // 标记事件（示例数据，实际可从后端获取或用户自定义）
  const markEvents = computed(() => {
    // 可以根据风险变化趋势自动标记转折点
    return []
  })

  const loadTrendData = async () => {
    loading.value = true
    try {
      const response: any = await fetchRiskTrend(timeRange.value)
      if (response.code === 200) {
        hasData.value = response.data?.has_data
        trendData.value = response.data
      } else {
        ElMessage.error(response.message || '获取趋势数据失败')
      }
    } catch (error) {
      console.error('获取风险趋势失败:', error)
      ElMessage.error('获取风险趋势失败')
    } finally {
      loading.value = false
    }
  }

  const handleTimeRangeChange = () => {
    loadTrendData()
  }

  const refreshData = () => {
    loadTrendData()
    ElMessage.success('数据已刷新')
  }

  const goBack = () => {
    router.back()
  }

  const goToQuestionnaire = () => {
    router.push('/questionnaire')
  }

  const viewDetail = (assessmentId: string) => {
    router.push(`/report/${assessmentId}`)
  }

  const getRiskColor = (score: number) => {
    if (!score) return '#999'
    if (score < 0.3) return '#52c41a'
    if (score < 0.6) return '#faad14'
    return '#f5222d'
  }

  type TagType = 'success' | 'warning' | 'danger' | 'info'
  const getRiskTagType = (level: string): TagType => {
    switch (level) {
      case '低风险':
        return 'success'
      case '中风险':
        return 'warning'
      case '高风险':
        return 'danger'
      default:
        return 'info'
    }
  }

  const getChangeClass = (change: number) => {
    if (!change) return ''
    if (change < 0) return 'success'
    if (change > 0) return 'danger'
    return 'neutral'
  }

  const getCategoryColor = (key: string) => {
    return categoryColors[key] || '#999'
  }

  onMounted(() => {
    loadTrendData()
  })
</script>

<style scoped lang="scss">
  .risk-trend-page {
    padding: 24px;
    min-height: 100vh;
    background:
      radial-gradient(circle at top left, rgba(54, 168, 255, 0.1), transparent 24%),
      radial-gradient(circle at top right, rgba(255, 194, 99, 0.12), transparent 20%),
      linear-gradient(180deg, #f4f8fb 0%, #edf3f8 100%);

    .page-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
      flex-wrap: wrap;
      gap: 16px;
      padding: 28px 30px;
      background:
        linear-gradient(145deg, rgba(255, 255, 255, 0.94), rgba(255, 255, 255, 0.76)),
        linear-gradient(120deg, #dcefff, #fff4e4);
      border: 1px solid rgba(255, 255, 255, 0.8);
      border-radius: 26px;
      box-shadow: 0 22px 52px rgba(21, 45, 72, 0.08);

      .header-left {
        display: flex;
        align-items: center;
        gap: 16px;

        .page-title {
          margin: 0;
          font-size: 24px;
          font-weight: bold;
          color: var(--art-text-gray-800);
          display: flex;
          align-items: center;
          gap: 8px;

          .iconfont-sys {
            font-size: 28px;
            color: var(--el-color-primary);
          }
        }
      }

      .header-actions {
        display: flex;
        gap: 12px;
        align-items: center;
      }
    }

    .trend-command {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }

    .command-card {
      padding: 18px 20px;
      background:
        linear-gradient(145deg, rgba(255, 255, 255, 0.92), rgba(255, 255, 255, 0.78)),
        linear-gradient(135deg, #e0f2ff, #fff4df);
      border: 1px solid rgba(255, 255, 255, 0.82);
      border-radius: 20px;
      box-shadow: 0 14px 34px rgba(18, 42, 68, 0.06);

      .command-label {
        display: block;
        margin-bottom: 8px;
        font-size: 12px;
        letter-spacing: 0.08em;
        color: #70819a;
        text-transform: uppercase;
      }

      strong {
        display: block;
        margin-bottom: 8px;
        font-size: 22px;
        color: #15253f;
      }

      p {
        margin: 0;
        font-size: 13px;
        line-height: 1.6;
        color: #5e6f86;
      }
    }

    .loading-container {
      padding: 40px;
      background: #fff;
      border-radius: 8px;
    }

    .empty-container {
      padding: 60px 0;
      background: #fff;
      border-radius: 8px;
    }

    .stats-row {
      margin-bottom: 24px;

      .stat-card {
        .stat-item {
          text-align: center;
          padding: 10px 0;

          .stat-label {
            font-size: 14px;
            color: var(--art-text-gray-500);
            margin-bottom: 8px;
          }

          .stat-value {
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 8px;

            &.primary {
              color: var(--el-color-primary);
            }

            &.success {
              color: #52c41a;
            }

            &.danger {
              color: #f5222d;
            }

            &.neutral {
              color: #999;
            }

            .unit {
              font-size: 14px;
              font-weight: normal;
              margin-left: 4px;
            }
          }

          .stat-desc {
            font-size: 12px;
            color: var(--art-text-gray-500);
          }
        }
      }
    }

    .summary-ribbon {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }

    .summary-item {
      padding: 16px 18px;
      background: rgba(255, 255, 255, 0.82);
      border: 1px solid rgba(199, 214, 228, 0.65);
      border-radius: 18px;
      box-shadow: 0 10px 28px rgba(26, 48, 72, 0.04);

      .summary-label {
        display: block;
        margin-bottom: 8px;
        font-size: 12px;
        color: #6c7c92;
      }

      strong {
        font-size: 20px;
        color: #16253f;
      }
    }

    .insight-card {
      margin-bottom: 24px;
      border-radius: 22px;
      overflow: hidden;
      border: 1px solid rgba(214, 225, 235, 0.95);
      box-shadow: 0 18px 42px rgba(26, 48, 72, 0.06);

      :deep(.el-card__header) {
        padding: 20px 24px;
        background: linear-gradient(180deg, #fff, #f8fbfd);
        border-bottom: 1px solid rgba(222, 231, 239, 0.9);
      }

      .insight-content {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        padding: 16px;
        background: linear-gradient(135deg, #e6f7ff 0%, #f0f5ff 100%);
        border-radius: 8px;
        border-left: 4px solid #1890ff;

        .insight-text {
          margin: 0;
          font-size: 15px;
          line-height: 1.6;
          color: var(--art-text-gray-700);
        }
      }
    }

    .chart-card {
      margin-bottom: 24px;
      border-radius: 24px;
      overflow: hidden;
      border: 1px solid rgba(214, 225, 235, 0.95);
      box-shadow: 0 20px 44px rgba(26, 48, 72, 0.06);

      :deep(.el-card__header) {
        padding: 20px 24px;
        background: linear-gradient(180deg, #fff, #f8fbfd);
        border-bottom: 1px solid rgba(222, 231, 239, 0.9);
      }

      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;

        .header-left {
          display: flex;
          align-items: center;
          gap: 8px;
        }
      }
    }

    .table-card {
      border-radius: 24px;
      overflow: hidden;
      border: 1px solid rgba(214, 225, 235, 0.95);
      box-shadow: 0 20px 44px rgba(26, 48, 72, 0.06);

      :deep(.el-card__header) {
        padding: 20px 24px;
        background: linear-gradient(180deg, #fff, #f8fbfd);
        border-bottom: 1px solid rgba(222, 231, 239, 0.9);
      }

      .risk-cell {
        display: flex;
        align-items: center;
        gap: 8px;

        .score {
          font-weight: 600;
        }
      }

      .category-scores {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;

        .category-tag {
          padding: 2px 8px;
          border-radius: 4px;
          font-size: 11px;
          font-weight: 500;
        }
      }
    }

    .card-header {
      display: flex;
      align-items: center;
      gap: 8px;

      .header-left {
        display: flex;
        align-items: center;
        gap: 8px;
        font-weight: 600;
      }
    }
  }

  @media (max-width: 768px) {
    .risk-trend-page {
      padding: 12px;

      .page-header {
        flex-direction: column;
        align-items: flex-start;

        .header-actions {
          width: 100%;
          flex-wrap: wrap;
        }
      }

      .trend-command,
      .summary-ribbon {
        grid-template-columns: 1fr;
      }
    }
  }
</style>
