import { onBeforeUnmount, onMounted, type Ref } from 'vue'
import { BarChart, LineChart } from 'echarts/charts'
import { GridComponent, LegendComponent, TooltipComponent } from 'echarts/components'
import { init, use } from 'echarts/core'
import type { ECharts, EChartsOption } from 'echarts'
import { CanvasRenderer } from 'echarts/renderers'

use([BarChart, CanvasRenderer, GridComponent, LegendComponent, LineChart, TooltipComponent])

export const useECharts = (elementRef: Ref<HTMLElement | null>, getOption: () => EChartsOption) => {
  let chart: ECharts | null = null
  let resizeObserver: ResizeObserver | null = null

  const renderChart = (): void => {
    chart?.setOption(getOption(), true)
  }

  onMounted(() => {
    const element = elementRef.value
    if (!element) {
      return
    }

    chart = init(element, undefined, { renderer: 'canvas' })
    renderChart()
    resizeObserver = new ResizeObserver(() => chart?.resize())
    resizeObserver.observe(element)
  })

  onBeforeUnmount(() => {
    resizeObserver?.disconnect()
    resizeObserver = null
    chart?.dispose()
    chart = null
  })

  return { renderChart }
}
