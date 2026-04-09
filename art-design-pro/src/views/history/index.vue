<template>
  <div class="history-container">
    <el-card>
      <template #header>
        <div class="header-content">
          <h2>筛查历史记录</h2>
        </div>
      </template>

      <el-table v-loading="loading" :data="historyList" stripe>
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="created_at" label="评估时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="综合风险" width="120">
          <template #default="{ row }">
            <el-tag :type="getRiskTagType(row.overall_risk_level)">
              {{ (row.overall_risk_score * 100).toFixed(0) }}分
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="overall_risk_level" label="风险等级" width="120">
          <template #default="{ row }">
            <span :style="{ color: getRiskColor(row.overall_risk_level) }">
              {{ row.overall_risk_level }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="分享状态" width="150">
          <template #default="{ row }">
            <div v-if="row.share_info">
              <div v-if="row.share_info.is_expired" style="color: #909399">
                <el-icon><CircleClose /></el-icon>
                已过期
              </div>
              <div v-else style="color: #67c23a">
                <el-icon><Share /></el-icon>
                已分享 ({{ row.share_info.view_count || 0 }}次)
              </div>
            </div>
            <span v-else style="color: #909399">未分享</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button link type="primary" size="small" @click="viewReport(row.id)">
                <el-icon><Document /></el-icon>
                查看报告
              </el-button>
              
              <el-button link type="info" size="small" @click="compareReport(row.id)">
                <el-icon><TrendCharts /></el-icon>
                对比分析
              </el-button>
              
              <!-- 分享相关按钮 -->
              <template v-if="row.share_info && !row.share_info.is_expired">
                <el-dropdown @command="(cmd) => handleShareCommand(cmd, row)">
                  <el-button link type="warning" size="small">
                    <el-icon><Share /></el-icon>
                    已分享
                    <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="view">
                        <el-icon><Link /></el-icon>
                        查看链接
                      </el-dropdown-item>
                      <el-dropdown-item command="cancel" divided>
                        <el-icon><CircleClose /></el-icon>
                        取消分享
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </template>
              <el-button v-else link type="success" size="small" @click="createShare(row.id)">
                <el-icon><Share /></el-icon>
                分享
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchHistory"
          @current-change="fetchHistory"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { CircleClose, Share, Document, TrendCharts, Link, ArrowDown } from '@element-plus/icons-vue'
import request from '@/utils/http'
import ShareDialog from '@/views/risk/components/ShareDialog.vue'

const router = useRouter()

const loading = ref(false)
const historyList = ref<any[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const showShareDialog = ref(false)
const currentAssessmentId = ref<string | null>(null)
const viewLinkDialogVisible = ref(false)
const currentShareLink = ref('')

onMounted(() => {
  fetchHistory()
})

/**
 * 获取历史记录（后端已包含分享信息）
 */
const fetchHistory = async () => {
  loading.value = true
  try {
    const res: any = await request.get({
      url: '/api/v1/assessment/history',
      params: {
        page: currentPage.value,
        page_size: pageSize.value
      }
    })
    
    // res 已经是 data 部分，因为 http utility 返回 res.data.data
    historyList.value = res.records || []
    total.value = res.total || 0
    
  } catch (error: any) {
    console.error('获取历史记录失败', error)
    ElMessage.error(error?.response?.data?.detail || '获取历史记录失败')
  } finally {
    loading.value = false
  }
}

const viewReport = (id: string) => {
  router.push(`/report/${id}`)
}

const compareReport = (id: string) => {
  router.push(`/history/compare?id=${id}`)
}

/**
 * 创建分享
 */
const createShare = (assessmentId: string) => {
  currentAssessmentId.value = assessmentId
  showShareDialog.value = true
}

/**
 * 处理分享下拉菜单命令
 */
const handleShareCommand = (command: string, row: any) => {
  if (command === 'view') {
    viewShareLink(row)
  } else if (command === 'cancel') {
    cancelShare(row)
  }
}

/**
 * 查看分享链接
 */
const viewShareLink = (row: any) => {
  if (!row.share_info) return
  
  const shareUrl = `${window.location.origin}/#/share/${row.share_info.share_token}`
  
  ElMessageBox.alert(
    `<div style="word-break: break-all;">
      <p><strong>分享链接：</strong></p>
      <p style="background: #f5f7fa; padding: 10px; border-radius: 4px;">${shareUrl}</p>
      <p style="margin-top: 10px;"><strong>有效期：</strong>${row.share_info.expire_at ? formatDate(row.share_info.expire_at) : '永久'}</p>
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
const cancelShare = async (row: any) => {
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
    await request.del({
      url: `/api/v1/share/${row.share_info.share_token}`
    })
    
    ElMessage.success('分享已取消')
    
    // 刷新列表
    await fetchHistory()
    
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('取消分享失败', error)
      ElMessage.error(error?.response?.data?.detail || '取消分享失败')
    }
  } finally {
    loading.value = false
  }
}

/**
 * 分享对话框关闭后的处理
 */
const handleShareDialogClose = () => {
  showShareDialog.value = false
  currentAssessmentId.value = null
}

/**
 * 格式化日期
 */
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

const getRiskTagType = (level: string) => {
  const typeMap: Record<string, any> = {
    '低风险': 'success',
    '中风险': 'warning',
    '高风险': 'danger',
    '极高风险': 'danger'
  }
  return typeMap[level] || 'info'
}

const getRiskColor = (level: string) => {
  const colorMap: Record<string, string> = {
    '低风险': '#52c41a',
    '中风险': '#faad14',
    '高风险': '#fa8c16',
    '极高风险': '#f5222d'
  }
  return colorMap[level] || '#999'
}
</script>

<!-- 分享对话框 -->
<ShareDialog
  v-model="showShareDialog"
  :assessment-id="currentAssessmentId"
  @success="fetchHistory"
  @update:model-value="handleShareDialogClose"
/>

<style scoped lang="scss">
.history-container {
  padding: 20px;

  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;

    h2 {
      margin: 0;
      font-size: 20px;
    }

    .header-actions {
      display: flex;
      gap: 10px;
    }
  }

  .pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
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

