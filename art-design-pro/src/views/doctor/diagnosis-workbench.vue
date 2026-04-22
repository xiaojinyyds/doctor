<template>
  <div class="diagnosis-workbench-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <div>
        <h1 class="page-title">
          <i class="el-icon-document-checked"></i>
          医生诊断工作台
        </h1>
        <p class="page-desc">集中处理待审核影像、查看AI解释结果，并完成医生复核闭环。</p>
      </div>
      <div class="header-stats">
        <el-tag type="warning" size="large">
          <i class="el-icon-warning"></i>
          待审核: {{ total }}
        </el-tag>
      </div>
    </div>

    <div class="command-grid">
      <div class="command-card">
        <span class="command-label">高风险病例</span>
        <strong>{{ highRiskCount }}</strong>
        <p>建议优先复核 AI 判定为高风险的影像结果</p>
      </div>
      <div class="command-card">
        <span class="command-label">热力图覆盖</span>
        <strong>{{ heatmapCoverage }}%</strong>
        <p>当前待审病例中已生成可视化解释的样本占比</p>
      </div>
      <div class="command-card">
        <span class="command-label">工作建议</span>
        <strong>{{ queueHint }}</strong>
        <p>根据队列状态动态给出本轮审核优先级提示</p>
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
            <div class="analysis-head">
              <h3 class="section-title">AI分析结果</h3>
              <div class="head-tags">
                <el-tag :type="getRiskTagType(item.result.risk_level)" effect="light">
                  {{ item.result.risk_level }}
                </el-tag>
                <el-tag type="info" effect="plain">
                  {{ (item.result.confidence * 100).toFixed(1) }}% 置信度
                </el-tag>
              </div>
            </div>
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

            <div class="review-flags">
              <div class="flag-item">
                <span class="flag-label">影像文件</span>
                <strong>{{ item.image.filename }}</strong>
              </div>
              <div class="flag-item">
                <span class="flag-label">解释图谱</span>
                <strong>{{ item.result.annotated_image_url ? '已生成热力图' : '暂无热力图' }}</strong>
              </div>
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
            <h4>AI关注区域热力图</h4>
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
import { ref, onMounted, computed } from 'vue'
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

const highRiskCount = computed(() =>
  reviewList.value.filter((item) => item.result.risk_level === '高风险').length
)

const heatmapCoverage = computed(() => {
  if (!reviewList.value.length) return 0
  const withHeatmap = reviewList.value.filter((item) => item.result.annotated_image_url).length
  return Math.round((withHeatmap / reviewList.value.length) * 100)
})

const queueHint = computed(() => {
  if (loading.value) return '队列同步中'
  if (!reviewList.value.length) return '当前无积压'
  if (highRiskCount.value >= 3) return '优先处理高风险'
  if (reviewList.value.length >= 10) return '建议批量清队'
  return '审核节奏平稳'
})

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
  padding: 24px;
  background:
    radial-gradient(circle at top left, rgba(58, 151, 255, 0.08), transparent 26%),
    radial-gradient(circle at top right, rgba(255, 191, 108, 0.12), transparent 22%),
    linear-gradient(180deg, #f4f8fb 0%, #eef3f7 100%);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 28px 30px;
  background:
    linear-gradient(140deg, rgba(255, 255, 255, 0.92), rgba(255, 255, 255, 0.72)),
    linear-gradient(120deg, #dcefff, #fff5e7);
  border: 1px solid rgba(255, 255, 255, 0.78);
  border-radius: 26px;
  box-shadow: 0 22px 52px rgba(22, 45, 72, 0.08);

  .page-title {
    font-size: 24px;
    font-weight: 600;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .page-desc {
    margin: 8px 0 0;
    font-size: 14px;
    color: #617086;
  }
}

.command-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.command-card {
  padding: 18px 20px;
  background:
    linear-gradient(145deg, rgba(255, 255, 255, 0.92), rgba(255, 255, 255, 0.76)),
    linear-gradient(135deg, #e3f2ff, #fff3e0);
  border: 1px solid rgba(255, 255, 255, 0.76);
  border-radius: 20px;
  box-shadow: 0 14px 34px rgba(20, 41, 66, 0.06);

  .command-label {
    display: block;
    margin-bottom: 8px;
    font-size: 12px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #708098;
  }

  strong {
    display: block;
    margin-bottom: 8px;
    font-size: 24px;
    color: #132541;
  }

  p {
    margin: 0;
    font-size: 13px;
    line-height: 1.6;
    color: #5e6e84;
  }
}

.review-list-card {
  border: 1px solid rgba(214, 225, 235, 0.95);
  border-radius: 24px;
  overflow: hidden;
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
    font-size: 16px;
    font-weight: 600;
  }
}

.review-list {
  .review-item {
    display: flex;
    gap: 20px;
    padding: 20px;
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(220, 228, 236, 0.92);
    border-radius: 22px;
    margin-bottom: 16px;
    transition: all 0.3s;

    &:hover {
      border-color: var(--el-color-primary);
      box-shadow: 0 16px 36px rgba(20, 45, 72, 0.1);
      transform: translateY(-2px);
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

      .analysis-head {
        display: flex;
        justify-content: space-between;
        gap: 12px;
        align-items: center;
        margin-bottom: 12px;
      }

      .head-tags {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
      }

      .section-title {
        font-size: 16px;
        font-weight: 600;
        margin: 0;
      }

      .ai-recommendation {
        margin-top: 12px;
        padding: 14px 16px;
        background: linear-gradient(180deg, #fbfdff, #f3f8fc);
        border: 1px solid rgba(15, 108, 189, 0.08);
        border-radius: 14px;
        font-size: 14px;

        strong {
          color: var(--el-text-color-primary);
        }

        p {
          margin: 6px 0 0 0;
          color: var(--el-text-color-regular);
        }
      }

      .review-flags {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 10px;
        margin-top: 12px;
      }

      .flag-item {
        padding: 12px 14px;
        background: rgba(247, 250, 253, 0.95);
        border: 1px solid rgba(21, 35, 62, 0.06);
        border-radius: 12px;
      }

      .flag-label {
        display: block;
        margin-bottom: 6px;
        font-size: 12px;
        color: #738199;
      }

      .flag-item strong {
        font-size: 14px;
        color: #17243d;
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

@media (width <= 900px) {
  .command-grid {
    grid-template-columns: 1fr;
  }

  .review-list .review-item {
    flex-direction: column;
  }

  .review-list .review-item .image-section {
    width: 100%;
  }

  .review-list .review-item .analysis-section .analysis-head,
  .review-list .review-item .analysis-section .review-flags {
    grid-template-columns: 1fr;
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>

