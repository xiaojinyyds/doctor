<template>
  <div class="user-docs-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <div class="header-content">
        <i class="iconfont-sys">&#xe788;</i>
        <div class="header-text">
          <h1>肿瘤数智化筛查系统 - 使用文档</h1>
          <p>帮助您快速了解和使用系统的各项功能</p>
        </div>
      </div>
    </div>

    <!-- 文档内容 -->
    <div class="docs-content">
      <!-- 系统介绍 -->
      <el-card class="doc-section" shadow="hover">
        <template #header>
          <div class="section-header">
            <i class="iconfont-sys">&#xe86e;</i>
            <span>系统介绍</span>
          </div>
        </template>
        <div class="section-content">
          <p class="intro-text">
            肿瘤数智化筛查系统是一个集健康问卷、风险评估、医学影像分析于一体的智能化健康管理平台。
            系统采用先进的人工智能技术，为用户提供专业、便捷的健康筛查服务。
          </p>
          <div class="feature-grid">
            <div class="feature-item">
              <div class="feature-icon" style="background: rgba(64, 158, 255, 0.1)">
                <i class="iconfont-sys" style="color: #409eff">&#xe788;</i>
              </div>
              <h4>健康问卷</h4>
              <p>通过科学的问卷调查，全面了解您的健康状况</p>
            </div>
            <div class="feature-item">
              <div class="feature-icon" style="background: rgba(103, 194, 58, 0.1)">
                <i class="iconfont-sys" style="color: #67c23a">&#xe7a5;</i>
              </div>
              <h4>风险评估</h4>
              <p>基于AI算法，精准评估健康风险等级</p>
            </div>
            <div class="feature-item">
              <div class="feature-icon" style="background: rgba(230, 162, 60, 0.1)">
                <i class="iconfont-sys" style="color: #e6a23c">&#xe667;</i>
              </div>
              <h4>影像分析</h4>
              <p>智能识别医学影像，辅助疾病诊断</p>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 主要功能 -->
      <el-card class="doc-section" shadow="hover">
        <template #header>
          <div class="section-header">
            <i class="iconfont-sys">&#xe7b9;</i>
            <span>主要功能</span>
          </div>
        </template>
        <div class="section-content">
          <el-collapse v-model="activeFunctions" accordion>
            <el-collapse-item name="1">
              <template #title>
                <div class="collapse-title">
                  <i class="iconfont-sys">&#xe788;</i>
                  <span>健康问卷</span>
                </div>
              </template>
              <div class="collapse-content">
                <p><strong>功能说明：</strong></p>
                <p>通过填写健康问卷，系统会收集您的基本信息、生活习惯、病史等重要数据。</p>
                <p><strong>使用步骤：</strong></p>
                <ol>
                  <li>点击左侧菜单"健康问卷"进入问卷页面</li>
                  <li>按照步骤依次填写：基本信息 → 生活方式 → 病史信息 → 症状描述</li>
                  <li>确认信息无误后提交问卷</li>
                  <li>系统自动生成评估报告</li>
                </ol>
                <p><strong>注意事项：</strong></p>
                <ul>
                  <li>请如实填写所有信息，以确保评估结果准确</li>
                  <li>带 * 号的为必填项</li>
                  <li>可以随时保存草稿，稍后继续填写</li>
                </ul>
              </div>
            </el-collapse-item>

            <el-collapse-item name="2">
              <template #title>
                <div class="collapse-title">
                  <i class="iconfont-sys">&#xe7a5;</i>
                  <span>风险评估</span>
                </div>
              </template>
              <div class="collapse-content">
                <p><strong>功能说明：</strong></p>
                <p>系统基于您提交的问卷数据，运用AI算法进行综合分析，评估各类健康风险。</p>
                <p><strong>评估等级：</strong></p>
                <ul>
                  <li><el-tag type="success" size="small">低风险</el-tag> 健康状况良好，继续保持</li>
                  <li><el-tag type="warning" size="small">中风险</el-tag> 需要注意健康管理，建议定期检查</li>
                  <li><el-tag type="danger" size="small">高风险</el-tag> 建议尽快就医进行详细检查</li>
                </ul>
                <p><strong>查看报告：</strong></p>
                <ol>
                  <li>在"筛查历史"或"风险评估"菜单中查看所有评估记录</li>
                  <li>点击"查看详情"可查看完整评估报告</li>
                  <li>支持下载或打印报告</li>
                  <li>可与历史记录进行对比分析</li>
                </ol>
              </div>
            </el-collapse-item>

            <el-collapse-item name="3">
              <template #title>
                <div class="collapse-title">
                  <i class="iconfont-sys">&#xe667;</i>
                  <span>医学影像上传与分析</span>
                </div>
              </template>
              <div class="collapse-content">
                <p><strong>功能说明：</strong></p>
                <p>上传医学影像（如B超、CT等），系统使用深度学习模型进行智能分析。</p>
                <p><strong>支持的影像类型：</strong></p>
                <ul>
                  <li>乳腺超声影像（.png, .jpg, .jpeg格式）</li>
                  <li>其他医学影像（持续更新中）</li>
                </ul>
                <p><strong>使用步骤：</strong></p>
                <ol>
                  <li>进入"影像上传"页面</li>
                  <li>选择影像类型</li>
                  <li>上传清晰的影像文件</li>
                  <li>等待AI分析（通常需要几秒钟）</li>
                  <li>查看分析结果和可视化热力图</li>
                </ol>
                <p><strong>注意事项：</strong></p>
                <ul>
                  <li>请确保影像清晰，文件大小不超过10MB</li>
                  <li>AI分析结果仅供参考，不能替代医生诊断</li>
                  <li>建议结合专业医生意见进行判断</li>
                </ul>
              </div>
            </el-collapse-item>

            <el-collapse-item name="4">
              <template #title>
                <div class="collapse-title">
                  <i class="iconfont-sys">&#xe7b5;</i>
                  <span>筛查历史</span>
                </div>
              </template>
              <div class="collapse-content">
                <p><strong>功能说明：</strong></p>
                <p>查看您的所有历史筛查记录，包括问卷、评估和影像分析。</p>
                <p><strong>主要功能：</strong></p>
                <ul>
                  <li>查看历史记录列表</li>
                  <li>对比不同时期的健康状况</li>
                  <li>下载历史报告</li>
                  <li>导出数据用于医疗咨询</li>
                </ul>
              </div>
            </el-collapse-item>

            <el-collapse-item name="5" v-if="isDoctor || isAdmin">
              <template #title>
                <div class="collapse-title">
                  <i class="iconfont-sys">&#xe734;</i>
                  <span>医生工作台（医生专用）</span>
                </div>
              </template>
              <div class="collapse-content">
                <p><strong>功能说明：</strong></p>
                <p>医生专用工作台，用于查看和管理患者的筛查数据。</p>
                <p><strong>主要功能：</strong></p>
                <ul>
                  <li>查看患者筛查记录</li>
                  <li>查看评估报告详情</li>
                  <li>查看影像分析结果</li>
                  <li>提供专业诊疗建议</li>
                </ul>
              </div>
            </el-collapse-item>

            <el-collapse-item name="6" v-if="isAdmin">
              <template #title>
                <div class="collapse-title">
                  <i class="iconfont-sys">&#xe7b9;</i>
                  <span>系统管理（管理员专用）</span>
                </div>
              </template>
              <div class="collapse-content">
                <p><strong>功能说明：</strong></p>
                <p>管理员可以管理系统用户、查看统计数据等。</p>
                <p><strong>主要功能：</strong></p>
                <ul>
                  <li>用户管理：创建、编辑、删除用户</li>
                  <li>角色管理：分配用户角色权限</li>
                  <li>筛查记录管理：查看所有用户的筛查记录</li>
                  <li>系统统计：查看系统使用情况和数据统计</li>
                </ul>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
      </el-card>

      <!-- 使用流程 -->
      <el-card class="doc-section" shadow="hover">
        <template #header>
          <div class="section-header">
            <i class="iconfont-sys">&#xe753;</i>
            <span>使用流程</span>
          </div>
        </template>
        <div class="section-content">
          <div class="workflow">
            <div class="workflow-step">
              <div class="step-number">1</div>
              <div class="step-content">
                <h4>注册登录</h4>
                <p>使用邮箱注册账号并登录系统</p>
              </div>
            </div>
            <div class="workflow-arrow">
              <i class="iconfont-sys">&#xe621;</i>
            </div>
            <div class="workflow-step">
              <div class="step-number">2</div>
              <div class="step-content">
                <h4>填写问卷</h4>
                <p>完成健康问卷调查</p>
              </div>
            </div>
            <div class="workflow-arrow">
              <i class="iconfont-sys">&#xe621;</i>
            </div>
            <div class="workflow-step">
              <div class="step-number">3</div>
              <div class="step-content">
                <h4>查看评估</h4>
                <p>获取AI智能风险评估报告</p>
              </div>
            </div>
            <div class="workflow-arrow">
              <i class="iconfont-sys">&#xe621;</i>
            </div>
            <div class="workflow-step">
              <div class="step-number">4</div>
              <div class="step-content">
                <h4>上传影像</h4>
                <p>（可选）上传医学影像进行分析</p>
              </div>
            </div>
            <div class="workflow-arrow">
              <i class="iconfont-sys">&#xe621;</i>
            </div>
            <div class="workflow-step">
              <div class="step-number">5</div>
              <div class="step-content">
                <h4>健康管理</h4>
                <p>定期查看历史记录，跟踪健康状况</p>
              </div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 常见问题 -->
      <el-card class="doc-section" shadow="hover">
        <template #header>
          <div class="section-header">
            <i class="iconfont-sys">&#xe86e;</i>
            <span>常见问题</span>
          </div>
        </template>
        <div class="section-content">
          <el-collapse v-model="activeFAQ" accordion>
            <el-collapse-item name="1">
              <template #title>
                <strong>Q: 评估结果准确吗？</strong>
              </template>
              <div class="faq-answer">
                <p>
                  A: 系统采用经过大量数据训练的AI模型，评估结果具有一定的参考价值。
                  但请注意，任何AI评估都不能完全替代专业医生的诊断。
                  建议您将评估结果作为参考，如有异常请及时就医。
                </p>
              </div>
            </el-collapse-item>

            <el-collapse-item name="2">
              <template #title>
                <strong>Q: 我的数据安全吗？</strong>
              </template>
              <div class="faq-answer">
                <p>
                  A: 系统采用严格的数据加密和权限管理机制，您的个人健康数据完全保密。
                  我们遵守相关法律法规，绝不会泄露或出售用户数据。
                </p>
              </div>
            </el-collapse-item>

            <el-collapse-item name="3">
              <template #title>
                <strong>Q: 可以修改已提交的问卷吗？</strong>
              </template>
              <div class="faq-answer">
                <p>
                  A: 已提交的问卷无法直接修改，但您可以重新填写新的问卷。
                  系统会保存所有历史记录，方便您对比不同时期的健康状况。
                </p>
              </div>
            </el-collapse-item>

            <el-collapse-item name="4">
              <template #title>
                <strong>Q: 支持哪些医学影像格式？</strong>
              </template>
              <div class="faq-answer">
                <p>
                  A: 目前系统支持常见的图像格式（PNG、JPG、JPEG）。
                  建议上传清晰度高、文件大小适中（小于10MB）的影像文件，以获得最佳分析效果。
                </p>
              </div>
            </el-collapse-item>

            <el-collapse-item name="5">
              <template #title>
                <strong>Q: 多久应该进行一次健康筛查？</strong>
              </template>
              <div class="faq-answer">
                <p>
                  A: 建议根据您的年龄、健康状况和风险等级来决定：
                </p>
                <ul>
                  <li>低风险人群：每年1-2次</li>
                  <li>中风险人群：每半年一次</li>
                  <li>高风险人群：每3个月一次，并及时就医</li>
                </ul>
                <p>具体频率请咨询专业医生。</p>
              </div>
            </el-collapse-item>

            <el-collapse-item name="6">
              <template #title>
                <strong>Q: 如何联系技术支持？</strong>
              </template>
              <div class="faq-answer">
                <p>
                  A: 如遇到技术问题或有任何疑问，您可以：
                </p>
                <ul>
                  <li>发送邮件至：3338170081@qq.com</li>
                  <li>在系统中留言反馈</li>
                  <li>联系您的医生或系统管理员</li>
                </ul>
              </div>
            </el-collapse-item>
          </el-collapse>
        </div>
      </el-card>

      <!-- 快速链接 -->
      <el-card class="doc-section quick-links" shadow="hover">
        <template #header>
          <div class="section-header">
            <i class="iconfont-sys">&#xe753;</i>
            <span>快速链接</span>
          </div>
        </template>
        <div class="section-content">
          <div class="link-grid">
            <div class="link-item" @click="goToPage('/questionnaire')">
              <i class="iconfont-sys">&#xe788;</i>
              <span>开始健康问卷</span>
            </div>
            <div class="link-item" @click="goToPage('/risk')">
              <i class="iconfont-sys">&#xe7a5;</i>
              <span>查看风险评估</span>
            </div>
            <div class="link-item" @click="goToPage('/medical-image/upload')">
              <i class="iconfont-sys">&#xe621;</i>
              <span>上传医学影像</span>
            </div>
            <div class="link-item" @click="goToPage('/history')">
              <i class="iconfont-sys">&#xe7b5;</i>
              <span>筛查历史记录</span>
            </div>
            <div class="link-item" @click="goToPage('/system/user-center')">
              <i class="iconfont-sys">&#xe734;</i>
              <span>个人中心</span>
            </div>
            <div class="link-item" @click="goToPage('/')">
              <i class="iconfont-sys">&#xe721;</i>
              <span>返回首页</span>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/modules/user'

