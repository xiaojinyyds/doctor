<template>
  <div class="compare-container">
    <el-card>
      <template #header>
        <div class="header-content">
          <h2>历史对比分析</h2>
          <el-button @click="$router.back()">返回</el-button>
        </div>
      </template>

      <div v-loading="loading" class="compare-content">
        <!-- 对比选择 -->
        <div class="compare-selector">
          <el-select v-model="selectedId1" placeholder="选择第一次评估" style="width: 300px">
            <el-option
              v-for="item in historyOptions"
              :key="item.id"
              :label="`${item.date} - ${item.riskScore}分`"
              :value="item.id"
            />
          </el-select>
          <span class="vs-text">VS</span>
          <el-select v-model="selectedId2" placeholder="选择第二次评估" style="width: 300px">
            <el-option
              v-for="item in historyOptions"
              :key="item.id"
              :label="`${item.date} - ${item.riskScore}分`"
              :value="item.id"
            />
          </el-select>
          <el-button type="primary" @click="compareData">对比</el-button>
        </div>

        <!-- 对比结果 -->
        <div v-if="showCompare" class="compare-result">
          <!-- 风险分数对比 -->
          <el-card class="compare-card">
            <template #header>
              <h3>风险分数变化</h3>
            </template>
            <div class="score-compare">
              <div class="score-item">
                <div class="score-label">{{ compareResult.date1 }}</div>
                <div class="score-value" style="color: #fa8c16">{{ compareResult.score1 }}分</div>
              </div>
              <div class="score-arrow">
                <el-icon v-if="compareResult.score1 > compareResult.score2" :size="40" color="#52c41a">
                  <ArrowDown />
                </el-icon>
                <el-icon v-else-if="compareResult.score1 < compareResult.score2" :size="40" color="#f5222d">
                  <ArrowUp />
                </el-icon>
                <el-icon v-else :size="40" color="#999">
                  <Minus />
                </el-icon>
              </div>
              <div class="score-item">
                <div class="score-label">{{ compareResult.date2 }}</div>
                <div class="score-value" style="color: #1890ff">{{ compareResult.score2 }}分</div>
              </div>
            </div>
            <div class="score-summary">
              <el-alert
                v-if="compareResult.score1 > compareResult.score2"
                type="success"
                :closable="false"
                show-icon
              >
                <template #title>
                  风险降低了 {{ Math.abs(compareResult.score1 - compareResult.score2) }} 分，保持良好的生活习惯！
                </template>
              </el-alert>
              <el-alert
                v-else-if="compareResult.score1 < compareResult.score2"
                type="warning"
                :closable="false"
                show-icon
              >
                <template #title>
                  风险升高了 {{ Math.abs(compareResult.score1 - compareResult.score2) }} 分，建议调整生活方式
                </template>
              </el-alert>
              <el-alert v-else type="info" :closable="false" show-icon>
                <template #title>风险分数保持稳定</template>
              </el-alert>
            </div>
          </el-card>

          <!-- TODO: 雷达图对比 -->
          <el-card class="compare-card">
            <template #header>
              <h3>各类风险对比</h3>
            </template>
            <div class="temp-chart">雷达图对比 (待实现)</div>
          </el-card>

          <!-- TODO: 关键因素变化 -->
          <el-card class="compare-card">
            <template #header>
              <h3>关键因素变化</h3>
            </template>
            <el-empty description="因素变化分析待实现" />
          </el-card>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowDown, ArrowUp, Minus } from '@element-plus/icons-vue'

const route = useRoute()
const loading = ref(false)
const showCompare = ref(false)

const selectedId1 = ref('')
const selectedId2 = ref('')

const historyOptions = ref([
  { id: '1', date: '2024-10-12', riskScore: 68 },
  { id: '2', date: '2024-09-15', riskScore: 71 }
])

const compareResult = ref({
  date1: '',
  score1: 0,
  date2: '',
  score2: 0
})

onMounted(() => {
  const id = route.query.id as string
  if (id) {
    selectedId1.value = id
  }
  // TODO: 加载历史记录列表
})

const compareData = () => {
  if (!selectedId1.value || !selectedId2.value) {
    return
  }

  // TODO: 调用后端API获取对比数据
  const record1 = historyOptions.value.find(item => item.id === selectedId1.value)
  const record2 = historyOptions.value.find(item => item.id === selectedId2.value)

  if (record1 && record2) {
    compareResult.value = {
      date1: record1.date,
      score1: record1.riskScore,
      date2: record2.date,
      score2: record2.riskScore
    }
    showCompare.value = true
  }
}
</script>

<style scoped lang="scss">
.compare-container {
  padding: 20px;

  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;

    h2 {
      margin: 0;
      font-size: 20px;
    }
  }

  .compare-selector {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 20px;
    background: #f5f5f5;
    border-radius: 8px;
    margin-bottom: 20px;

    .vs-text {
      font-size: 20px;
      font-weight: bold;
      color: #1890ff;
    }
  }

  .compare-card {
    margin-bottom: 20px;

    h3 {
      margin: 0;
      font-size: 18px;
    }
  }

  .score-compare {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 80px;
    padding: 40px 0;

    .score-item {
      text-align: center;

      .score-label {
        font-size: 14px;
        color: #999;
        margin-bottom: 10px;
      }

      .score-value {
        font-size: 48px;
        font-weight: bold;
      }
    }

    .score-arrow {
      display: flex;
      align-items: center;
    }
  }

  .score-summary {
    margin-top: 20px;
  }

  .temp-chart {
    background: #f5f5f5;
    border: 2px dashed #d9d9d9;
    border-radius: 8px;
    min-height: 300px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #999;
  }
}
</style>

