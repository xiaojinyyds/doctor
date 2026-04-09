<!-- 用户管理 -->
<!-- art-full-height 自动计算出页面剩余高度 -->
<!-- art-table-card 一个符合系统样式的 class，同时自动撑满剩余高度 -->
<!-- 更多 useTable 使用示例请移步至 功能示例 下面的 高级表格示例或者查看官方文档 -->
<!-- useTable 文档：https://www.artd.pro/docs/zh/guide/hooks/use-table.html -->
<template>
  <div class="user-page art-full-height">
    <ElCard class="art-table-card" shadow="never">
      <!-- 搜索栏 -->
      <UserSearch
        v-model="searchForm"
        @search="handleSearch"
        @reset="resetSearchParams"
      ></UserSearch>

      <!-- 表格头部 -->
      <ArtTableHeader v-model:columns="columnChecks" :loading="loading" @refresh="refreshData">
        <template #left>
          <ElSpace wrap>
            <ElButton @click="showDialog('add')" v-ripple>新增用户</ElButton>
          </ElSpace>
        </template>
      </ArtTableHeader>

      <!-- 表格 -->
      <ArtTable
        :loading="loading"
        :data="data"
        :columns="columns"
        :pagination="pagination"
        @selection-change="handleSelectionChange"
        @pagination:size-change="handleSizeChange"
        @pagination:current-change="handleCurrentChange"
      >
      </ArtTable>

      <!-- 用户弹窗 -->
      <UserDialog
        v-model:visible="dialogVisible"
        :type="dialogType"
        :user-data="currentUserData"
        @submit="handleDialogSubmit"
      />
    </ElCard>
  </div>
</template>

