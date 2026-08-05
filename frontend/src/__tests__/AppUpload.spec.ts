import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import { NUpload } from 'naive-ui'

import AppUpload from '../components/AppUpload/index.vue'

const createFile = (name: string, size: number): File =>
  new File([new Uint8Array(size)], name, { type: 'application/octet-stream' })

const createUploadFile = (name: string, size: number) => ({
  id: name,
  name,
  status: 'pending' as const,
  percentage: 0,
  file: createFile(name, size),
  type: 'application/octet-stream',
  url: null,
  thumbnailUrl: null,
  batchId: null,
  fullPath: null,
})

describe('AppUpload', () => {
  it('supports controlled file lists and the default trigger', async () => {
    const wrapper = mount(AppUpload, {
      props: {
        fileList: [],
      },
    })
    const fileList = [createUploadFile('report.txt', 4)]
    const updateFileList = wrapper.findComponent(NUpload).props('onUpdate:fileList')

    expect(wrapper.get('.n-button').text()).toContain('选择文件')
    expect(typeof updateFileList).toBe('function')
    if (typeof updateFileList !== 'function') {
      wrapper.unmount()
      return
    }

    Reflect.apply(updateFileList, null, [fileList])
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('update:fileList')?.[0]?.[0]).toEqual(fileList)
    wrapper.unmount()
  })

  it('blocks oversized files and emits a typed validation error', async () => {
    const wrapper = mount(AppUpload, {
      props: {
        maxSize: 4,
      },
    })
    const beforeUpload = wrapper.findComponent(NUpload).props('onBeforeUpload')
    const file = createUploadFile('large.bin', 5)

    expect(typeof beforeUpload).toBe('function')
    if (typeof beforeUpload !== 'function') {
      wrapper.unmount()
      return
    }

    const allowed = await Reflect.apply(beforeUpload, null, [{ file, fileList: [file] }])

    expect(allowed).toBe(false)
    expect(wrapper.emitted('validation-error')?.[0]?.[0]).toEqual(
      expect.objectContaining({ reason: 'size', maxSize: 4, message: '文件大小不能超过 4 B' }),
    )
    wrapper.unmount()
  })

  it('supports dragger mode and removal guards', async () => {
    const wrapper = mount(AppUpload, {
      props: {
        dragger: true,
        beforeRemove: () => false,
      },
    })
    const file = createUploadFile('protected.txt', 1)
    const remove = wrapper.findComponent(NUpload).props('onRemove')

    expect(wrapper.find('.n-upload-dragger').exists()).toBe(true)
    expect(typeof remove).toBe('function')
    if (typeof remove !== 'function') {
      wrapper.unmount()
      return
    }

    const allowed = await Reflect.apply(remove, null, [{ file, fileList: [file], index: 0 }])

    expect(allowed).toBe(false)
    expect(wrapper.emitted('remove')).toBeUndefined()
    wrapper.unmount()
  })
})
