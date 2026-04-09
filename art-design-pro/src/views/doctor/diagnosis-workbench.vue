<template>
  <div class="diagnosis-workbench-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">
        <i class="el-icon-document-checked"></i>
        医生诊断工作台
      </h1>
      <div class="header-stats">
        <el-tag type="warning" size="large">
          <i class="el-icon-warning"></i>
          待审核: {{ total }}
        </el-tag>
      </div>
    </div>

    <!-- 待审核列表 -->
    <el-card class="review-list-card" shadow="hover" v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>待审核影像列表</span>
          <el-button @click="loadData" :loading="loading">
            <i class="el-icon-refresh"></i>
            刷新
          </el-button>
        </div>
      </template>

      <el-empty v-if="reviewList.length === 0 && !loading" description="暂无待审核影像" />

      <div v-else class="review-list">
        <div v-for="item in reviewList" :key="item.result.id" class="review-item">
          <!-- 影像区域 -->
          <div class="image-section">
            <el-image
              :src="item.image.file_url"
              fit="cover"
              class="thumbnail"
              :preview-src-list="[item.image.file_url, item.result.annotated_image_url].filter(Boolean)"
            >
              <template #error>
                <div class="image-slot">
                  <i class="el-icon-picture-outline"></i>
                </div>
              </template>
            </el-image>
            <div v-if="item.result.annotated_image_url" class="has-annotation-badge">
              <i class="el-icon-view"></i>
              有标注
            </div>
          </div>

          <!-- AI分析结果 -->
          <div class="analysis-section">
            <h3 class="section-title">AI分析结果</h3>
            <el-descriptions :column="2" size="small" border>
              <el-descriptions-item label="预测类别">
                <el-tag :type="getRiskTagType(item.result.risk_level)" size="small">
                  {{ item.result.predicted_class }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="置信度">
                <span style="font-weight: 600; color: var(--el-color-primary)">
                  {{ (item.result.confidence * 100).toFixed(2) }}%
                </span>
              </el-descriptions-item>
              <el-descriptions-item label="风险等级">
                {{ item.result.risk_level }}
              </el-descriptions-item>
              <el-descriptions-item label="分析时间">
                {{ formatDateTime(item.result.analyzed_at) }}
              </el-descriptions-item>
            </el-descriptions>

            <div class="ai-recommendation">
              <strong>AI建议：</strong>
              <p>{{ item.result.ai_recommendation }}</p>
            </div>
          </div>

          <!-- 审核操作 -->
          <div class="review-section">
            <el-button
              type="primary"
              @click="openReviewDialog(item)"
              class="review-btn"
            >
              <i class="el-icon-edit"></i>
              审核并诊断
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
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </el-card>

    <!-- 审核对话框 -->
    <el-dialog
      v-model="reviewDialogVisible"
      title="医生诊断审核"
      width="900px"
      :close-on-click-modal="false"
    >
      <div v-if="currentItem" class="review-dialog-content">
        <!-- 图像对比 -->
        <el-row :gutter="16">
          <el-col :span="12">
            <h4>原始影像</h4>
            <el-image
              :src="currentItem.image.file_url"
              fit="contain"
              class="dialog-image"
              :preview-src-list="[currentItem.image.file_url]"
            />
          </el-col>
          <el-col :span="12" v-if="currentItem.result.annotated_image_url">
            <h4>AI标注图</h4>
            <el-image
              :src="currentItem.result.annotated_image_url"
              fit="contain"
              class="dialog-image"
              :preview-src-list="[currentItem.result.annotated_image_url]"
            />
          </el-col>
        </el-row>

        <!-- AI分析结果 -->
        <el-divider>AI分析结果</el-divider>
        <el-alert
          :title="`AI预测: ${currentItem.result.predicted_class} (置信度: ${(currentItem.result.confidence * 100).toFixed(2)}%)`"
          :type="getRiskTagType(currentItem.result.risk_level)"
          :closable="false"
          show-icon
        >
          {{ currentItem.result.ai_recommendation }}
        </el-alert>

        <!-- 诊断表单 -->
        <el-divider>医生诊断意见</el-divider>
        <el-form :model="reviewForm" ref="reviewFormRef" :rules="reviewRules" label-width="120px">
          <el-form-item label="真实诊断" prop="true_label">
            <el-select v-model="reviewForm.true_label" placeholder="请选择真实诊断结果">
              <el-option label="正常" value="normal" />
              <el-option label="良性肿瘤" value="benign" />
              <el-option label="恶性肿瘤" value="malignant" />
            </el-select>
            <span class="form-tip">
              （选填，用于模型改进。如果AI预测准确，可与AI预测一致）
            </span>
          </el-form-item>

          <el-form-item label="诊断意见" prop="doctor_opinion">
            <el-input
              v-model="reviewForm.doctor_opinion"
              type="textarea"
              :rows="6"
              placeholder="请输入详细的诊断意见和建议..."
            />
          </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <el-button @click="reviewDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitReview" :loading="submitting">
          <i class="el-icon-check"></i>
          提交审核
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { medicalImageAPI } from '@/api/medical-image'

// 状态
const loading = ref(false)
const reviewList = ref<any[]>([])
const total = ref(0)
const pagination = ref({
  page: 1,
  pageSize: 20
})

const reviewDialogVisible = ref(false)
const currentItem = ref<any>(null)
const submitting = ref(false)
const reviewFormRef = ref<FormInstance>()

// 审核表单
const reviewForm = ref({
  true_label: '',
  doctor_opinion: ''
})

// 表单验证
const reviewRules: FormRules = {
  doctor_opinion: [
    { required: true, message: '请输入诊断意见', trigger: 'blur' },
    { min: 10, message: '诊断意见至少10个字符', trigger: 'blur' }
  ]
}

// 加载待审核列表
const loadData = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.value.page - 1) * pagination.value.pageSize,
      limit: pagination.value.pageSize
    }

    const response: any = await medicalImageAPI.getPendingReview(params)
    reviewList.value = response.items
    total.value = response.total
  } catch (error) {
    ElMessage.error('加载待审核列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 打开审核对话框
const openReviewDialog = (item: any) => {
  currentItem.value = item
  reviewForm.value = {
    true_label: item.result.predicted_class === '正常' ? 'normal' : 
                item.result.predicted_class === '良性肿瘤' ? 'benign' : 
                item.result.predicted_class === '恶性肿瘤' ? 'malignant' : '',
    doctor_opinion: ''
  }
  reviewDialogVisible.value = true
}

// 提交审核
const submitReview = async () => {
  if (!reviewFormRef.value || !currentItem.value) return

  await reviewFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        submitting.value = true
        await medicalImageAPI.submitReview(currentItem.value.result.id, {
          doctor_opinion: reviewForm.value.doctor_opinion,
          true_label: reviewForm.value.true_label || undefined
        })

        ElMessage.success('审核提交成功')
        reviewDialogVisible.value = false
        loadData() // 刷新列表
      } catch (error: any) {
        ElMessage.error(error.message || '审核提交失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

// 获取风险标签类型
const getRiskTagType = (riskLevel: string): 'success' | 'warning' | 'danger' | 'info' => {
  if (riskLevel === '低风险') return 'success'
  if (riskLevel === '中风险') return 'warning'
  return 'danger'
}

// 格式化日期时间
const formatDateTime = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  loadData()
})
</script>

<style scoped lang="scss">
.diagnosis-workbench-container {
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
}

.review-list-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 16px;
    font-weight: 600;
  }
}

