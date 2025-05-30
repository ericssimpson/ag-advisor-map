import axios from '@/http-common'
import type { SelectedProductParams } from '@/shared'

/*
 * Retrieves all available datasets
 */
export async function getAvailableProducts() {
  const response = await axios.get('/products', {
    params: { '18n': 'en' },
  })

  const data = await response.data
  return data
}

export async function getDatasetEntries(
  selectedProduct: SelectedProductParams,
) {
  const { product_id /*date, ...params*/ } = selectedProduct

  const url = `/datasets/?product_id=${product_id}&limit=10000`

  const response = await axios.get(url)

  // TODO : Why isn't this passing paramters?
  // const response = await axios.get("/datasets/", {
  //     limit: 10000,
  //     product_id: product_id
  // })

  const data = await response.data

  return data
}
