<template>
  <div class="risk-page">
    <div class="toolbar">
      <ElButton type="primary" @click="openApply">申请评估</ElButton>
      <ElButton
        type="success"
        :disabled="selectedIds.length !== 2"
        @click="openCompare"
      >
        <i class="iconfont-sys">&#xe7a3;</i>
        对比分析 {{ selectedIds.length > 0 ? `(已选${selectedIds.length}条)` : '' }}
      </ElButton>
      <ElButton
        v-if="selectedIds.length > 0"
        text
        @click="clearSelection"
      >
        清空选择
      </ElButton>
    </div>

    <ElDivider class="primary-divider" />

    <div class="list">
      <div v-if="loading">加载中...</div>
      <div v-else>
        <template v-if="Array.isArray(items) && items.length > 0">
          <ElTable
            :data="items"
            size="small"
            class="risk-table"
            style="width: 100%"
            @selection-change="handleSelectionChange"
          >
            <ElTableColumn type="selection" width="55" :selectable="checkSelectable" />
            <ElTableColumn prop="id" label="ID" min-width="220" />
            <ElTableColumn label="创建时间" min-width="180">
              <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
            </ElTableColumn>
            <ElTableColumn prop="age" label="年龄" width="80" />
            <ElTableColumn prop="gender" label="性别" width="80" />
            <ElTableColumn prop="overall_risk_level" label="总体风险等级" min-width="120" />
            <ElTableColumn prop="overall_risk_score" label="总体风险分" min-width="120" />
            <ElTableColumn prop="questionnaire_id" label="问卷ID" min-width="220" />
            <ElTableColumn label="操作" fixed="right" width="260">
              <template #default="{ row }">
                <div class="action-buttons">
                  <ElButton 
                    type="primary" 
                    link 
                    size="small" 
                    @click="openView(row)"
                  >
                    <el-icon><View /></el-icon>
                    查看
                  </ElButton>
                  
                  <ElButton
                    type="success"
                    link
                    size="small"
                    :loading="exportingId === row.id"
                    @click="onExport(row)"
                  >
                    <el-icon><Download /></el-icon>
                    导出
                  </ElButton>
                  
                  <!-- 分享按钮：根据 share_info 显示不同状态 -->
                  <template v-if="row.share_info && !row.share_info.is_expired">
                    <ElDropdown @command="(cmd) => handleShareCommand(cmd, row)">
                      <ElButton type="warning" link size="small">
                        <el-icon><Share /></el-icon>
                        已分享
                        <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                      </ElButton>
                      <template #dropdown>
                        <ElDropdownMenu>
                          <ElDropdownItem command="view">
                            <el-icon><Link /></el-icon>
                            查看链接
                          </ElDropdownItem>
                          <ElDropdownItem command="cancel" divided>
                            <el-icon><CircleClose /></el-icon>
                            取消分享
                          </ElDropdownItem>
                        </ElDropdownMenu>
                      </template>
                    </ElDropdown>
                  </template>
                  <ElButton
                    v-else
                    type="warning"
                    link
                    size="small"
                    @click="openShare(row)"
                  >
                    <el-icon><Share /></el-icon>
                    分享
                  </ElButton>
                  
                  <ElButton
                    type="danger"
                    link
                    size="small"
                    :loading="deletingId === row.id"
                    @click="onDelete(row)"
                  >
                    <el-icon><Delete /></el-icon>
                    删除
                  </ElButton>
                </div>
              </template>
            </ElTableColumn>
          </ElTable>
        </template>
        <template v-else>
          <div class="empty">暂无数据</div>
        </template>
      </div>
    </div>
    <div class="pager">
      <ElButton @click="prevPage" :disabled="page <= 1">上一页</ElButton>
      <span>第 {{ page }} 页 · 每页 {{ pageSize }} 条</span>
      <ElButton @click="nextPage">下一页</ElButton>
    </div>
    <AssessmentApplyDialog v-model="applyVisible" @submitted="loadList" />
    <AssessmentViewDialog v-model="viewVisible" :record-id="currentId" />
    <CompareDialog v-model="compareVisible" :id1="compareId1" :id2="compareId2" />
    <ShareDialog v-model="shareVisible" :assessment-id="shareAssessmentId" @success="loadList" />
  </div>
</template>