defineOptions({ name: 'UserDocs' })

const router = useRouter()
const userStore = useUserStore()

// 当前展开的功能项
const activeFunctions = ref('1')
// 当前展开的FAQ项
const activeFAQ = ref('1')

// 获取用户角色
const userInfo = computed(() => userStore.getUserInfo)
const isDoctor = computed(() => userInfo.value.roles?.includes('doctor'))
const isAdmin = computed(() => userInfo.value.roles?.includes('admin'))

/**
 * @brief 跳转到指定页面
 * @param {string} path - 目标路径
 */
const goToPage = (path: string) => {
  router.push(path)
}
</script>

<style scoped lang="scss">
.user-docs-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;

  .page-header {
    margin-bottom: 30px;
    padding: 40px;
    background: linear-gradient(135deg, #e8f4f8 0%, #f5f7fa 100%);
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    border: 1px solid var(--el-border-color-lighter);

    .header-content {
      display: flex;
      align-items: center;
      gap: 24px;

      i {
        font-size: 64px;
        color: var(--el-color-primary);
        opacity: 0.9;
      }

      .header-text {
        h1 {
          margin: 0 0 8px 0;
          font-size: 32px;
          font-weight: 600;
          color: #303133;
        }

        p {
          margin: 0;
          font-size: 16px;
          color: #606266;
        }
      }
    }
  }

  .docs-content {
    .doc-section {
      margin-bottom: 24px;

      &:last-child {
        margin-bottom: 0;
      }

      .section-header {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 18px;
        font-weight: 600;
        color: #303133;

        i {
          font-size: 20px;
          color: var(--el-color-primary);
        }
      }

      .section-content {
        .intro-text {
          font-size: 15px;
          line-height: 1.8;
          color: #606266;
          margin-bottom: 24px;
        }

        .feature-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
          gap: 20px;

          .feature-item {
            padding: 24px;
            background: var(--el-fill-color-light);
            border-radius: 12px;
            transition: all 0.3s;

            &:hover {
              transform: translateY(-4px);
              box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
            }

            .feature-icon {
              width: 56px;
              height: 56px;
              border-radius: 12px;
              display: flex;
              align-items: center;
              justify-content: center;
              margin-bottom: 16px;

              i {
                font-size: 28px;
              }
            }

            h4 {
              margin: 0 0 8px 0;
              font-size: 16px;
              font-weight: 600;
              color: #303133;
            }

            p {
              margin: 0;
              font-size: 14px;
              color: #606266;
              line-height: 1.6;
            }
          }
        }

        .collapse-title {
          display: flex;
          align-items: center;
          gap: 10px;
          font-size: 15px;
          font-weight: 500;

          i {
            font-size: 18px;
            color: var(--el-color-primary);
          }
        }

        .collapse-content {
          padding: 16px;
          font-size: 14px;
          line-height: 1.8;
          color: #606266;

          p {
            margin: 8px 0;
          }

          strong {
            color: #303133;
          }

          ol, ul {
            margin: 8px 0;
            padding-left: 24px;

            li {
              margin: 6px 0;
            }
          }
        }

        .faq-answer {
          padding: 16px;
          background: var(--el-fill-color-lighter);
          border-radius: 8px;
          font-size: 14px;
          line-height: 1.8;
          color: #606266;

          p {
            margin: 8px 0;
          }

          ul {
            margin: 8px 0;
            padding-left: 24px;

            li {
              margin: 6px 0;
            }
          }
        }

        .workflow {
          display: flex;
          align-items: center;
          justify-content: space-between;
          flex-wrap: wrap;
          gap: 16px;
          padding: 20px;

          .workflow-step {
            display: flex;
            flex-direction: column;
            align-items: center;
            flex: 1;
            min-width: 150px;

            .step-number {
              width: 48px;
              height: 48px;
              line-height: 48px;
              text-align: center;
              font-size: 20px;
              font-weight: 600;
              color: white;
              background: var(--el-color-primary);
              border-radius: 50%;
              margin-bottom: 12px;
              box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
            }

            .step-content {
              text-align: center;

              h4 {
                margin: 0 0 6px 0;
                font-size: 15px;
                font-weight: 600;
                color: #303133;
              }

              p {
                margin: 0;
                font-size: 13px;
                color: #909399;
              }
            }
          }

          .workflow-arrow {
            color: #dcdfe6;
            font-size: 24px;
            flex-shrink: 0;

            @media (max-width: 768px) {
              display: none;
            }
          }
        }

        .link-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 16px;

          .link-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 20px;
            background: var(--el-fill-color-light);
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s;

            i {
              font-size: 24px;
              color: var(--el-color-primary);
            }

            span {
              font-size: 14px;
              font-weight: 500;
              color: #606266;
            }

            &:hover {
              background: var(--el-color-primary);
              transform: translateY(-2px);
              box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);

              i, span {
                color: white;
              }
            }
          }
        }
      }
    }

    .quick-links {
      border: 1px solid var(--el-border-color-lighter);
      
      :deep(.el-card__header) {
        background: var(--el-fill-color-light);
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .user-docs-container {
    padding: 12px;

    .page-header {
      padding: 24px;

      .header-content {
        i {
          font-size: 48px;
        }

        .header-text h1 {
          font-size: 24px;
        }
      }
    }

    .docs-content {
      .doc-section .section-content {
        .feature-grid {
          grid-template-columns: 1fr;
        }

        .link-grid {
          grid-template-columns: 1fr;
        }

        .workflow {
          flex-direction: column;
        }
      }
    }
  }
}
</style>