.review-list {
  .review-item {
    display: flex;
    gap: 20px;
    padding: 20px;
    border: 1px solid var(--el-border-color-light);
    border-radius: 8px;
    margin-bottom: 16px;
    transition: all 0.3s;

    &:hover {
      border-color: var(--el-color-primary);
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    }

    .image-section {
      position: relative;
      width: 200px;
      flex-shrink: 0;

      .thumbnail {
        width: 100%;
        height: 200px;
        border-radius: 8px;
        cursor: pointer;
      }

      .image-slot {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
        height: 100%;
        background: var(--el-fill-color-light);
        font-size: 32px;
        color: var(--el-text-color-secondary);
      }

      .has-annotation-badge {
        position: absolute;
        bottom: 8px;
        left: 8px;
        padding: 4px 8px;
        background: rgba(230, 162, 60, 0.9);
        color: white;
        border-radius: 4px;
        font-size: 12px;
        display: flex;
        align-items: center;
        gap: 4px;
      }
    }

    .analysis-section {
      flex: 1;
      min-width: 0;

      .section-title {
        font-size: 16px;
        font-weight: 600;
        margin: 0 0 12px 0;
      }

      .ai-recommendation {
        margin-top: 12px;
        padding: 12px;
        background: var(--el-fill-color-light);
        border-radius: 6px;
        font-size: 14px;

        strong {
          color: var(--el-text-color-primary);
        }

        p {
          margin: 6px 0 0 0;
          color: var(--el-text-color-regular);
        }
      }
    }

    .review-section {
      display: flex;
      align-items: center;

      .review-btn {
        height: 100%;
        padding: 20px;
      }
    }
  }
}

.pagination {
  margin-top: 24px;
  display: flex;
  justify-content: center;
}

.review-dialog-content {
  h4 {
    margin: 0 0 12px 0;
    font-size: 14px;
    font-weight: 600;
  }

  .dialog-image {
    width: 100%;
    max-height: 300px;
    border-radius: 8px;
    border: 2px solid var(--el-border-color);
  }

  .form-tip {
    margin-left: 12px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }
}
</style>

