<template>
  <div class="medical-image-upload-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <i class="iconfont-sys">&#xe667;</i>
          乳腺超声影像智能识别
        </h1>
        <p class="page-desc">
          上传乳腺超声图像，AI自动识别病灶类型，提供专业医疗建议
        </p>
        <div class="model-info">
          <el-tag type="success" effect="plain">
            <i class="el-icon-cpu"></i>
            ResNet18深度学习模型
          </el-tag>
          <el-tag type="primary" effect="plain">
            <i class="el-icon-data-analysis"></i>
            准确率86.44%
          </el-tag>
          <el-tag type="warning" effect="plain">
            <i class="el-icon-time"></i>
            推理时间&lt;200ms
          </el-tag>
        </div>
      </div>
    </div>

    <!-- 主要内容 -->
    <el-row :gutter="24">
      <!-- 左侧：上传区域 -->
      <el-col :xs="24" :lg="12">
        <el-card class="upload-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>
                <i class="iconfont-sys">&#xe621;</i>
                上传影像
              </span>
            </div>
          </template>

          <!-- 上传组件 -->
          <el-upload
            ref="uploadRef"
            class="image-uploader"
            :auto-upload="false"
            :show-file-list="false"
            :on-change="handleFileChange"
            :before-upload="beforeUpload"
            accept="image/png,image/jpeg,image/jpg"
            drag
          >
            <div v-if="!imageUrl" class="upload-placeholder">
              <i class="el-icon-upload"></i>
              <div class="upload-text">点击或拖拽上传乳腺超声图像</div>
              <div class="upload-hint">支持 PNG、JPG 格式，文件大小不超过10MB</div>
            </div>
            <div v-else class="image-preview">
              <el-image
                :src="imageUrl"
                fit="contain"
                class="preview-image"
                :preview-src-list="[imageUrl]"
              />
              <span class="delete-icon" @click.stop="clearImage">×</span>
            </div>
          </el-upload>

          <!-- 分析按钮 -->
          <div class="action-btns">
            <el-button
              type="primary"
              size="large"
              :loading="analyzing"
              :disabled="!imageFile"
              @click="analyzeImage"
              class="analyze-btn"
            >
              <i v-if="!analyzing" class="el-icon-data-analysis"></i>
              {{ analyzing ? '分析中...' : '开始AI分析' }}
            </el-button>
            <el-button size="large" :disabled="!imageFile" @click="clearImage">
              <i class="el-icon-refresh-left"></i>
              重新选择
            </el-button>
          </div>

          <!-- 标注图展示（在上传卡片内） -->
          <div
            v-if="analysisResult && analysisResult.analysis.annotated_image_url"
            class="annotated-section"
          >
            <div class="annotated-header">
              <h4>
                <i class="el-icon-picture-outline"></i>
                AI病灶标注图
              </h4>
              <el-tag type="warning" size="small" effect="plain">
                <i class="el-icon-warning"></i>
                圆圈标注为可疑区域
              </el-tag>
            </div>
            <el-image
              :src="analysisResult.analysis.annotated_image_url"
              fit="contain"
              class="annotated-preview"
              :preview-src-list="[
                analysisResult.image.file_url,
                analysisResult.analysis.annotated_image_url
              ]"
            >
              <template #error>
                <div class="image-error-box">
                  <i class="el-icon-picture-outline"></i>
                  <span>标注图加载失败</span>
                </div>
              </template>
            </el-image>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：分析结果 -->
      <el-col :xs="24" :lg="12">
        <el-card class="result-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <span>
                <i class="iconfont-sys">&#xe61b;</i>
                分析结果
              </span>
            </div>
          </template>

          <!-- 分析结果展示 -->
          <div v-if="analysisResult" class="result-content">
            <!-- 预测类别 -->
            <div class="result-main">
              <div class="result-icon" :class="`result-${analysisResult.analysis.risk_level}`">
                <i class="el-icon-success" v-if="analysisResult.analysis.predicted_class === '正常'"></i>
                <i
                  class="el-icon-warning"
                  v-else-if="analysisResult.analysis.predicted_class === '良性肿瘤'"
                ></i>
                <i class="el-icon-warning" v-else></i>
              </div>
              <h2 class="result-title">{{ analysisResult.analysis.predicted_class }}</h2>
              <div class="confidence-badge" :class="`confidence-${getConfidenceLevel()}`">
                置信度: {{ analysisResult.analysis.confidence_percentage }}
              </div>
            </div>

            <!-- 风险等级 -->
            <el-alert
              :title="analysisResult.analysis.risk_level"
              :type="getRiskAlertType()"
              :closable="false"
              class="risk-alert"
            >
              <template #default>
                <p>{{ analysisResult.analysis.recommendation }}</p>
              </template>
            </el-alert>

            <!-- 概率分布 -->
            <div class="probabilities">
              <h4 class="section-title">各类别概率分布</h4>
              <div
                v-for="(prob, className) in analysisResult.analysis.probabilities"
                :key="className"
                class="prob-item"
              >
                <div class="prob-label">
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

            <!-- 分析详情 -->
            <div class="analysis-details">
              <h4 class="section-title">分析详情</h4>
              <el-descriptions :column="1" border size="small">
                <el-descriptions-item label="影像ID">
                  {{ analysisResult.image.id }}
                </el-descriptions-item>
                <el-descriptions-item label="文件名">
                  {{ analysisResult.image.filename }}
                </el-descriptions-item>
                <el-descriptions-item label="图像尺寸">
                  {{ analysisResult.image.size }}
                </el-descriptions-item>
                <el-descriptions-item label="推理时间">
                  {{ analysisResult.analysis.inference_time_ms }} ms
                </el-descriptions-item>
                <el-descriptions-item label="分析时间">
                  {{ formatDateTime(analysisResult.analysis.analyzed_at) }}
                </el-descriptions-item>
              </el-descriptions>
            </div>

            <!-- 操作按钮 -->
            <div class="result-actions">
              <el-button type="success" @click="viewHistory">
                <i class="el-icon-view"></i>
                查看历史记录
              </el-button>
              <el-button type="primary" @click="analyzeAgain">
                <i class="el-icon-refresh"></i>
                继续分析
              </el-button>
            </div>
          </div>

          <!-- 空状态 -->
          <el-empty v-else description="请上传图像进行分析" :image-size="120" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 使用说明 -->
    <el-card class="guide-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>
            <i class="el-icon-question"></i>
            使用说明
          </span>
        </div>
      </template>
      <el-row :gutter="16">
        <el-col :xs="24" :sm="12" :md="6">
          <div class="guide-item">
            <div class="guide-icon">1</div>
            <h4>上传图像</h4>
            <p>选择或拖拽乳腺超声图像文件</p>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="guide-item">
            <div class="guide-icon">2</div>
            <h4>AI分析</h4>
            <p>ResNet18深度学习模型自动识别</p>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="guide-item">
            <div class="guide-icon">3</div>
            <h4>查看结果</h4>
            <p>获取预测类别和置信度</p>
          </div>
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <div class="guide-item">
            <div class="guide-icon">4</div>
            <h4>专业建议</h4>
            <p>获取AI生成的医疗建议</p>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 免责声明 -->
    <el-alert
      title="免责声明"
      type="warning"
      :closable="false"
      show-icon
      class="disclaimer"
    >
      本系统提供的AI分析结果仅供参考，不能替代专业医生的诊断。请务必咨询专业医生进行确诊。
    </el-alert>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type UploadFile } from 'element-plus'
