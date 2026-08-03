import { beforeEach, describe, expect, it, vi } from 'vitest'

import { flushPromises, mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { defineComponent, nextTick } from 'vue'
import { createMemoryHistory, createRouter } from 'vue-router'
import { NNotificationProvider } from 'naive-ui'

const authApi = vi.hoisted(() => ({
  fetchCaptcha: vi.fn(),
}))

vi.mock('../api', () => authApi)

import LoginView from '../views/login/index.vue'
import { useAuthStore, usePreferencesStore } from '../stores'

const HomeView = defineComponent({
  template: '<div data-testid="home-page">Home page</div>',
})

const LoginTestHost = defineComponent({
  components: { LoginView, NNotificationProvider },
  template: '<NNotificationProvider><LoginView /></NNotificationProvider>',
})

const createLoginRouter = () =>
  createRouter({
    history: createMemoryHistory(),
    routes: [
      {
        path: '/login',
        name: 'login',
        component: LoginView,
      },
      {
        path: '/home',
        name: 'home',
        component: HomeView,
      },
      {
        path: '/',
        name: 'app',
        component: HomeView,
      },
    ],
  })

describe('LoginView', () => {
  beforeEach(() => {
    localStorage.clear()
    authApi.fetchCaptcha.mockResolvedValue({
      captcha_id: 'captcha-id',
      image: 'data:image/png;base64,captcha',
    })
  })

  it('does not navigate when required fields are empty', async () => {
    const router = createLoginRouter()

    await router.push('/login')
    await router.isReady()

    const wrapper = mount(LoginTestHost, {
      global: {
        plugins: [router, createPinia()],
      },
    })

    await wrapper.get('.login-submit').trigger('click')
    await flushPromises()

    expect(router.currentRoute.value.name).toBe('login')

    wrapper.unmount()
  })

  it('toggles dark mode on the whole login page', async () => {
    const router = createLoginRouter()

    await router.push('/login')
    await router.isReady()

    const wrapper = mount(LoginTestHost, {
      global: {
        plugins: [router, createPinia()],
      },
    })

    const loginPage = wrapper.get('.login-page')
    expect(loginPage.classes()).not.toContain('login-page--dark')

    await wrapper.get('.theme-toggle').trigger('click')
    expect(loginPage.classes()).toContain('login-page--dark')
    expect(localStorage.getItem('fastapi-admin:theme')).toBe('dark')

    await wrapper.get('.theme-toggle').trigger('click')
    expect(loginPage.classes()).not.toContain('login-page--dark')
    expect(localStorage.getItem('fastapi-admin:theme')).toBe('light')

    wrapper.unmount()
  })

  it('updates login labels and actions when the language changes', async () => {
    const router = createLoginRouter()
    const pinia = createPinia()
    const preferences = usePreferencesStore(pinia)

    await router.push('/login')
    await router.isReady()

    const wrapper = mount(LoginTestHost, {
      global: {
        plugins: [router, pinia],
      },
    })

    expect(wrapper.get('.login-submit').text()).toContain('登录')
    expect(wrapper.get('.theme-toggle').attributes('title')).toBe('切换暗色模式')
    expect(wrapper.get('.language-toggle').attributes('title')).toBe('切换到 English')

    preferences.language = 'en-US'
    await nextTick()

    expect(wrapper.get('.login-submit').text()).toContain('Sign in')
    expect(wrapper.get('.brand-title').text()).toContain('A ready-to-use administration system')
    expect(wrapper.get('.theme-toggle').attributes('title')).toBe('Switch to dark mode')
    expect(wrapper.get('.language-toggle').attributes('title')).toBe('Switch to Simplified Chinese')
    expect(wrapper.find('input[placeholder="Enter your username"]').exists()).toBe(true)

    wrapper.unmount()
  })

  it('navigates through the application route after a successful login', async () => {
    const router = createLoginRouter()
    const pinia = createPinia()
    await router.push({ name: 'login', query: { redirect: '/home' } })
    await router.isReady()

    const auth = useAuthStore(pinia)
    vi.spyOn(auth, 'signIn').mockResolvedValue(undefined)

    const wrapper = mount(LoginTestHost, {
      global: {
        plugins: [router, pinia],
      },
    })

    await flushPromises()
    const inputs = wrapper.findAll('input')
    const identifierInput = inputs.find(
      (input) => input.attributes('placeholder') === '请输入用户名',
    )
    const passwordInput = inputs.find((input) => input.attributes('type') === 'password')
    const captchaInput = inputs.find((input) => input.attributes('placeholder') === '请输入验证码')
    if (!identifierInput || !passwordInput || !captchaInput) {
      throw new Error('登录表单输入框未渲染')
    }

    await identifierInput.setValue('admin')
    await passwordInput.setValue('password')
    await captchaInput.setValue('1234')
    await wrapper.get('.remember-option input').setValue(true)

    await wrapper.get('.login-submit').trigger('click')
    await flushPromises()

    expect(router.currentRoute.value.name).toBe('home')
    expect(auth.signIn).toHaveBeenCalledOnce()
    expect(JSON.parse(localStorage.getItem('fastapi-admin:remembered-login') ?? '{}')).toEqual({
      identifier: 'admin',
      password: 'password',
    })

    wrapper.unmount()
  })

  it('requests a new captcha when the refresh control is clicked', async () => {
    const router = createLoginRouter()

    await router.push('/login')
    await router.isReady()

    const wrapper = mount(LoginTestHost, {
      global: {
        plugins: [router, createPinia()],
      },
    })

    await flushPromises()
    expect(authApi.fetchCaptcha).toHaveBeenCalledTimes(1)

    await wrapper.get('.captcha-image').trigger('click')
    await flushPromises()

    expect(authApi.fetchCaptcha).toHaveBeenCalledTimes(2)

    wrapper.unmount()
  })
})
