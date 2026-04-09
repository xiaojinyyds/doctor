<template>
  <div class="model-performance-badge">
    <ElCard shadow="hover">
      <div class="badge-content">
        <div class="badge-header">
          <i class="iconfont-sys">&#xe7b2;</i>
          <span class="title">模型信息</span>
        </div>

        <div class="metrics-grid">
          <div class="metric-item">
            <div class="metric-label">模型版本</div>
            <div class="metric-value version">{{ modelInfo?.version || 'N/A' }}</div>
          </div>

          <div class="metric-item">
            <div class="metric-label">准确率</div>
            <div class="metric-value accuracy">
              {{ formatPercent(modelInfo?.accuracy) }}
            </div>
            <ElProgress
              :percentage="(modelInfo?.accuracy || 0) * 100"
              :show-text="false"
              :stroke-width="6"
              :color="getAccuracyColor(modelInfo?.accuracy || 0)"
            />
          </div>

          <div class="metric-item">
            <div class="metric-label">AUC值</div>
            <div class="metric-value auc">{{ formatDecimal(modelInfo?.auc) }}</div>
            <ElProgress
              :percentage="(modelInfo?.auc || 0) * 100"
              :show-text="false"
              :stroke-width="6"
              color="#409eff"
            />
          </div>

          <div class="metric-item">
            <div class="metric-label">特征数</div>
            <div class="metric-value">{{ modelInfo?.feature_count || 0 }}</div>
          </div>

          <div class="metric-item">
            <div class="metric-label">推理时间</div>
            <div class="metric-value time">{{ modelInfo?.inference_time_ms || 0 }} ms</div>
          </div>
        </div>

        <div class="badge-footer">
          <ElTag type="success" size="small" effect="dark">
            <i class="el-icon-success"></i>
            XGBoost增强模型
          </ElTag>
          <ElTag type="info" size="small" effect="plain">32个特征</ElTag>
          <ElTag type="warning" size="small" effect="plain">SHAP可解释</ElTag>
        </div>
      </div>
    </ElCard>
  </div>
</template>

<script setup lang="ts">
interface ModelInfo {
  version: string
  feature_count: number
  inference_time_ms: number
  accuracy: number
  auc: number
}

interface Props {
  modelInfo?: ModelInfo
}

defineProps<Props>()

const formatPercent = (value?: number) => {
  if (typeof value !== 'number') return 'N/A'
  return `${(value * 100).toFixed(2)}%`
}

const formatDecimal = (value?: number) => {
  if (typeof value !== 'number') return 'N/A'
  return value.toFixed(4)
}

const getAccuracyColor = (accuracy: number) => {
  if (accuracy >= 0.9) return '#67c23a'
  if (accuracy >= 0.8) return '#409eff'
  if (accuracy >= 0.7) return '#e6a23c'
  return '#f56c6c'
}
</script>

<style scoped lang="scss">
.model-performance-badge {
  margin-bottom: 20px;

  .badge-content {
    .badge-header {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 20px;
      padding-bottom: 12px;
      border-bottom: 2px solid var(--el-border-color-lighter);

      .iconfont-sys {
        font-size: 24px;
        color: var(--el-color-primary);
      }

      .title {
        font-size: 16px;
        font-weight: 600;
        color: var(--art-text-gray-900);
      }
    }

    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 20px;
      margin-bottom: 16px;

      .metric-item {
        .metric-label {
          font-size: 12px;
          color: var(--art-text-gray-500);
          margin-bottom: 6px;
        }

        .metric-value {
          font-size: 20px;
          font-weight: 600;
          color: var(--art-text-gray-900);
          margin-bottom: 6px;

          &.version {
            font-size: 16px;
            color: var(--el-color-primary);
          }

          &.accuracy {
            color: #67c23a;
          }

          &.auc {
            color: #409eff;
          }

          &.time {
            font-size: 16px;
            color: var(--el-color-warning);
          }
        }
      }
    }

    .badge-footer {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      padding-top: 12px;
      border-top: 1px solid var(--el-border-color-lighter);
    }
  }
}
</style>