import { medicalImageAPI } from '@/api/medical-image'

const router = useRouter()

// 状态
const imageFile = ref<File | null>(null)
const imageUrl = ref<string>('')
const analyzing = ref(false)
const analysisResult = ref<any>(null)
const uploadRef = ref()

// 文件选择处理
const handleFileChange = (file: UploadFile) => {
  const rawFile = file.raw as File
  if (!rawFile) return

  // 创建预览URL
  imageUrl.value = URL.createObjectURL(rawFile)
  imageFile.value = rawFile
  analysisResult.value = null
}

// 上传前验证
const beforeUpload = (file: File) => {
  const isImage = file.type.startsWith('image/')
  const isLt10M = file.size / 1024 / 1024 < 10

  if (!isImage) {
    ElMessage.error('只能上传图像文件！')
    return false
  }
  if (!isLt10M) {
    ElMessage.error('图像大小不能超过 10MB!')
    return false
  }
  return true
}

// 清除图像
const clearImage = () => {
  if (imageUrl.value) {
    URL.revokeObjectURL(imageUrl.value)
  }
  imageUrl.value = ''
  imageFile.value = null
  analysisResult.value = null
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}

// 分析图像
const analyzeImage = async () => {
  if (!imageFile.value) {
    ElMessage.warning('请先选择图像')
    return
  }

  analyzing.value = true

  try {
    const formData = new FormData()
    formData.append('file', imageFile.value)

    const params = {
      image_type: 'breast_ultrasound',
      body_part: 'breast',
      generate_heatmap: false
    }

    // HTTP工具会自动提取 data 字段，所以 response 就是实际数据
    const response: any = await medicalImageAPI.uploadAndAnalyze(formData, params)

    // response 已经是 { image: {...}, analysis: {...} }
    analysisResult.value = response
    ElMessage.success('分析完成！')

    // 如果是高风险，额外提示
    if (response.analysis.risk_level === '高风险') {
      ElMessageBox.alert(
        '检测到高风险病变，强烈建议尽快就医进行专业诊断！',
        '重要提示',
        {
          confirmButtonText: '知道了',
          type: 'warning'
        }
      )
    }
  } catch (error: any) {
    ElMessage.error(error.message || '分析失败，请重试')
    console.error('分析失败:', error)
  } finally {
    analyzing.value = false
  }
}

