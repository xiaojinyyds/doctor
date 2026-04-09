<template>
  <div class="knowledge-graph-page">
    <!-- 顶部切换标签 -->
    <el-card>
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="通用知识图谱" name="general" />
        <el-tab-pane label="个性化风险图谱" name="personal" />
      </el-tabs>
    </el-card>

    <!-- 通用知识图谱 -->
    <div v-show="activeTab === 'general'" class="graph-container">
      <el-card v-loading="generalLoading">
        <template #header>
          <div class="card-header">
            <span>肿瘤疾病知识图谱</span>
            <div>
              <el-tooltip content="刷新数据">
                <el-button circle @click="loadGeneralGraph">
                  <el-icon><Refresh /></el-icon>
                </el-button>
              </el-tooltip>
              <el-tooltip content="图谱说明">
                <el-button circle @click="showGraphInfo">
                  <el-icon><InfoFilled /></el-icon>
                </el-button>
              </el-tooltip>
            </div>
          </div>
        </template>

        <el-alert
          title="图谱操作提示"
          description="鼠标滚轮可缩放，拖拽可移动视图，点击节点可高亮相关节点，节点可拖动调整位置"
          type="info"
          :closable="true"
          show-icon
          style="margin-bottom: 16px"
        />

        <!-- 图例说明 -->
        <div class="legend-box">
          <div class="legend-item">
            <span class="legend-dot" style="background: #ff4d4f"></span>
            <span>疾病</span>
          </div>
          <div class="legend-item">
            <span class="legend-dot" style="background: #ffa940"></span>
            <span>风险因素</span>
          </div>
          <div class="legend-item">
            <span class="legend-dot" style="background: #1890ff"></span>
            <span>症状</span>
          </div>
          <div class="legend-item">
            <span class="legend-dot" style="background: #52c41a"></span>
            <span>筛查方法</span>
          </div>
        </div>

        <!-- 知识图谱展示 -->
        <art-graph-chart
          :nodes="generalGraphData.nodes"
          :edges="generalGraphData.edges"
          :categories="generalGraphData.categories"
          :loading="generalLoading"
          height="700px"
          layout="force"
          :roam="true"
          :draggable="true"
        />
      </el-card>
    </div>

    <!-- 个性化风险图谱 -->
    <div v-show="activeTab === 'personal'" class="graph-container">
      <!-- 选择评估记录 -->
      <el-card style="margin-bottom: 16px">
        <el-form :inline="true">
          <el-form-item label="选择评估记录">
            <el-select
              v-model="selectedAssessmentId"
              placeholder="请选择评估记录"
              style="width: 300px"
              :loading="assessmentListLoading"
              @change="handleAssessmentChange"
            >
              <el-option
                v-for="record in assessmentList"
                :key="record.id"
                :label="`${formatDate(record.created_at)} - ${record.overall_risk_level}`"
                :value="record.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :disabled="!selectedAssessmentId" @click="loadPersonalGraph">
              <el-icon><Search /></el-icon>
              生成图谱
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 个性化图谱展示 -->
      <el-card v-if="personalGraphData.nodes.length > 0" v-loading="personalLoading">
        <template #header>
          <div class="card-header">
            <span>您的个性化风险图谱</span>
            <el-tag :type="getRiskLevelColor(assessmentInfo.risk_level)">
              {{ assessmentInfo.risk_level }}
            </el-tag>
          </div>
        </template>

        <el-alert
          :title="`风险评分: ${(assessmentInfo.risk_score * 100).toFixed(1)}分`"
          :description="`评估时间: ${formatDate(assessmentInfo.created_at)}`"
          type="warning"
          show-icon
          style="margin-bottom: 16px"
        />

        <!-- 图例说明 -->
        <div class="legend-box">
          <div class="legend-item">
            <span class="legend-dot" style="background: #722ed1"></span>
            <span>您</span>
          </div>
          <div class="legend-item">
            <span class="legend-dot" style="background: #ffa940"></span>
            <span>您的风险因素</span>
          </div>
          <div class="legend-item">
            <span class="legend-dot" style="background: #ff4d4f"></span>
            <span>高风险疾病</span>
          </div>
          <div class="legend-item">
            <span class="legend-dot" style="background: #52c41a"></span>
            <span>推荐筛查</span>
          </div>
        </div>

        <!-- 个性化图谱 -->
        <art-graph-chart
          :nodes="personalGraphData.nodes"
          :edges="personalGraphData.edges"
          :categories="personalGraphData.categories"
          :loading="personalLoading"
          height="700px"
          layout="force"
          :roam="true"
          :draggable="true"
        />
      </el-card>

      <!-- 空状态 -->
      <el-card v-else>
        <el-empty description="请先选择一条评估记录">
          <el-button type="primary" @click="$router.push('/questionnaire')"> 去评估 </el-button>
        </el-empty>
      </el-card>
    </div>

    <!-- 图谱说明对话框 -->
    <el-dialog v-model="infoModalVisible" title="知识图谱说明" width="600px">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="疾病节点">
          <el-tag type="danger">红色圆点</el-tag>
          代表肿瘤疾病，如肺癌、胃癌等
        </el-descriptions-item>
        <el-descriptions-item label="风险因素">
          <el-tag type="warning">橙色圆点</el-tag>
          代表致癌风险因素，如吸烟、年龄等
        </el-descriptions-item>
        <el-descriptions-item label="症状">
          <el-tag type="primary">蓝色圆点</el-tag>
          代表常见症状，如咳嗽、胸痛等
        </el-descriptions-item>
        <el-descriptions-item label="筛查方法">
          <el-tag type="success">绿色圆点</el-tag>
          代表推荐的筛查方法，如CT、胃镜等
        </el-descriptions-item>
        <el-descriptions-item label="连线说明">
          <strong>实线：</strong>风险因素与疾病的关联<br />
          <strong>虚线：</strong>疾病与症状的关联<br />
          <strong>点线：</strong>疾病与筛查方法的关联<br />
          线条粗细代表关联强度
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
  import { ref, reactive, onMounted } from 'vue'
  import { fetchKnowledgeGraph, fetchUserRiskGraph } from '@/api/knowledge'
  import { fetchAssessmentHistory } from '@/api/assessment'
  import ArtGraphChart from '@/components/core/charts/art-graph-chart/index.vue'
  import { Refresh, InfoFilled, Search } from '@element-plus/icons-vue'

  defineOptions({ name: 'KnowledgeGraph' })

  // 标签页
  const activeTab = ref('general')

  // 通用知识图谱
  const generalLoading = ref(false)
  const generalGraphData = reactive({
    nodes: [] as any[],
    edges: [] as any[],
    categories: [] as any[]
  })

  // 个性化图谱
  const personalLoading = ref(false)
  const assessmentListLoading = ref(false)
  const selectedAssessmentId = ref<string>()
  const assessmentList = ref<any[]>([])
  const personalGraphData = reactive({
    nodes: [] as any[],
    edges: [] as any[],
    categories: [] as any[]
  })
  const assessmentInfo = reactive({
    assessment_id: '',
    risk_level: '',
    risk_score: 0,
    created_at: ''
  })

  // 对话框
  const infoModalVisible = ref(false)

  // 加载通用知识图谱
  const loadGeneralGraph = async () => {
    generalLoading.value = true
    try {
      const res = await fetchKnowledgeGraph()
      // HTTP拦截器已经解包了data，直接访问res.nodes
      if (res && res.nodes) {
        generalGraphData.nodes = res.nodes || []
        generalGraphData.edges = res.edges || []
        generalGraphData.categories = res.categories || []
      }
    } catch (error: any) {
      console.error('加载知识图谱失败:', error)
    } finally {
      generalLoading.value = false
    }
  }

  // 加载评估记录列表
  const loadAssessmentList = async () => {
    assessmentListLoading.value = true
    try {
      const res = await fetchAssessmentHistory({ page: 1, page_size: 50 })
      assessmentList.value = res.records || []
    } catch (error: any) {
      console.error('加载评估记录失败:', error)
    } finally {
      assessmentListLoading.value = false
    }
  }

  // 加载个性化图谱
  const loadPersonalGraph = async () => {
    if (!selectedAssessmentId.value) {
      return
    }

    personalLoading.value = true
    try {
      const res = await fetchUserRiskGraph(selectedAssessmentId.value)

      // HTTP拦截器已解包，直接访问res.graph
      if (res && res.graph) {
        personalGraphData.nodes = res.graph.nodes || []
        personalGraphData.edges = res.graph.edges || []
        personalGraphData.categories = res.graph.categories || []

        assessmentInfo.assessment_id = res.assessment_info?.assessment_id || ''
        assessmentInfo.risk_level = res.assessment_info?.risk_level || ''
        assessmentInfo.risk_score = res.assessment_info?.risk_score || 0
        assessmentInfo.created_at = res.assessment_info?.created_at || ''
      }
    } catch (error: any) {
      console.error('生成个性化图谱失败:', error)
    } finally {
      personalLoading.value = false
    }
  }

  // 标签页切换
  const handleTabChange = (name: string | number) => {
    const key = String(name)
    if (key === 'general' && generalGraphData.nodes.length === 0) {
      loadGeneralGraph()
    } else if (key === 'personal' && assessmentList.value.length === 0) {
      loadAssessmentList()
    }
  }

  // 评估记录切换
  const handleAssessmentChange = () => {
    // 切换后不自动加载，等用户点击按钮
  }

  // 显示图谱说明
  const showGraphInfo = () => {
    infoModalVisible.value = true
  }

  // 格式化日期
  const formatDate = (date: string) => {
    if (!date) return ''
    const d = new Date(date)
    const year = d.getFullYear()
    const month = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    const hours = String(d.getHours()).padStart(2, '0')
    const minutes = String(d.getMinutes()).padStart(2, '0')
    return `${year}-${month}-${day} ${hours}:${minutes}`
  }

  // 获取风险等级颜色
  const getRiskLevelColor = (level: string) => {
    const colorMap: Record<string, any> = {
      低风险: 'success',
      中低风险: 'primary',
      中高风险: 'warning',
      高风险: 'danger'
    }
    return colorMap[level] || ''
  }

  // 初始化
  onMounted(() => {
    loadGeneralGraph()
  })
</script>

<style lang="scss" scoped>
  .knowledge-graph-page {
    padding: 16px;

    .graph-container {
      min-height: 600px;
      margin-top: 16px;
    }

    .card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .legend-box {
      display: flex;
      gap: 24px;
      padding: 12px;
      margin-bottom: 16px;
      background: var(--el-fill-color-light);
      border-radius: 4px;

      .legend-item {
        display: flex;
        align-items: center;
        font-size: 14px;

        .legend-dot {
          display: inline-block;
          width: 12px;
          height: 12px;
          margin-right: 6px;
          border-radius: 50%;
        }
      }
    }
  }
</style>
