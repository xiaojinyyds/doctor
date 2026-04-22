<template>
  <div class="doctor-workspace">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="8">
        <el-card shadow="hover">
          <el-statistic title="待审核" :value="statistics.pending_count">
            <template #suffix>
              <span style="font-size: 14px; color: #999">条</span>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <el-statistic title="今日已审" :value="statistics.today_reviewed">
            <template #suffix>
              <span style="font-size: 14px; color: #999">条</span>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <el-statistic title="本月筛查" :value="statistics.month_total">
            <template #suffix>
              <span style="font-size: 14px; color: #999">条</span>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 列表卡片 -->
    <el-card class="list-card" style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span style="font-weight: 600; font-size: 16px">待审核列表</span>
          <div>
            <el-radio-group v-model="filterRisk" @change="handleFilterChange" size="default">
              <el-radio-button label="">全部</el-radio-button>
              <el-radio-button label="高风险">高风险</el-radio-button>
              <el-radio-button label="中风险">中风险</el-radio-button>
              <el-radio-button label="低风险">低风险</el-radio-button>
            </el-radio-group>
          </div>
        </div>
      </template>

      <el-table :data="assessmentList" v-loading="loading" stripe>
        <el-table-column label="风险等级" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getRiskTagType(row.overall_risk_level)" effect="dark" size="large">
              {{ row.overall_risk_level }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="patient_name" label="患者" width="120" />

        <el-table-column label="基本信息" width="150">
          <template #default="{ row }">
            <span v-if="row.age && row.gender">{{ row.age }}岁 {{ row.gender }}</span>
            <span v-else style="color: #999">-</span>
          </template>
        </el-table-column>

        <el-table-column label="AI评分" width="100" align="center">
          <template #default="{ row }">
            <span class="risk-score" :style="{ color: getRiskScoreColor(row.overall_risk_score) }">
              {{ (row.overall_risk_score * 100).toFixed(0) }}
            </span>
          </template>
        </el-table-column>

        <el-table-column prop="created_at" label="提交时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleReview(row)">审核</el-button>
            <el-button size="small" @click="handleViewDetail(row.id)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @current-change="loadData"
        @size-change="loadData"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- 审核对话框 -->
    <el-dialog v-model="showReviewDialog" title="审核评估结果" width="800px" :close-on-click-modal="false">
      <div class="review-content" v-if="currentAssessment">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="患者姓名">
            {{ currentAssessment.patient_name }}
          </el-descriptions-item>
          <el-descriptions-item label="基本信息">
            {{ currentAssessment.age }}岁 {{ currentAssessment.gender }}
          </el-descriptions-item>
          <el-descriptions-item label="AI风险等级">
            <el-tag :type="getRiskTagType(currentAssessment.overall_risk_level)" effect="dark">
              {{ currentAssessment.overall_risk_level }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="AI评分">
            <span :style="{ color: getRiskScoreColor(currentAssessment.overall_risk_score), fontWeight: 'bold' }">
              {{ (currentAssessment.overall_risk_score * 100).toFixed(0) }}
            </span>
          </el-descriptions-item>
        </el-descriptions>

        <el-form :model="reviewForm" label-width="120px" style="margin-top: 20px">
          <el-form-item label="审核决定">
            <el-radio-group v-model="reviewForm.action">
              <el-radio label="approve">同意AI判断</el-radio>
              <el-radio label="modify">修改风险等级</el-radio>
              <el-radio label="reject">驳回重评</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item v-if="reviewForm.action === 'modify'" label="修改为">
            <el-select v-model="reviewForm.doctor_risk_level" placeholder="请选择风险等级">
              <el-option label="低风险" value="低风险" />
              <el-option label="中风险" value="中风险" />
              <el-option label="高风险" value="高风险" />
              <el-option label="极高风险" value="极高风险" />
            </el-select>
          </el-form-item>

          <el-form-item v-if="reviewForm.action === 'reject'" label="驳回原因" required>
            <el-input
              v-model="reviewForm.reject_reason"
              type="textarea"
              :rows="4"
              placeholder="请输入驳回原因..."
            />
          </el-form-item>

          <el-form-item label="医生意见">
            <el-input
              v-model="reviewForm.doctor_comment"
              type="textarea"
              :rows="4"
              placeholder="请输入您的专业意见（可选）..."
            />
          </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <el-button @click="showReviewDialog = false">取消</el-button>
        <el-button type="primary" @click="submitReview" :loading="submitting">提交审核</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { fetchPendingAssessments, fetchDoctorStatistics, approveAssessment, rejectAssessment } from '@/api/doctor'
import { useRouter } from 'vue-router'

const router = useRouter()

// 数据
const loading = ref(false)
const assessmentList = ref<any[]>([])
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const filterRisk = ref('')

// 统计数据
const statistics = ref({
  pending_count: 0,
  today_reviewed: 0,
  month_total: 0
})

// 审核对话框
const showReviewDialog = ref(false)
const currentAssessment = ref<any>(null)
const submitting = ref(false)
const reviewForm = ref({
  action: 'approve',
  doctor_risk_level: '',
  doctor_comment: '',
  reject_reason: ''
})

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const res = await fetchPendingAssessments({
      page: page.value,
      page_size: pageSize.value,
      risk_level: filterRisk.value || undefined
    })

    if (res.code === 200) {
      assessmentList.value = res.data.items || []
      total.value = res.data.total || 0
    }
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 加载统计数据
const loadStatistics = async () => {
  try {
    const res = await fetchDoctorStatistics()
    if (res.code === 200) {
      statistics.value = res.data
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

// 筛选变化
const handleFilterChange = () => {
  page.value = 1
  loadData()
}

// 审核
const handleReview = (row: any) => {
  currentAssessment.value = row
  reviewForm.value = {
    action: 'approve',
    doctor_risk_level: '',
    doctor_comment: '',
    reject_reason: ''
  }
  showReviewDialog.value = true
}

// 查看详情
const handleViewDetail = (id: string) => {
  // TODO: 跳转到详情页
  ElMessage.info('详情页面开发中...')
}

// 提交审核
const submitReview = async () => {
  if (!currentAssessment.value) return

  // 验证
  if (reviewForm.value.action === 'reject' && !reviewForm.value.reject_reason) {
    ElMessage.warning('请填写驳回原因')
    return
  }

  submitting.value = true
  try {
    if (reviewForm.value.action === 'reject') {
      // 驳回
      await rejectAssessment(currentAssessment.value.id, {
        reason: reviewForm.value.reject_reason
      })
      ElMessage.success('已驳回')
    } else {
      // 通过或修改
      await approveAssessment(currentAssessment.value.id, {
        doctor_comment: reviewForm.value.doctor_comment,
        doctor_risk_level: reviewForm.value.action === 'modify' ? reviewForm.value.doctor_risk_level : undefined
      })
      ElMessage.success('审核通过')
    }

    showReviewDialog.value = false
    loadData()
    loadStatistics()
  } catch (error) {
    console.error('审核失败:', error)
  } finally {
    submitting.value = false
  }
}

// 工具函数
const getRiskTagType = (level: string) => {
  const map: Record<string, any> = {
    低风险: 'success',
    中风险: 'warning',
    高风险: 'danger',
    极高风险: 'danger'
  }
  return map[level] || 'info'
}

const getRiskScoreColor = (score: number) => {
  if (score >= 0.7) return '#f56c6c'
  if (score >= 0.4) return '#e6a23c'
  return '#67c23a'
}

const formatDateTime = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 初始化
onMounted(() => {
  loadData()
  loadStatistics()
})
</script>

<style scoped lang="scss">
.doctor-workspace {
  padding: 20px;

  .stats-row {
    margin-bottom: 20px;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .risk-score {
    font-size: 18px;
    font-weight: bold;
  }

  .review-content {
    padding: 10px 0;
  }
}
</style>