// 获取置信度等级
const getConfidenceLevel = () => {
  if (!analysisResult.value) return 'low'
  const conf = analysisResult.value.analysis.confidence
  if (conf >= 0.9) return 'high'
  if (conf >= 0.7) return 'medium'
  return 'low'
}

// 获取风险提示类型
const getRiskAlertType = () => {
  if (!analysisResult.value) return 'info'
  const riskLevel = analysisResult.value.analysis.risk_level
  if (riskLevel === '低风险') return 'success'
  if (riskLevel === '中风险') return 'warning'
  return 'error'
}

// 获取进度条颜色
const getProgressColor = (className: string): string => {
  if (className === '正常') return '#67C23A'
  if (className === '良性肿瘤') return '#E6A23C'
  return '#F56C6C'
}

// 格式化日期时间
const formatDateTime = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

// 查看历史记录
const viewHistory = () => {
  router.push('/medical-image/history')
}

// 继续分析
const analyzeAgain = () => {
  clearImage()
}

// 页面卸载时清理
onUnmounted(() => {
  if (imageUrl.value) {
    URL.revokeObjectURL(imageUrl.value)
  }
})
</script>

<style scoped lang="scss">
.medical-image-upload-container {
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;
  padding: 32px;
  background: linear-gradient(to right, #f5f7fa 0%, #e8f4f8 100%);
  border-radius: 12px;
  border: 1px solid #e4e7ed;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);

  .header-content {
    max-width: 1200px;
    margin: 0 auto;
  }

  .page-title {
    font-size: 32px;
    font-weight: 600;
    margin: 0 0 12px 0;
    display: flex;
    align-items: center;
    gap: 12px;
    color: #303133;

    i {
      font-size: 36px;
      color: #409eff;
    }
  }

  .page-desc {
    font-size: 16px;
    color: #606266;
    margin: 0 0 16px 0;
  }

  .model-info {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
  }
}

.upload-card {
  .card-header {
    font-size: 18px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 8px;
  }
}

.result-card {
  min-height: 600px;

  .card-header {
    font-size: 18px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 8px;
  }
}

.image-uploader {
  :deep(.el-upload) {
    width: 100%;
  }

  :deep(.el-upload-dragger) {
    width: 100%;
    height: 400px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 2px dashed var(--el-border-color);
    border-radius: 8px;
    transition: all 0.3s;

    &:hover {
      border-color: var(--el-color-primary);
    }
  }
}

.upload-placeholder {
  text-align: center;

  i {
    font-size: 64px;
    color: var(--el-color-primary);
    margin-bottom: 16px;
  }

  .upload-text {
    font-size: 16px;
    color: var(--el-text-color-primary);
    margin-bottom: 8px;
  }

  .upload-hint {
    font-size: 14px;
    color: var(--el-text-color-secondary);
  }
}

.image-preview {
  position: relative;
  width: 100%;
  height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;

  .preview-image {
    max-width: 100%;
    max-height: 100%;
    border-radius: 8px;
  }

  .delete-icon {
    position: absolute;
    top: 10px;
    right: 10px;
    width: 32px;
    height: 32px;
    background: rgba(255, 255, 255, 0.95);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    font-weight: bold;
    color: #606266;
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    transition: all 0.3s;

    &:hover {
      background: #f56c6c;
      color: white;
      transform: scale(1.1);
    }
  }
}

.action-btns {
  margin-top: 24px;
  display: flex;
  gap: 12px;
  justify-content: center;

  .analyze-btn {
    min-width: 160px;
  }
}

.annotated-section {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 2px dashed var(--el-border-color);

  .annotated-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;

    h4 {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
      color: var(--el-text-color-primary);
      display: flex;
      align-items: center;
      gap: 8px;

      i {
        color: var(--el-color-warning);
      }
    }
  }

  .annotated-preview {
    width: 100%;
    max-height: 400px;
    border-radius: 8px;
    border: 2px solid var(--el-color-warning-light-5);
    box-shadow: 0 2px 12px rgba(230, 162, 60, 0.15);
    cursor: pointer;
    transition: all 0.3s;

    &:hover {
      border-color: var(--el-color-warning);
      box-shadow: 0 4px 16px rgba(230, 162, 60, 0.25);
    }
  }

  .image-error-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 200px;
    color: var(--el-text-color-secondary);

    i {
      font-size: 48px;
      margin-bottom: 8px;
    }
  }
}

