<template>
  <div class="screening-records-page">
    <ElCard shadow="never">
      <!-- 搜索栏 -->
      <div class="search-bar">
        <ElForm :model="searchParams" :inline="true">
          <ElFormItem label="用户ID">
            <ElInput
              v-model="searchParams.userId"
              placeholder="请输入用户ID"
              clearable
              style="width: 180px"
            />
          </ElFormItem>
          <ElFormItem label="关键词">
            <ElInput
              v-model="searchParams.keyword"
              placeholder="用户邮箱/昵称"
              clearable
              style="width: 180px"
            />
          </ElFormItem>
          <ElFormItem label="风险等级">
            <ElSelect
              v-model="searchParams.riskLevel"
              clearable
              placeholder="请选择"
              style="width: 120px"
            >
              <ElOption label="全部" value="" />
              <ElOption label="低风险" value="低风险" />
              <ElOption label="中风险" value="中风险" />
              <ElOption label="高风险" value="高风险" />
              <ElOption label="极高风险" value="极高风险" />
            </ElSelect>
          </ElFormItem>
          <ElFormItem label="评估时间">
            <ElDatePicker
              v-model="searchParams.dateRange"
              type="daterange"
              range-separator="-"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              style="width: 260px"
              value-format="YYYY-MM-DD"
            />
          </ElFormItem>
          <ElFormItem class="search-buttons">
            <ElButton type="primary" @click="handleSearch">
              <i class="iconfont-sys">&#xe7a4;</i>
              查询
            </ElButton>
            <ElButton @click="handleReset">
              <i class="iconfont-sys">&#xe7a6;</i>
              重置
            </ElButton>
          </ElFormItem>
        </ElForm>
      </div>

      <!-- 表格 -->
      <ElTable v-loading="loading" :data="tableData" stripe style="width: 100%; margin-top: 20px">
        <ElTableColumn type="index" label="序号" width="60" />
        <ElTableColumn prop="user_id" label="用户ID" min-width="180" show-overflow-tooltip />
        <ElTableColumn prop="user_nickname" label="用户昵称" min-width="80" show-overflow-tooltip />
        <ElTableColumn prop="created_at" label="评估时间" width="160" />
        <ElTableColumn label="风险分数" width="120">
          <template #default="{ row }">
            <ElTag :type="getRiskTagType(row.riskLevel)"> {{ row.overall_risk_score }}分 </ElTag>
          </template>
        </ElTableColumn>
        <ElTableColumn prop="riskLevel" label="风险等级" width="120">
          <template #default="{ row }">
            <span :style="{ color: getRiskColor(row.overall_risk_level), fontWeight: 'bold' }">
              {{ row.overall_risk_level }}
            </span>
          </template>
        </ElTableColumn>
        <ElTableColumn prop="model_version" label="模型版本" width="120" />
        <ElTableColumn prop="inference_time_ms" label="推理耗时" width="100">
          <template #default="{ row }"> {{ row.inference_time_ms }}ms </template>
        </ElTableColumn>
        <ElTableColumn label="操作" width="200">
          <template #default="{ row }">
            <ElButton link type="primary" @click="viewDetail(row.id)"> 查看详情 </ElButton>

            <ElButton link type="danger" @click="deleteRecord(row.id)"> 删除 </ElButton>
          </template>
        </ElTableColumn>
      </ElTable>

      <!-- 分页 -->
      <div class="pagination">
        <ElPagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchData"
          @current-change="fetchData"
        />
      </div>
    </ElCard>
  </div>
</template>

<script setup lang="ts">
  import { ref, reactive, onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  import { ElMessage, ElMessageBox } from 'element-plus'
  import {
    fetchGetScreeningRecords,
    fetchDeleteScreeningRecord,
    fetchScreeningRecord
  } from '@/api/screening-records'

  const router = useRouter()

  const loading = ref(false)
  const tableData = ref<any[]>([])
  const currentPage = ref(1)
  const pageSize = ref(20)
  const total = ref(0)

  const searchParams = reactive({
    userId: '',
    keyword: '',
    riskLevel: '',
    dateRange: null as [string, string] | null
  })

  onMounted(() => {
    fetchData()
  })

  const fetchData = async () => {
    loading.value = true
    try {
      // 构建请求参数（使用后端 API 要求的字段名）
      const params: any = {
        page: currentPage.value,
        page_size: pageSize.value
      }
      // 只添加有值的参数
      if (searchParams.userId) params.user_id = searchParams.userId
      if (searchParams.keyword) params.keyword = searchParams.keyword
      if (searchParams.riskLevel) params.risk_level = searchParams.riskLevel
      if (searchParams.dateRange && searchParams.dateRange[0])
        params.start_date = searchParams.dateRange[0]
      if (searchParams.dateRange && searchParams.dateRange[1])
        params.end_date = searchParams.dateRange[1]

      const response = (await fetchGetScreeningRecords(params)) as any

      console.log('筛查记录接口返回数据:', response)

      tableData.value = response.records || []
      total.value = response.total || 0
    } catch (error) {
      console.error('获取筛查记录失败:', error)
      ElMessage.error('获取数据失败')
    } finally {
      loading.value = false
    }
  }

  const handleSearch = () => {
    currentPage.value = 1
    fetchData()
  }

  const handleReset = () => {
    searchParams.userId = ''
    searchParams.keyword = ''
    searchParams.riskLevel = ''
    searchParams.dateRange = null
    currentPage.value = 1
    fetchData()
  }

  const viewDetail = async (id: string) => {
    try {
      const res = (await fetchScreeningRecord(id)) as any
      console.log('筛查记录详情:', res)
      // 跳转到详情页，并通过 state 传递数据
      router.push({
        path: `/system/screening-records/detail/${id}`,
        state: {
          recordData: res,
          recordId: id
        }
      })
    } catch (error) {
      console.error('获取筛查记录详情失败:', error)
      ElMessage.error('加载报告失败')
    }
  }

  const deleteRecord = (id: string) => {
    ElMessageBox.confirm('确定要删除这条记录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
      .then(async () => {
        try {
          await fetchDeleteScreeningRecord(id)
          ElMessage.success('删除成功')
          fetchData()
        } catch (error) {
          console.error('删除筛查记录失败:', error)
          ElMessage.error('删除失败')
        }
      })
      .catch(() => {
        // 用户取消操作
      })
  }

  const getRiskTagType = (level: string) => {
    const typeMap: Record<string, 'success' | 'warning' | 'danger' | 'info'> = {
      低风险: 'success',
      中风险: 'warning',
      高风险: 'danger',
      极高风险: 'danger'
    }
    return typeMap[level] || 'info'
  }

  const getRiskColor = (level: string): string => {
    const colorMap: Record<string, string> = {
      低风险: '#52c41a',
      中风险: '#faad14',
      高风险: '#fa8c16',
      极高风险: '#f5222d'
    }
    return colorMap[level] || '#999'
  }
</script>

<style scoped lang="scss">
  .screening-records-page {
    padding: 20px;

    .search-bar {
      :deep(.el-form-item) {
        margin-bottom: 0;
      }

      :deep(.search-buttons) {
        width: 100%;
        margin-top: 18px;
        margin-bottom: 0;

        .el-form-item__content {
          display: flex;
          justify-content: flex-end;
        }
      }

      .iconfont-sys {
        margin-right: 4px;
      }
    }

    .pagination {
      display: flex;
      justify-content: flex-end;
      margin-top: 20px;
    }
  }
</style>
