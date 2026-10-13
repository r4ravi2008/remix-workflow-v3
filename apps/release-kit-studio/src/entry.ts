import { Runtime } from 'foldkit'

import { Message, Model, init, update } from './main'
import { view } from './view'
import './styles.css'

const application = Runtime.makeApplication({
  Model,
  init,
  update,
  view,
  container: document.getElementById('root'),
  ...(import.meta.env.DEV &&
  import.meta.env.VITE_ENABLE_FOLDKIT_DEVTOOLS === 'true'
    ? { devTools: { Message } }
    : {}),
})
Runtime.run(application)