.result-content {

  .result-main {
    text-align: center;
    padding: 24px 0;
    margin-bottom: 24px;
    border-bottom: 1px solid var(--el-border-color-light);

    .result-icon {
      width: 80px;
      height: 80px;
      margin: 0 auto 16px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 40px;

      &.result-低风险 {
        background: rgba(103, 194, 58, 0.1);
        color: #67c23a;
      }

      &.result-中风险 {
        background: rgba(230, 162, 60, 0.1);
        color: #e6a23c;
      }

      &.result-高风险 {
        background: rgba(245, 108, 108, 0.1);
        color: #f56c6c;
      }
    }

    .result-title {
      font-size: 28px;
      font-weight: 600;
      margin: 0 0 12px 0;
    }

    .confidence-badge {
      display: inline-block;
      padding: 6px 16px;
      border-radius: 16px;
      font-size: 14px;
      font-weight: 500;

      &.confidence-high {
        background: rgba(103, 194, 58, 0.1);
        color: #67c23a;
      }

      &.confidence-medium {
        background: rgba(230, 162, 60, 0.1);
        color: #e6a23c;
      }

      &.confidence-low {
        background: rgba(245, 108, 108, 0.1);
        color: #f56c6c;
      }
    }
  }

  .risk-alert {
    margin-bottom: 24px;
  }

  .probabilities {
    margin-bottom: 24px;

    .prob-item {
      margin-bottom: 16px;

      &:last-child {
        margin-bottom: 0;
      }
    }

    .prob-label {
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

  .analysis-details {
    margin-bottom: 24px;
  }

  .section-title {
    font-size: 16px;
    font-weight: 600;
    margin: 0 0 16px 0;
    color: var(--el-text-color-primary);
  }

  .result-actions {
    display: flex;
    gap: 12px;
    justify-content: center;
  }
}

.guide-card {
  margin-top: 24px;

  .guide-item {
    text-align: center;
    padding: 20px;

    .guide-icon {
      width: 48px;
      height: 48px;
      margin: 0 auto 12px;
      border-radius: 50%;
      background: var(--el-color-primary);
      color: white;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      font-weight: 600;
    }

    h4 {
      font-size: 16px;
      margin: 0 0 8px 0;
    }

    p {
      font-size: 14px;
      color: var(--el-text-color-secondary);
      margin: 0;
    }
  }
}

.disclaimer {
  margin-top: 24px;
}
</style>

