<template>
  <ElDialog
    v-model="visible"
    title="评估详情"
    width="80vw"
    :close-on-click-modal="false"
    class="view-dialog"
  >
    <div v-if="loading" class="loading-wrap">
      <ElSkeleton :rows="10" animated />
    </div>
    <div v-else class="layout">
      <aside class="sidenav">
        <ElMenu :default-active="active" class="menu" @select="onSelect">
          <ElMenuItem index="overview">总览</ElMenuItem>
          <ElMenuItem index="category">分类风险</ElMenuItem>
          <ElMenuItem index="factors">关键因素</ElMenuItem>
          <ElMenuItem index="questionnaire">问卷信息</ElMenuItem>
          <ElMenuItem index="recommendations">建议</ElMenuItem>
          <ElMenuItem index="ai-recommendation">AI建议</ElMenuItem>
        </ElMenu>
      </aside>
      <section class="content" ref="contentRef">
        <!-- 总览 -->
        <ElCard class="block" id="overview">
          <template #header>
            <div class="block-title">总览</div>
          </template>
          <ElDescriptions :column="3" border>
            <ElDescriptionsItem label="总体风险等级">{{ overall.level || '-' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="总体风险分">{{ overall.score ?? '-' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="百分位">{{ overall.percentile ?? '-' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="推理耗时(ms)">{{
              assessment.inference_time_ms ?? '-'
            }}</ElDescriptionsItem>
            <ElDescriptionsItem label="记录ID">{{ base.id || '-' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="创建时间">{{ fmtTime(base.created_at) }}</ElDescriptionsItem>
          </ElDescriptions>
        </ElCard>

        <!-- 分类风险 -->
        <ElCard class="block" id="category">
          <template #header>
            <div class="block-title">分类风险</div>
          </template>
          <ElTable :data="categoryRows" size="small">
            <ElTableColumn prop="name" label="类别" min-width="140" />
            <ElTableColumn prop="level" label="风险等级" min-width="120" />
            <ElTableColumn prop="score" label="风险分" min-width="160" />
          </ElTable>
        </ElCard>

        <!-- 关键因素 -->
        <ElCard class="block" id="factors">
          <template #header>
            <div class="block-title">关键因素</div>
          </template>
          <ElTable :data="keyFactors" size="small">
            <ElTableColumn prop="factor" label="因素" min-width="140" />
            <ElTableColumn prop="direction" label="方向" width="100" />
            <ElTableColumn prop="importance" label="重要性" min-width="120" />
            <ElTableColumn prop="contribution" label="贡献度" min-width="120" />
            <ElTableColumn prop="description" label="描述" min-width="260" />
          </ElTable>
        </ElCard>

        <!-- 问卷信息 -->
        <ElCard class="block" id="questionnaire">
          <template #header>
            <div class="block-title">问卷信息</div>
          </template>
          <ElDescriptions :column="3" border>
            <ElDescriptionsItem label="年龄">{{ q.age ?? '-' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="性别">{{ q.gender || '-' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="身高(cm)">{{ q.height ?? '-' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="体重(kg)">{{ q.weight ?? '-' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="BMI">{{ q.bmi ?? '-' }}</ElDescriptionsItem>
            <ElDescriptionsItem label="是否吸烟">{{
              bool(q?.smoking_history?.is_smoking)
            }}</ElDescriptionsItem>
            <ElDescriptionsItem label="运动习惯" :span="2">{{
              q.exercise_habit || '-'
            }}</ElDescriptionsItem>
            <ElDescriptionsItem label="症状" :span="3">
              <div class="chips"
                ><ElTag v-for="(it, i) in arr(q.symptoms)" :key="i" type="warning" effect="plain">{{
                  it
                }}</ElTag
                ><span v-if="!arr(q.symptoms).length">-</span></div
              >
            </ElDescriptionsItem>
            <ElDescriptionsItem label="慢性病" :span="3">
              <div class="chips"
                ><ElTag v-for="(it, i) in arr(q.chronic_diseases)" :key="i" effect="plain">{{
                  it
                }}</ElTag
                ><span v-if="!arr(q.chronic_diseases).length">-</span></div
              >
            </ElDescriptionsItem>
            <ElDescriptionsItem label="家族史" :span="3">
              <div class="chips"
                ><ElTag
                  v-for="(it, i) in arr(q.family_cancer_history)"
                  :key="i"
                  type="info"
                  effect="plain"
                  >{{ it }}</ElTag
                ><span v-if="!arr(q.family_cancer_history).length">-</span></div
              >
            </ElDescriptionsItem>
            <ElDescriptionsItem label="创建时间">{{ fmtTime(q.created_at) }}</ElDescriptionsItem>
            <ElDescriptionsItem label="更新时间">{{ fmtTime(q.updated_at) }}</ElDescriptionsItem>
            <ElDescriptionsItem label="状态">{{ q.status || '-' }}</ElDescriptionsItem>
          </ElDescriptions>
        </ElCard>

        <!-- 建议 -->
        <ElCard class="block" id="recommendations">
          <template #header>
            <div class="block-title">建议</div>
          </template>
          <ElTimeline>
            <ElTimelineItem
              v-for="(rec, idx) in recs"
              :key="idx"
              :timestamp="fmtTime(rec.created_at) || ''"
              placement="top"
            >
              <ElCard shadow="never" class="rec-card">
                <div class="rec-header">
                  <div class="rec-title">
                    <ElTag type="success" effect="dark" class="mr8">{{
                      rec.category || '建议'
                    }}</ElTag>
                    <strong>{{ rec.title || '无标题' }}</strong>
                  </div>
                  <ElTag :type="priorityType(rec.priority)" effect="plain"
                    >优先级：{{ rec.priority ?? '-' }}</ElTag
                  >
                </div>
                <div class="rec-content">{{ rec.content || '-' }}</div>
              </ElCard>
            </ElTimelineItem>
          </ElTimeline>
        </ElCard>

        <!-- AI个性化建议 -->
        <ElCard class="block ai-recommendation-card" id="ai-recommendation">
          <template #header>
            <div class="block-title" style="display: flex; align-items: center; gap: 10px;">
              <span>AI个性化健康建议</span>
              <ElTag type="success" size="small" effect="dark">GLM-4.6</ElTag>
              <div style="flex: 1"></div>
              <ElButton
                v-if="!aiRecommendation && !isGeneratingAI"
                type="primary"
                size="small"
                @click="generateAIRecommendation"
              >
                生成AI建议
              </ElButton>
              <ElButton
                v-if="aiRecommendation && !isGeneratingAI"
                type="default"
                size="small"
                @click="regenerateAIRecommendation"
              >
                重新生成
              </ElButton>
            </div>
          </template>
          
          <div class="ai-content">
            <!-- 生成中 -->
            <div v-if="isGeneratingAI" class="ai-generating">
              <div class="generating-header">
                <ElIcon class="is-loading" :size="18"><Loading /></ElIcon>
                <span>AI正在思考中，请稍候...</span>
              </div>
              <div class="ai-text-stream">
                {{ aiStreamText }}
                <span class="cursor-blink">|</span>
              </div>
            </div>
            
            <!-- 已生成 -->
            <div v-else-if="aiRecommendation" class="ai-generated">
              <div class="ai-text">{{ aiRecommendation }}</div>
              <div class="ai-footer">
                <ElIcon><InfoFilled /></ElIcon>
                <span>此建议由智谱GLM-4.6大模型生成，仅供参考，不构成医疗诊断。</span>
              </div>
            </div>
            
            <!-- 未生成 -->
            <div v-else class="ai-empty">
              <ElEmpty description="暂无AI建议">
                <ElButton type="primary" @click="generateAIRecommendation">
                  立即生成AI个性化建议
                </ElButton>
              </ElEmpty>
            </div>
          </div>
        </ElCard>
      </section>
    </div>
    <template #footer>
      <ElButton type="primary" @click="close">关闭</ElButton>
    </template>
  </ElDialog>
</template>

<script setup lang="ts">
  import { ref, watch, computed, nextTick } from 'vue'
  import { ElMessage } from 'element-plus'
  import { Loading, InfoFilled } from '@element-plus/icons-vue'
  import { fetchAssessmentRecord } from '@/api/assessment'
  import { useUserStore } from '@/store/modules/user'

  const userStore = useUserStore()

  const props = withDefaults(defineProps<{ modelValue: boolean; recordId: string | null }>(), {
    modelValue: false,
    recordId: null
  })
  const emit = defineEmits<{ (e: 'update:modelValue', v: boolean): void }>()

  const visible = ref(false)
  const loading = ref(false)
  const raw = ref<Record<string, any>>({})
  const active = ref('overview')
  const contentRef = ref<HTMLElement | null>(null)

  // AI建议相关
  const aiRecommendation = ref('')
  const isGeneratingAI = ref(false)
  const aiStreamText = ref('')

  watch(
    () => props.modelValue,
    async (v) => {
      visible.value = v
      if (v && props.recordId) {
        await loadDetail(props.recordId)
        await nextTick()
        scrollTo('overview')
      }
    },
    { immediate: true }
  )
  watch(visible, (v) => emit('update:modelValue', v))

  const base = computed(() => raw.value?.assessment || {})
  const assessment = computed(() => raw.value?.assessment || {})
  const overall = computed(() => assessment.value?.overall_risk || {})
  const categoryRows = computed(() => toCategoryRows(assessment.value?.category_risks))
  const keyFactors = computed(() => arr(assessment.value?.key_factors))
  const q = computed(() => raw.value?.questionnaire || {})
  const recs = computed(() => arr(raw.value?.recommendations))

  function arr(v: any): any[] {
    return Array.isArray(v) ? v : v ? [v] : []
  }
  function bool(v: any) {
    return v === true ? '是' : v === false ? '否' : (v ?? '-')
  }
  function toCategoryRows(obj: Record<string, any> | undefined): any[] {
    if (!obj || typeof obj !== 'object') return []
    return Object.keys(obj).map((k) => ({ name: k, level: obj[k]?.level, score: obj[k]?.score }))
  }
  function priorityType(p: any) {
    if (p === 1) return 'danger'
    if (p === 2) return 'warning'
    return 'info'
  }

  function pad2(n: number) {
    return n < 10 ? `0${n}` : String(n)
  }
  function fmtTime(v: any): string {
    if (!v) return '-'
    const d = new Date(v)
    if (isNaN(d.getTime())) return String(v)
    const Y = d.getFullYear()
    const M = pad2(d.getMonth() + 1)
    const D = pad2(d.getDate())
    const h = pad2(d.getHours())
    const m = pad2(d.getMinutes())
    return `${Y}-${M}-${D} ${h}:${m}`
  }

  function onSelect(key: string) {
    active.value = key
    scrollTo(key)
  }
  function scrollTo(id: string) {
    const el = contentRef.value?.querySelector(`#${id}`) as HTMLElement | null
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  async function loadDetail(id: string) {
    loading.value = true
    aiRecommendation.value = ''
    aiStreamText.value = ''
    isGeneratingAI.value = false
    
    try {
      const res: any = await fetchAssessmentRecord(id)
      raw.value = res?.data || res || {}
      
      // 检查是否已有AI建议
      if (assessment.value?.ai_recommendation) {
        aiRecommendation.value = assessment.value.ai_recommendation
      }
    } catch (e) {
      console.error('[Assessment] fetch detail error:', e)
      raw.value = {}
    } finally {
      loading.value = false
    }
  }

  /**
   * 生成AI个性化建议（SSE流式）
   */
  async function generateAIRecommendation() {
    const assessmentId = props.recordId
    
    if (!assessmentId) {
      ElMessage.error('评估ID不存在')
      return
    }
    
    isGeneratingAI.value = true
    aiStreamText.value = ''
    aiRecommendation.value = ''
    
    try {
      const token = userStore.accessToken
      const apiUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
      const url = `${apiUrl}/api/v1/assessment/${assessmentId}/ai-recommendation`
      
      // 使用fetch实现SSE（支持Authorization header）
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      
      // 读取流式响应
      const reader = response.body?.getReader()
      const decoder = new TextDecoder()
      
      if (!reader) {
        throw new Error('无法读取响应流')
      }
      
      // 逐块读取数据
      while (true) {
        const { done, value } = await reader.read()
        
        if (done) {
          // 流结束
          if (aiStreamText.value) {
            aiRecommendation.value = aiStreamText.value
            ElMessage.success('AI建议生成成功')
          }
          isGeneratingAI.value = false
          break
        }
        
        // 解码数据
        const chunk = decoder.decode(value, { stream: true })
        
        // 处理SSE格式数据（data: {...}\n\n）
        const lines = chunk.split('\n')
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const jsonStr = line.substring(6) // 去掉 "data: "
              const data = JSON.parse(jsonStr)
              
              if (data.type === 'start') {
                console.log('开始生成:', data.message)
              } else if (data.type === 'text') {
                // 追加文本
                aiStreamText.value += data.content
              } else if (data.type === 'done') {
                // 生成完成
                console.log('生成完成:', data.message)
              } else if (data.type === 'error') {
                ElMessage.error(`生成失败: ${data.message}`)
              }
            } catch (e) {
              console.error('解析SSE数据失败:', e, line)
            }
          }
        }
      }
      
    } catch (error) {
      console.error('生成AI建议失败:', error)
      ElMessage.error('生成失败，请重试')
      isGeneratingAI.value = false
    }
  }

  /**
   * 重新生成AI建议
   */
  function regenerateAIRecommendation() {
    aiRecommendation.value = ''
    generateAIRecommendation()
  }

  function close() {
    visible.value = false
  }
</script>

<style scoped>
  .view-dialog :deep(.el-dialog__body) {
    padding-top: 8px;
  }

  .loading-wrap {
    padding: 12px;
  }

  .layout {
    display: grid;
    grid-template-columns: 220px 1fr;
    gap: 12px;
    min-height: 640px;
  }

  .sidenav {
    padding-right: 8px;
    border-right: 1px solid var(--el-border-color);
  }

  .menu {
    border-right: none;
  }

  .content {
    max-height: 75vh;
    padding-left: 4px;
    overflow: auto;
  }

  .view-dialog :deep(.el-dialog) {
    max-width: 1280px;
  }

  .block {
    margin-bottom: 12px;
  }

  .block-title {
    font-weight: 600;
    color: #000;
  }

  .chips {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }

  .rec-card {
    border: 1px solid var(--el-border-color-light);
  }

  .rec-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 6px;
  }

  .rec-title {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .mr8 {
    margin-right: 8px;
  }

  /* AI建议卡片样式 */
  .ai-recommendation-card {
    border: 2px solid #67c23a !important;
  }

  .ai-content {
    min-height: 150px;
  }

  .ai-generating {
    .generating-header {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 15px;
      color: var(--el-color-primary);
      font-size: 14px;
    }
    
    .ai-text-stream {
      font-size: 15px;
      line-height: 1.8;
      padding: 20px;
      background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
      border-radius: 8px;
      min-height: 100px;
      white-space: pre-wrap;
      word-wrap: break-word;
      
      .cursor-blink {
        display: inline-block;
        animation: blink 1s infinite;
        color: var(--el-color-primary);
        font-weight: bold;
      }
    }
  }

  .ai-generated {
    .ai-text {
      font-size: 15px;
      line-height: 1.8;
      padding: 20px;
      background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
      border-radius: 8px;
      margin-bottom: 15px;
      white-space: pre-wrap;
      word-wrap: break-word;
      box-shadow: 0 2px 8px rgba(103, 194, 58, 0.1);
    }
    
    .ai-footer {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 12px;
      color: #909399;
    }
  }

  .ai-empty {
    padding: 20px;
    text-align: center;
  }

  @keyframes blink {
    0%, 50% {
      opacity: 1;
    }
    51%, 100% {
      opacity: 0;
    }
  }
</style>