<script setup lang="ts">
  import { onMounted, ref } from 'vue'
  import {
    fetchAssessmentHistory,
    deleteAssessmentRecord,
    exportAssessment
  } from '@/api/assessment'
  import html2pdf from 'html2pdf.js'
  import AssessmentApplyDialog from './components/AssessmentApplyDialog.vue'
  import AssessmentViewDialog from './components/AssessmentViewDialog.vue'
  import CompareDialog from './components/CompareDialog.vue'
  import ShareDialog from './components/ShareDialog.vue'
  import { ElMessage, ElMessageBox } from 'element-plus'
  import { View, Download, Share, Delete, Link, CircleClose, ArrowDown } from '@element-plus/icons-vue'

  defineOptions({ name: 'RiskIndex' })

  const items = ref<any[]>([])
  const loading = ref(false)
  const page = ref(1)
  const pageSize = ref(10)
  const applyVisible = ref(false)
  const deletingId = ref<string | null>(null)
  const exportingId = ref<string | null>(null)
  const viewVisible = ref(false)
  const currentId = ref<string | null>(null)
  
  // 对比功能相关
  const compareVisible = ref(false)
  const compareId1 = ref<string | null>(null)
  const compareId2 = ref<string | null>(null)
  const selectedIds = ref<string[]>([])
  
  // 分享功能相关
  const shareVisible = ref(false)
  const shareAssessmentId = ref<string | null>(null)

  function buildReportHtml(res: any) {
    const user = res?.user_info || {}
    const report = res?.report_info || {}
    const assess = res?.assessment_result || {}
    const q = res?.questionnaire_data || {}

    const categoryRisks = assess?.category_risks || {}
    const keyFactors = assess?.key_factors || []
    const recs = assess?.recommendations || []
    const overall = assess?.overall_risk || {}

    const now = formatTime(new Date().toISOString())
    const style = `
      <style>
        .report-root{font-family: -apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica,Arial,'PingFang SC','Microsoft Yahei','Noto Sans SC',sans-serif; color:#000; background:#fff; width: 794px; /* ~A4 width at 96dpi */ padding:24px;}
        h1{margin:0 0 12px;font-size:22px}
        h2{margin:18px 0 8px;font-size:18px;border-left:4px solid #409EFF;padding-left:8px}
        table{width:100%;border-collapse:collapse;margin:8px 0 16px}
        th,td{border:1px solid #e5e7eb;padding:8px;text-align:left;font-size:12px;vertical-align: top}
        th{background:#f7f9fc;font-weight:600}
        .meta{display:flex;gap:24px;flex-wrap:wrap;margin-bottom:8px}
        .muted{color:#606266}
        .section{page-break-inside: avoid}
        .footer{margin-top:24px;text-align:right;color:#606266;font-size:12px}
        .wrap { white-space: pre-wrap; }
      </style>
    `

    const categoryRows = Object.keys(categoryRisks)
      .map(
        (k) => `
      <tr><td>${k}</td><td>${safe(categoryRisks[k]?.level)}</td><td>${safe(categoryRisks[k]?.score)}</td></tr>
    `
      )
      .join('')

    const factorRows = (Array.isArray(keyFactors) ? keyFactors : [])
      .slice(0, 20)
      .map(
        (f: any) => `
      <tr>
        <td>${safe(f?.factor)}</td>
        <td>${safe(f?.direction)}</td>
        <td>${safe(f?.importance)}</td>
        <td>${safe(f?.contribution)}</td>
        <td>${safe(f?.description)}</td>
      </tr>
    `
      )
      .join('')

    const recRows = (Array.isArray(recs) ? recs : [])
      .map(
        (r: any) => `
      <tr>
        <td>${safe(r?.category)}</td>
        <td>${safe(r?.title)}</td>
        <td>${safe(r?.priority)}</td>
        <td class="wrap">${safe(r?.content)}</td>
        <td>${formatTime(r?.created_at)}</td>
      </tr>
    `
      )
      .join('')

    const html = `
      ${style}
      <div class="report-root">
        <h1>风险评估报告</h1>
        <div class="meta">
          <div>姓名：${safe(user?.name)}</div>
          <div>年龄：${safe(user?.age)}</div>
          <div>性别：${safe(user?.gender)}</div>
          <div>BMI：${safe(user?.bmi)}</div>
        </div>
        <div class="meta muted">
          <div>评估日期：${formatTime(report?.assessment_date)}</div>
          <div>生成时间：${formatTime(report?.generated_at)}</div>
          <div>报告ID：${safe(report?.report_id)}</div>
        </div>

        <div class="section">
          <h2>总体风险</h2>
          <table><tbody>
            <tr><th>等级</th><td>${safe(overall?.level)}</td><th>分数</th><td>${safe(overall?.score)}</td><th>百分位</th><td>${safe(overall?.percentile)}</td></tr>
          </tbody></table>
        </div>

        <div class="section">
          <h2>分类风险</h2>
          <table><thead><tr><th>类别</th><th>风险等级</th><th>风险分</th></tr></thead><tbody>
            ${categoryRows || '<tr><td colspan="3">-</td></tr>'}
          </tbody></table>
        </div>

        <div class="section">
          <h2>关键因素</h2>
          <table><thead><tr><th>因素</th><th>方向</th><th>重要性</th><th>贡献度</th><th>描述</th></tr></thead><tbody>
            ${factorRows || '<tr><td colspan="5">-</td></tr>'}
          </tbody></table>
        </div>

        <div class="section">
          <h2>问卷摘要</h2>
          <table><tbody>
            <tr><th>慢性病</th><td>${text(q?.chronic_diseases)}</td></tr>
            <tr><th>家族史</th><td>${text(q?.family_cancer_history)}</td></tr>
            <tr><th>症状</th><td>${text(q?.symptoms)}</td></tr>
            <tr><th>运动习惯</th><td>${safe(q?.exercise_habit)}</td></tr>
          </tbody></table>
        </div>

        <div class="section">
          <h2>建议</h2>
          <table>
            <thead>
              <tr><th>类别</th><th>标题</th><th>优先级</th><th>内容</th><th>时间</th></tr>
            </thead>
            <tbody>
              ${recRows || '<tr><td colspan="5">-</td></tr>'}
            </tbody>
          </table>
        </div>

        <div class="footer">导出时间：${now}</div>
      </div>
    `
    return html
  }

  async function loadList() {
    loading.value = true
    try {
      const res: any = await fetchAssessmentHistory({ page: page.value, page_size: pageSize.value })
      console.log(res)
      items.value = res.records.map((item: any) => ({
        ...item,
        created_at: formatTime(item.created_at)
      }))
    } catch (e) {
      console.error('[Risk] fetch list error:', e)
      items.value = []
    } finally {
      loading.value = false
    }
  }

  function prevPage() {
    if (page.value > 1) {
      page.value -= 1
      loadList()
    }
  }
  function nextPage() {
    page.value += 1
    loadList()
  }

  function openApply() {
    applyVisible.value = true
  }

  function openView(row: any) {
    currentId.value = String(row.id)
    viewVisible.value = true
  }

  /**
   * 打开对比对话框
   */
  function openCompare() {
    if (selectedIds.value.length !== 2) {
      ElMessage.warning('请选择2条评估记录进行对比')
      return
    }
    
    // 按时间顺序排列（旧的在前）
    const sorted = selectedIds.value.map(id => {
      const item = items.value.find(i => i.id === id)
      return { id, created_at: item?.created_at || '' }
    }).sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
    
    compareId1.value = sorted[0].id
    compareId2.value = sorted[1].id
    compareVisible.value = true
  }

  /**
   * 处理选择变化
   */
  function handleSelectionChange(selection: any[]) {
    selectedIds.value = selection.map(item => item.id)
  }

  /**
   * 检查行是否可选择（限制最多选2条）
   */
  function checkSelectable(row: any, index: number): boolean {
    // 如果已选2条且当前行未被选中，则不可选
    if (selectedIds.value.length >= 2 && !selectedIds.value.includes(row.id)) {
      return false
    }
    return true
  }

  /**
   * 清空选择
   */
  function clearSelection() {
    selectedIds.value = []
  }

  /**
   * 打开分享对话框
   */
  function openShare(row: any) {
    shareAssessmentId.value = String(row.id)
    shareVisible.value = true
  }

  async function onExport(row: any) {
    try {
      exportingId.value = row.id
      const data = await exportAssessment(String(row.id))
      console.log('[Risk] export json:', data)
      await generateAndDownloadPdf(data)
      ElMessage.success('PDF 已开始下载')
    } catch (e) {
      console.error('[Risk] export error:', e)
    } finally {
      exportingId.value = null
    }
  }

  async function onDelete(row: any) {
    try {
      await ElMessageBox.confirm('确认删除该记录？', '提示', { type: 'warning' })
    } catch {
      return
    }
    try {
      deletingId.value = row.id
      await deleteAssessmentRecord(String(row.id))
      ElMessage.success('删除成功')
      await loadList()
    } catch (e) {
      console.error('[Risk] delete error:', e)
    } finally {
      deletingId.value = null
    }
  }

  onMounted(() => {
    loadList()
  })

  function pad2(n: number) {
    return n < 10 ? `0${n}` : String(n)
  }
  function formatTime(v: any): string {
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

  function safe(v: any, d: any = '-') {
    return v ?? d
  }
  function text(v: any) {
    try {
      return Array.isArray(v) ? v.join('、') : String(v ?? '-')
    } catch {
      return '-'
    }
  }

  async function generateAndDownloadPdf(res: any) {
    try {
      const html = buildReportHtml(res)
      const container = document.createElement('div')
      container.style.position = 'fixed'
      container.style.left = '-99999px'
      container.innerHTML = html
      document.body.appendChild(container)

      const fileName = `风险评估报告_${safe(res?.user_info?.name, '匿名')}_${formatTime(res?.report_info?.generated_at).replace(/[:\\s]/g, '-')}.pdf`
      const source = container.querySelector('.report-root') || container
      await html2pdf()
        .set({
          margin: 10,
          filename: fileName,
          image: { type: 'jpeg', quality: 0.98 },
          html2canvas: { scale: 2, useCORS: true },
          jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
        })
        .from(source as HTMLElement)
        .save()

      container.remove()
    } catch (e) {
      console.error('generateAndDownloadPdf failed:', e)
      // 退回打印预览方案
      openReportWindowFallback(res)
    }
  }

  function openReportWindowFallback(payload: any) {
    const w = window.open('', '_blank')
    if (!w) return
    w.document.write(
      '<pre>' +
        (typeof payload === 'string' ? payload : JSON.stringify(payload, null, 2)) +
        '</pre>'
    )
    w.document.close()
    w.focus()
    setTimeout(() => {
      w.print()
    }, 300)
  }

  /**
   * 处理分享下拉菜单命令
   */
  function handleShareCommand(command: string, row: any) {
    if (command === 'view') {
      viewShareLink(row)
    } else if (command === 'cancel') {
      cancelShare(row)
    }
  }

  /**
   * 查看分享链接
   */
  function viewShareLink(row: any) {
    if (!row.share_info) return
    
    const shareUrl = `${window.location.origin}/#/share/${row.share_info.share_token}`
    
    ElMessageBox.alert(
      `<div style="word-break: break-all;">
        <p><strong>分享链接：</strong></p>
        <p style="background: #f5f7fa; padding: 10px; border-radius: 4px;">${shareUrl}</p>
        <p style="margin-top: 10px;"><strong>有效期：</strong>${row.share_info.expire_at ? formatTime(row.share_info.expire_at) : '永久'}</p>
        <p><strong>访问密码：</strong>${row.share_info.has_password ? '已设置' : '无'}</p>
        <p><strong>查看次数：</strong>${row.share_info.view_count || 0} 次</p>
      </div>`,
      '分享链接详情',
      {
        dangerouslyUseHTMLString: true,
        confirmButtonText: '复制链接',
        showCancelButton: true,
        cancelButtonText: '关闭'
      }
    ).then(() => {
      // 复制链接
      navigator.clipboard.writeText(shareUrl).then(() => {
        ElMessage.success('链接已复制到剪贴板')
      }).catch(() => {
        ElMessage.error('复制失败')
      })
    }).catch(() => {})
  }

  /**
   * 取消分享
   */
  async function cancelShare(row: any) {
    if (!row.share_info) return
    
    try {
      await ElMessageBox.confirm(
        '取消分享后，之前的分享链接将失效，确定要取消吗？',
        '确认取消分享',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
      
      loading.value = true
      
      // 调用后端DELETE接口
      const request = (await import('@/utils/http')).default
      await request.del({
        url: `/api/v1/share/${row.share_info.share_token}`
      })
      
      ElMessage.success('分享已取消')
      
      // 刷新列表
      await loadList()
      
    } catch (error: any) {
      if (error !== 'cancel') {
        console.error('取消分享失败', error)
        ElMessage.error(error?.response?.data?.detail || '取消分享失败')
      }
    } finally {
      loading.value = false
    }
  }
</script>

<style scoped>
  .risk-page {
    display: flex;
    flex-direction: column;
    min-height: 90%;
    padding: 16px;
  }

  .toolbar {
    margin-bottom: 16px;
    display: flex;
    gap: 12px;
    align-items: center;
    
    .iconfont-sys {
      margin-right: 4px;
    }
  }

  .list {
    display: flex;
    flex: 1;
    flex-direction: column;
    min-height: 400px;
  }

  .list-item {
    margin-bottom: 12px;
  }

  .empty {
    color: var(--el-text-color-secondary);
  }

  .pager {
    display: flex;
    gap: 8px;
    align-items: center;
    justify-content: flex-end;
    padding: 20px 16px 16px; /* 上 右 下 左 */
    margin-top: 12px;
  }

  /* 自定义分隔线为主题蓝色 */
  .primary-divider {
    --el-border-color: var(--el-color-primary);
  }

  /* 表格视觉增强：更大字号与纯黑文本 */
  .risk-table :deep(.el-table__inner-wrapper),
  .risk-table :deep(.el-table__header),
  .risk-table :deep(.el-table__body) {
    font-size: 14px;
    color: #000;
  }

  .risk-table :deep(.el-table__header th) {
    font-weight: 600;
    color: #000;
  }

  /* 操作按钮样式 */
  .action-buttons {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    align-items: center;
  }

  .action-buttons .el-button {
    margin: 0;
    padding: 4px 8px;
  }

  .action-buttons .el-icon {
    margin-right: 2px;
  }
</style>
