<template>
  <div class="medical-image-history-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">
        <i class="iconfont-sys">&#xe63c;</i>
        影像分析历史
      </h1>
      <div class="header-actions">
        <el-button type="primary" @click="refreshData">
          <i class="el-icon-refresh"></i>
          刷新
        </el-button>
        <el-button @click="$router.push('/medical-image/upload')">
          <i class="el-icon-upload"></i>
          上传新影像
        </el-button>
      </div>
    </div>

    <!-- 筛选栏 -->
    <el-card class="filter-card" shadow="never">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="影像类型">
          <el-select v-model="filterForm.imageType" placeholder="全部" clearable>
            <el-option label="乳腺超声" value="breast_ultrasound" />
            <el-option label="CT" value="ct" />
            <el-option label="MRI" value="mri" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadHistory">
            <i class="el-icon-search"></i>
            查询
          </el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 历史记录列表 -->
    <el-card class="history-list-card" shadow="hover" v-loading="loading">
      <el-empty v-if="historyList.length === 0 && !loading" description="暂无历史记录" />

      <div v-else class="history-list">
        <div
          v-for="item in historyList"
          :key="item.image.id"
          class="history-item"
          @click="viewDetail(item)"
        >
          <!-- 缩略图 -->
          <div class="thumbnail">
            <el-image :src="item.image.file_url" fit="cover" lazy>
              <template #error>
                <div class="image-slot">
                  <i class="el-icon-picture-outline"></i>
                </div>
              </template>
            </el-image>
            <div v-if="item.image.analysis_status === 'pending'" class="status-badge pending">
              待分析
            </div>
            <div
              v-else-if="item.image.analysis_status === 'completed'"
              class="status-badge completed"
            >
              已完成
            </div>
          </div>

          <!-- 信息区 -->
          <div class="item-content">
            <div class="item-header">
              <h3 class="item-title">{{ item.image.filename }}</h3>
              <el-tag
                v-if="item.latest_analysis"
                :type="getRiskTagType(item.latest_analysis.risk_level)"
                effect="dark"
                size="small"
              >
                {{ item.latest_analysis.risk_level }}
              </el-tag>
            </div>

            <div v-if="item.latest_analysis" class="item-info">
              <div class="info-row">
                <span class="label">预测结果：</span>
                <span class="value">{{ item.latest_analysis.predicted_class }}</span>
              </div>
              <div class="info-row">
                <span class="label">置信度：</span>
                <span class="value confidence">
                  {{ (item.latest_analysis.confidence * 100).toFixed(2) }}%
                </span>
              </div>
              <div class="info-row">
                <span class="label">分析时间：</span>
                <span class="value">{{ formatDateTime(item.latest_analysis.analyzed_at) }}</span>
              </div>
            </div>
            <div v-else class="item-info">
              <el-text type="info">尚未分析</el-text>
            </div>

            <div class="item-meta">
              <span>
                <i class="el-icon-calendar"></i>
                {{ formatDateTime(item.image.upload_time) }}
              </span>
              <span>
                <i class="el-icon-picture"></i>
                {{ item.image.image_type }}
              </span>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="item-actions">
            <el-button type="primary" link @click.stop="viewDetail(item)">
              <i class="el-icon-view"></i>
              查看详情
            </el-button>
            <el-button type="danger" link @click.stop="deleteItem(item)">
              <i class="el-icon-delete"></i>
              删除
            </el-button>
          </div>
        </div>
      </div>

      <!-- 分页 -->
      <div v-if="total > 0" class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadHistory"
          @current-change="loadHistory"
        />
      </div>
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="影像分析详情"
      width="1000px"
      :close-on-click-modal="false"
    >
      <div v-if="detailData" class="detail-content" v-loading="detailLoading">
        <!-- 图像对比 -->
        <div class="image-comparison">
          <div class="image-box">
            <h4 class="image-title">
              <i class="el-icon-picture-outline"></i>
              原始影像
            </h4>
            <el-image
              :src="detailData.image.file_url"
              fit="contain"
              class="detail-image"
              :preview-src-list="[detailData.image.file_url]"
            />
          </div>
          <div v-if="detailData.result.annotated_image_url" class="image-box">
            <h4 class="image-title">
              <i class="el-icon-view"></i>
              AI关注区域热力图
            </h4>
            <el-image
              :src="detailData.result.annotated_image_url"
              fit="contain"
              class="detail-image annotated"
              :preview-src-list="[detailData.result.annotated_image_url]"
            />
            <el-tag type="warning" size="small" class="image-badge">
              <i class="el-icon-warning"></i>
              颜色越暖表示模型关注度越高
            </el-tag>
          </div>
        </div>

        <!-- 分析结果详情 -->
        <el-divider content-position="left">
          <i class="el-icon-data-analysis"></i>
          分析结果
        </el-divider>

        <el-row :gutter="24">
          <el-col :span="12">
            <el-card shadow="never" class="info-card">
              <template #header>
                <span>基础信息</span>
              </template>
              <el-descriptions :column="1" border size="small">
                <el-descriptions-item label="预测类别">
                  <el-tag :type="getRiskTagType(detailData.result.risk_level)" size="large">
                    {{ detailData.result.predicted_class }}
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="置信度">
                  <span style="font-size: 18px; font-weight: 600; color: var(--el-color-primary)">
                    {{ (detailData.result.confidence * 100).toFixed(2) }}%
                  </span>
                </el-descriptions-item>
                <el-descriptions-item label="风险等级">
                  {{ detailData.result.risk_level }}
                </el-descriptions-item>
                <el-descriptions-item label="推理时间">
                  {{ detailData.result.model_info.inference_time_ms }} ms
                </el-descriptions-item>
                <el-descriptions-item label="模型版本">
                  {{ detailData.result.model_info.name }} {{ detailData.result.model_info.version }}
                </el-descriptions-item>
                <el-descriptions-item label="分析时间">
                  {{ formatDateTime(detailData.result.analyzed_at) }}
                </el-descriptions-item>
              </el-descriptions>
            </el-card>
          </el-col>

          <el-col :span="12">
            <el-card shadow="never" class="info-card">
              <template #header>
                <span>概率分布</span>
              </template>
              <div class="probability-list">
                <div
                  v-for="(prob, className) in detailData.result.probabilities"
                  :key="className"
                  class="prob-item"
                >
                  <div class="prob-header">
                    <span>{{ className }}</span>
                    <span class="prob-value">{{ (prob * 100).toFixed(2) }}%</span>
                  </div>
                  <el-progress
                    :percentage="Number((prob * 100).toFixed(2))"
                    :color="getProgressColor(String(className))"
                    :stroke-width="12"
                  />
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- AI建议 -->
        <el-alert
          :title="detailData.result.risk_level"
          :type="getRiskAlertType(detailData.result.risk_level)"
          :closable="false"
          show-icon
          class="recommendation-alert"
        >
          <p>{{ detailData.result.recommendation }}</p>
        </el-alert>

        <!-- 影像文件信息 -->
        <el-divider content-position="left">
          <i class="el-icon-document"></i>
          文件信息
        </el-divider>
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="文件名">
            {{ detailData.image.filename }}
          </el-descriptions-item>
          <el-descriptions-item label="影像类型">
            {{ detailData.image.image_type }}
          </el-descriptions-item>
          <el-descriptions-item label="图像尺寸">
            {{ detailData.image.size }}
          </el-descriptions-item>
          <el-descriptions-item label="上传时间">
            {{ formatDateTime(detailData.image.uploaded_at) }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
        <el-button type="primary" @click="downloadAnnotatedImage" v-if="detailData?.result.annotated_image_url">
          <i class="el-icon-download"></i>
          下载热力图
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { medicalImageAPI } from '@/api/medical-image'

// 状态
const loading = ref(false)
const historyList = ref<any[]>([])
const total = ref(0)
const pagination = ref({
  page: 1,
  pageSize: 20
})

const filterForm = ref({
  imageType: ''
})

const detailDialogVisible = ref(false)
const selectedItem = ref<any>(null)
const detailData = ref<any>(null)
const detailLoading = ref(false)

// 加载历史记录
const loadHistory = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.value.page - 1) * pagination.value.pageSize,
      limit: pagination.value.pageSize,
      image_type: filterForm.value.imageType || undefined
    }

    // HTTP工具已自动提取data字段
    const response: any = await medicalImageAPI.getHistory(params)
    historyList.value = response.items
    total.value = response.total
  } catch (error) {
    ElMessage.error('加载历史记录失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 重置筛选
const resetFilter = () => {
  filterForm.value.imageType = ''
  pagination.value.page = 1
  loadHistory()
}

// 刷新数据
const refreshData = () => {
  loadHistory()
  ElMessage.success('数据已刷新')
}

// 查看详情
const viewDetail = async (item: any) => {
  if (!item.latest_analysis) {
    ElMessage.warning('该影像尚未分析')
    return
  }

  selectedItem.value = item
  detailDialogVisible.value = true
  detailLoading.value = true
  detailData.value = null

  try {
    // 调用API获取完整的分析结果详情
    const response: any = await medicalImageAPI.getResultDetail(item.latest_analysis.id)
    detailData.value = response
  } catch (error) {
    ElMessage.error('获取详情失败')
    console.error(error)
  } finally {
    detailLoading.value = false
  }
}

// 下载标注图
const downloadAnnotatedImage = () => {
  if (detailData.value?.result.annotated_image_url) {
    window.open(detailData.value.result.annotated_image_url, '_blank')
  }
}

// 删除记录
const deleteItem = async (item: any) => {
  try {
    await ElMessageBox.confirm('确定要删除这条记录吗？删除后无法恢复。', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await medicalImageAPI.deleteImage(item.image.id)
    ElMessage.success('删除成功')
    loadHistory()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
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

// 获取进度条颜色
const getProgressColor = (className: string): string => {
  if (className === '正常') return '#67C23A'
  if (className === '良性肿瘤') return '#E6A23C'
  return '#F56C6C'
}

// 获取风险提示类型
const getRiskAlertType = (riskLevel: string) => {
  if (riskLevel === '低风险') return 'success'
  if (riskLevel === '中风险') return 'warning'
  return 'error'
}

// 页面挂载时加载数据
onMounted(() => {
  loadHistory()
})
</script>

<style scoped lang="scss">
.medical-image-history-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;

  .page-title {
    font-size: 24px;
    font-weight: 600;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .header-actions {
    display: flex;
    gap: 12px;
  }
}

.filter-card {
  margin-bottom: 20px;
}

.history-list {
  .history-item {
    display: flex;
    gap: 20px;
    padding: 20px;
    border: 1px solid var(--el-border-color-light);
    border-radius: 8px;
    margin-bottom: 16px;
    cursor: pointer;
    transition: all 0.3s;

    &:hover {
      border-color: var(--el-color-primary);
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    }

    .thumbnail {
      position: relative;
      width: 120px;
      height: 120px;
      flex-shrink: 0;
      border-radius: 8px;
      overflow: hidden;

      :deep(.el-image) {
        width: 100%;
        height: 100%;
      }

      .image-slot {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 100%;
        background: var(--el-fill-color-light);
        color: var(--el-text-color-secondary);
        font-size: 32px;
      }

      .status-badge {
        position: absolute;
        top: 8px;
        right: 8px;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 500;

        &.pending {
          background: rgba(230, 162, 60, 0.9);
          color: white;
        }

        &.completed {
          background: rgba(103, 194, 58, 0.9);
          color: white;
        }
      }
    }

    .item-content {
      flex: 1;
      min-width: 0;

      .item-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;

        .item-title {
          font-size: 16px;
          font-weight: 600;
          margin: 0;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
      }

      .item-info {
        margin-bottom: 12px;

        .info-row {
          margin-bottom: 6px;
          font-size: 14px;

          .label {
            color: var(--el-text-color-secondary);
          }

          .value {
            color: var(--el-text-color-primary);
            margin-left: 8px;

            &.confidence {
              font-weight: 600;
              color: var(--el-color-primary);
            }
          }
        }
      }

      .item-meta {
        display: flex;
        gap: 16px;
        font-size: 13px;
        color: var(--el-text-color-secondary);

        span {
          display: flex;
          align-items: center;
          gap: 4px;
        }
      }
    }

    .item-actions {
      display: flex;
      flex-direction: column;
      gap: 8px;
      justify-content: center;
    }
  }
}

.pagination {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}

.detail-content {
  .image-comparison {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin-bottom: 24px;

    .image-box {
      text-align: center;

      .image-title {
        margin: 0 0 12px 0;
        font-size: 16px;
        font-weight: 600;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        color: var(--el-text-color-primary);
      }

      .detail-image {
        width: 100%;
        max-height: 350px;
        border-radius: 8px;
        border: 2px solid var(--el-border-color);

        &.annotated {
          border-color: var(--el-color-warning-light-5);
        }
      }

      .image-badge {
        margin-top: 8px;
      }
    }
  }

  .info-card {
    height: 100%;

    :deep(.el-card__header) {
      padding: 12px 16px;
      font-weight: 600;
    }
  }

  .probability-list {
    .prob-item {
      margin-bottom: 16px;

      &:last-child {
        margin-bottom: 0;
      }

      .prob-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 8px;
        font-size: 14px;

        .prob-value {
          font-weight: 600;
          color: var(--el-color-primary);
        }
      }
    }
  }

  .recommendation-alert {
    margin: 20px 0;

    p {
      margin: 0;
      line-height: 1.6;
    }
  }
}
</style>