<script setup lang="ts">
  import ArtButtonTable from '@/components/core/forms/art-button-table/index.vue'
  import { useTable } from '@/composables/useTable'
  import {
    fetchGetUserList,
    fetchDeleteUser,
    fetchUpdateUserStatus,
    fetchResetUserPassword
  } from '@/api/system-manage'
  import UserSearch from './modules/user-search.vue'
  import UserDialog from './modules/user-dialog.vue'
  import { Key } from '@element-plus/icons-vue'

  defineOptions({ name: 'User' })

  type UserListItem = Api.SystemManage.UserListItem

  // 弹窗相关
  const dialogType = ref<Form.DialogType>('add')
  const dialogVisible = ref(false)
  const currentUserData = ref<Partial<UserListItem>>({})

  // 选中行
  const selectedRows = ref<UserListItem[]>([])

  // 搜索表单
  const searchForm = ref({
    keyword: undefined,
    role: undefined,
    status: undefined
  })

  // 状态切换的加载状态（记录正在切换状态的用户ID）
  const statusChangingIds = ref<Set<string>>(new Set())

  const {
    columns,
    columnChecks,
    data,
    loading,
    pagination,
    getData,
    searchParams,
    resetSearchParams,
    handleSizeChange,
    handleCurrentChange,
    refreshData,
    refreshRemove,
    refreshUpdate
  } = useTable({
    // 核心配置
    core: {
      apiFn: fetchGetUserList,
      apiParams: {
        page: 1,
        size: 20,
        ...searchForm.value
      },
      // 自定义分页字段映射，后端使用 page/size
      paginationKey: {
        current: 'page',
        size: 'size'
      },
      columnsFactory: () => [
        { type: 'selection' }, // 勾选列
        { type: 'index', width: 60, label: '序号' }, // 序号
        {
          prop: 'id',
          label: 'ID',
          width: 280,
          formatter: (row: UserListItem) => {
            return h('span', { style: 'font-family: monospace; font-size: 12px' }, row.id)
          }
        },
        {
          prop: 'nickname',
          label: '用户名'
        },
        {
          prop: 'email',
          label: '邮箱',
          width: 180
        },
        {
          prop: 'role',
          label: '角色',
          width: 100,
          formatter: (row: UserListItem) => {
            const roleMap: Record<string, { label: string; type: any }> = {
              'user': { label: '普通用户', type: 'info' },
              'doctor': { label: '医生', type: 'success' },
              'admin': { label: '管理员', type: 'danger' }
            }
            const roleInfo = roleMap[row.role] || { label: row.role, type: 'info' }
            return h(
              ElTag,
              {
                type: roleInfo.type,
                size: 'small'
              },
              () => roleInfo.label
            )
          }
        },
        {
          prop: 'status',
          label: '状态',
          width: 100,
          formatter: (row: UserListItem) => {
            const isActive = row.status === 'active'
            return h(
              ElTag,
              {
                type: isActive ? 'success' : 'info'
              },
              () => (isActive ? '活跃' : '禁用')
            )
          }
        },
        {
          prop: 'created_at',
          label: '创建时间',
          width: 120,
          sortable: true,
          formatter: (row: UserListItem) => {
            if (!row.created_at) return '-'
            // 提取年月日部分 (YYYY-MM-DD)
            return row.created_at.split('T')[0]
          }
        },
        {
          prop: 'operation',
          label: '操作',
          // fixed: 'right', // 固定列
          formatter: (row: UserListItem) => {
            const isActive = row.status === 'active'
            const isChanging = statusChangingIds.value.has(row.id)
            return h('div', { style: 'display: flex; gap: 4px; align-items: center' }, [
              h(ArtButtonTable, {
                type: 'edit',
                onClick: () => showDialog('edit', row)
              }),
              h(ArtButtonTable, {
                type: 'delete',
                onClick: () => deleteUser(row)
              }),
              h(ElButton, {
                type: 'primary',
                text: true,
                size: 'small',
                style: { margin: 0, padding: '16px 12px', border: '1px solid #dcdfe6' },
                icon: Key,

                onClick: () => resetPassword(row)
              }),
              h(
                ElButton,
                {
                  type: isActive ? 'warning' : 'success',
                  text: true,
                  size: 'small',
                  style: { margin: 0 },
                  loading: isChanging,
                  disabled: isChanging,
                  onClick: () => handleStatusChange(row, isActive ? 'disabled' : 'active')
                },
                () => (isActive ? '禁用' : '启用')
              )
            ])
          }
        }
      ]
    },
    hooks: {
      onSuccess: (data, response) => {
        console.log('数据加载成功:', data)
        console.log('响应数据:', response)
      }
    },
    // 调试配置
    debug: {
      enableLog: true,
      logLevel: 'info'
    }
  })

  /**
   * 搜索处理
   * @param params 参数
   */
  const handleSearch = (params: Record<string, any>) => {
    console.log('搜索参数:', params)
    // 搜索参数赋值
    Object.assign(searchParams, params)
    getData()
  }

  /**
   * 处理用户状态切换
   */
  const handleStatusChange = async (
    row: UserListItem,
    newStatus: 'active' | 'disabled'
  ): Promise<void> => {
    try {
      // 添加到加载状态集合
      statusChangingIds.value.add(row.id)

      // 调用更新状态接口
      await fetchUpdateUserStatus(row.id, newStatus)

      // 显示成功提示
      const statusText = newStatus === 'active' ? '活跃' : '禁用'
      ElMessage.success(`用户状态已更新为：${statusText}`)

      // 更新后刷新（保持当前页）
      await refreshUpdate()
    } catch (error: any) {
      console.error('更新用户状态失败:', error)
      ElMessage.error(error?.message || '状态更新失败，请稍后重试')

      // 刷新数据以恢复原状态
      await refreshUpdate()
    } finally {
      // 从加载状态集合中移除
      statusChangingIds.value.delete(row.id)
    }
  }

  /**
   * 显示用户弹窗
   */
  const showDialog = (type: Form.DialogType, row?: UserListItem): void => {
    console.log('打开弹窗:', { type, row })
    dialogType.value = type
    currentUserData.value = row || {}
    nextTick(() => {
      dialogVisible.value = true
    })
  }

  /**
   * 重置用户密码
   */
  const resetPassword = async (row: UserListItem): Promise<void> => {
    try {
      // 弹出输入框让管理员输入新密码
      const { value: newPassword } = await ElMessageBox.prompt(
        `请为用户 "${row.nickname}" 设置新密码`,
        '重置密码',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          inputType: 'password',
          inputPlaceholder: '请输入新密码（至少6位）',
          inputPattern: /^.{6,}$/,
          inputErrorMessage: '密码长度至少为6位'
        }
      )

      if (!newPassword) {
        ElMessage.warning('请输入新密码')
        return
      }

      // 调用重置密码接口
      await fetchResetUserPassword(row.id, newPassword)

      // 显示成功提示
      ElMessageBox.alert(
        `用户 "${row.nickname}" 的密码已重置成功！\n\n新密码：${newPassword}\n\n请及时告知用户并提醒其修改密码。`,
        '重置成功',
        {
          confirmButtonText: '确定',
          type: 'success'
        }
      )
    } catch (error: any) {
      // 用户取消操作
      if (error === 'cancel') {
        return
      }
      // 重置失败
      console.error('重置密码失败:', error)
      ElMessage.error(error?.message || '重置密码失败，请稍后重试')
    }
  }

  /**
   * 删除用户
   */
  const deleteUser = async (row: UserListItem): Promise<void> => {
    try {
      await ElMessageBox.confirm(
        `确定要删除用户 "${row.nickname}" 吗？此操作不可恢复！`,
        '删除用户',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )

      // 调用删除接口
      await fetchDeleteUser(row.id)

      ElMessage.success('删除成功')

      // 删除后智能刷新（如果当前页为空会自动回到上一页）
      await refreshRemove()
    } catch (error: any) {
      // 用户取消操作
      if (error === 'cancel') {
        return
      }
      // 删除失败
      console.error('删除用户失败:', error)
      ElMessage.error(error?.message || '删除失败，请稍后重试')
    }
  }

  /**
   * 处理弹窗提交事件
   */
  const handleDialogSubmit = async () => {
    try {
      dialogVisible.value = false
      currentUserData.value = {}
      // 刷新列表数据（保持当前页）
      await refreshUpdate()
    } catch (error) {
      console.error('提交失败:', error)
    }
  }

  /**
   * 处理表格行选择变化
   */
  const handleSelectionChange = (selection: UserListItem[]): void => {
    selectedRows.value = selection
    console.log('选中行数据:', selectedRows.value)
  }
</script>

<style lang="scss" scoped>
  // 用户管理页面样式
</style>
