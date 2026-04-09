<template>
  <div class="login register">
    <LoginLeftView></LoginLeftView>
    <div class="right-wrap">
      <div class="header">
        <ArtLogo class="icon" />
        <h1>{{ systemName }}</h1>
      </div>
      <div class="login-wrap">
        <div class="form">
          <h3 class="title">{{ $t('register.title') }}</h3>
          <p class="sub-title">{{ $t('register.subTitle') }}</p>
          <ElForm ref="formRef" :model="formData" :rules="rules" label-position="top">
            <ElFormItem prop="username">
              <ElInput
                v-model.trim="formData.username"
                :placeholder="$t('register.placeholder[0]')"
              />
            </ElFormItem>

            <ElFormItem prop="email">
              <ElInput
                v-model.trim="formData.email"
                :placeholder="te('register.email') ? t('register.email') : '请输入邮箱'"
              />
            </ElFormItem>

            <ElFormItem prop="phone">
              <ElInput
                v-model.trim="formData.phone"
                :placeholder="te('register.phone') ? t('register.phone') : '请输入手机号'"
              />
            </ElFormItem>

            <ElFormItem prop="code">
              <div style="display: flex; gap: 8px; width: 100%">
                <ElInput
                  v-model.trim="formData.code"
                  :placeholder="te('register.code') ? t('register.code') : '请输入验证码'"
                />
                <ElButton :loading="sendLoading" @click="sendCode" type="primary">
                  {{ te('register.sendCode') ? t('register.sendCode') : '发送验证码' }}
                </ElButton>
              </div>
            </ElFormItem>

            <ElFormItem prop="password">
              <ElInput
                v-model.trim="formData.password"
                :placeholder="$t('register.placeholder[1]')"
                type="password"
                autocomplete="off"
                show-password
              />
            </ElFormItem>

            <ElFormItem prop="confirmPassword">
              <ElInput
                v-model.trim="formData.confirmPassword"
                :placeholder="$t('register.placeholder[2]')"
                type="password"
                autocomplete="off"
                @keyup.enter="register"
                show-password
              />
            </ElFormItem>

            <ElFormItem prop="agreement">
              <ElCheckbox v-model="formData.agreement">
                {{ $t('register.agreeText') }}
                <router-link
                  style="color: var(--main-color); text-decoration: none"
                  to="/privacy-policy"
                  >{{ $t('register.privacyPolicy') }}</router-link
                >
              </ElCheckbox>
            </ElFormItem>

            <div style="margin-top: 15px">
              <ElButton
                class="register-btn"
                type="primary"
                @click="register"
                :loading="loading"
                v-ripple
              >
                {{ $t('register.submitBtnText') }}
              </ElButton>
            </div>

            <div class="footer">
              <p>
                {{ $t('register.hasAccount') }}
                <router-link :to="{ name: 'Login' }">{{ $t('register.toLogin') }}</router-link>
              </p>
            </div>
          </ElForm>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import AppConfig from '@/config'
  import { useI18n } from 'vue-i18n'
  import type { FormInstance, FormRules } from 'element-plus'
  import { fetchRegister, fetchSendCode } from '@/api/auth'

  defineOptions({ name: 'Register' })

  interface RegisterForm {
    username: string
    email: string
    phone: string
    code: string
    password: string
    confirmPassword: string
    agreement: boolean
  }

  const USERNAME_MIN_LENGTH = 3
  const USERNAME_MAX_LENGTH = 20
  const PASSWORD_MIN_LENGTH = 8
  const REDIRECT_DELAY = 1000

  const { t, te } = useI18n()
  const router = useRouter()
  const formRef = ref<FormInstance>()

  const systemName = AppConfig.systemInfo.name
  const loading = ref(false)

  const formData = reactive<RegisterForm>({
    username: '',
    email: '',
    phone: '',
    code: '',
    password: '',
    confirmPassword: '',
    agreement: false
  })

  /**
   * 验证密码
   * 当密码输入后，如果确认密码已填写，则触发确认密码的验证
   */
  const validatePassword = (_rule: any, value: string, callback: (error?: Error) => void) => {
    if (!value) {
      callback(new Error(t('register.placeholder[1]')))
      return
    }

    if (formData.confirmPassword) {
      formRef.value?.validateField('confirmPassword')
    }

    callback()
  }

  /**
   * 验证确认密码
   * 检查确认密码是否与密码一致
   */
  const validateConfirmPassword = (
    _rule: any,
    value: string,
    callback: (error?: Error) => void
  ) => {
    if (!value) {
      callback(new Error(t('register.rule[0]')))
      return
    }

    if (value !== formData.password) {
      callback(new Error(t('register.rule[1]')))
      return
    }

    callback()
  }

  /**
   * 验证用户协议
   * 确保用户已勾选同意协议
   */
  const validateAgreement = (_rule: any, value: boolean, callback: (error?: Error) => void) => {
    if (!value) {
      callback(new Error(t('register.rule[4]')))
      return
    }
    callback()
  }

  const rules = reactive<FormRules<RegisterForm>>({
    username: [
      { required: true, message: t('register.placeholder[0]'), trigger: 'blur' },
      {
        min: USERNAME_MIN_LENGTH,
        max: USERNAME_MAX_LENGTH,
        message: t('register.rule[2]'),
        trigger: 'blur'
      }
    ],
    email: [
      {
        required: true,
        message: te('register.emailRequired') ? t('register.emailRequired') : '请输入邮箱',
        trigger: 'blur'
      },
      {
        type: 'email',
        message: te('register.emailInvalid') ? t('register.emailInvalid') : '邮箱格式不正确',
        trigger: 'blur'
      }
    ],
    phone: [
      {
        required: true,
        message: te('register.phoneRequired') ? t('register.phoneRequired') : '请输入手机号',
        trigger: 'blur'
      }
    ],
    code: [
      {
        required: true,
        message: te('register.codeRequired') ? t('register.codeRequired') : '请输入验证码',
        trigger: 'blur'
      }
    ],
    password: [
      { required: true, validator: validatePassword, trigger: 'blur' },
      { min: PASSWORD_MIN_LENGTH, message: t('register.rule[3]'), trigger: 'blur' }
    ],
    confirmPassword: [{ required: true, validator: validateConfirmPassword, trigger: 'blur' }],
    agreement: [{ validator: validateAgreement, trigger: 'change' }]
  })

  /**
   * 注册用户
   * 验证表单后提交注册请求
   */
  const sendLoading = ref(false)

  const sendCode = async () => {
    if (!formData.email) {
      ElMessage.warning(te('register.emailRequired') ? t('register.emailRequired') : '请先填写邮箱')
      return
    }
    try {
      sendLoading.value = true
      console.log({ email: formData.email })
      await fetchSendCode({ email: formData.email })
      console.log({ email: formData.email })
      ElMessage.success(te('register.codeSent') ? t('register.codeSent') : '验证码已发送')
    } catch (e) {
      console.error('[Register] sendCode error:', e)
    } finally {
      sendLoading.value = false
    }
  }

  const register = async () => {
    if (!formRef.value) return

    try {
      await formRef.value.validate()
      loading.value = true
      console.log({
        email: formData.email,
        phone: formData.phone,
        code: formData.code,
        password: formData.password,
        nickname: formData.username
      })

      const res = await fetchRegister({
        email: formData.email,
        phone: formData.phone,
        code: formData.code,
        password: formData.password,
        nickname: formData.username
      })
      if (res.code === 200) {
        ElMessage.success(te('register.success') ? t('register.success') : '注册成功')
      } else {
        ElMessage.error(res.message)
      }

      loading.value = false

      toLogin()
    } catch (error) {
      console.error('表单验证失败:', error)
      loading.value = false
    }
  }

  /**
   * 跳转到登录页面
   */
  const toLogin = () => {
    setTimeout(() => {
      router.push({ name: 'Login' })
    }, REDIRECT_DELAY)
  }
</script>

<style lang="scss" scoped>
  @use '../login/index' as login;
  @use './index' as register;
</style>
