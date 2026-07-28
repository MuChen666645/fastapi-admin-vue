import { beforeEach, describe, expect, it, vi } from 'vitest'

import { flushPromises, mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { defineComponent } from 'vue'
import { createMemoryHistory, createRouter } from 'vue-router'

const authApi = vi.hoisted(() => ({
  fetchCaptcha: vi.fn(),
}))

vi.mock('../api/auth', () => authApi)

import LoginView from '../views/login/index.vue'
import { useAuthStore } from '../stores/auth'

const HomeView = defineComponent({
  template: '<div data-testid="home-page">Home page</div>',
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
    authApi.fetchCaptcha.mockResolvedValue({
      captcha_id: 'captcha-id',
      image: 'data:image/png;base64,captcha',
    })
  })

  it('does not navigate when required fields are empty', async () => {
    const router = createLoginRouter()

    await router.push('/login')
    await router.isReady()

    const wrapper = mount(LoginView, {
      global: {
        plugins: [router, createPinia()],
      },
    })

    await wrapper.get('button').trigger('click')
    await flushPromises()

    expect(router.currentRoute.value.name).toBe('login')

    wrapper.unmount()
  })

  it('navigates through the application route after a successful login', async () => {
    const router = createLoginRouter()
    const pinia = createPinia()
    await router.push({ name: 'login', query: { redirect: '/home' } })
    await router.isReady()

    const auth = useAuthStore(pinia)
    vi.spyOn(auth, 'signIn').mockResolvedValue(undefined)

    const wrapper = mount(LoginView, {
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

    const buttons = wrapper.findAll('button')
    const submitButton = buttons[buttons.length - 1]
    if (!submitButton) {
      throw new Error('登录按钮未渲染')
    }

    await submitButton.trigger('click')
    await flushPromises()

    expect(router.currentRoute.value.name).toBe('home')
    expect(auth.signIn).toHaveBeenCalledOnce()

    wrapper.unmount()
  })

  it('requests a new captcha when the refresh control is clicked', async () => {
    const router = createLoginRouter()

    await router.push('/login')
    await router.isReady()

    const wrapper = mount(LoginView, {
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
