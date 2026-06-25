<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import api from './api/client.js'

/* ---------- estado ---------- */
const current = ref('hoy')
const capInput = ref('')
const clock = ref('')
const status = ref('Conectando…')
const statusErr = ref(false)

const tasks = ref([])
const objectives = ref([])
const trends = ref([])
const rhythmsOn = ref([])      // [{rhythm, day}]
const review = ref([])
const newTrend = ref('')
const miniInputs = reactive({})

const VIEWS = [
  { id:'hoy', label:'Hoy' },
  { id:'tareas', label:'Sistema de tareas' },
  { id:'okrs', label:'Objetivos (OKR)' },
  { id:'estudio', label:'Plan de estudio' },
  { id:'crecimiento', label:'Crecimiento' },
  { id:'equilibrio', label:'Equilibrio' },
  { id:'semana', label:'Mi semana' },
  { id:'revision', label:'Revisión semanal' },
]

const LISTS = [
  { key:'inbox', name:'Inbox', color:'var(--gold)' },
  { key:'next', name:'Próximas acciones', color:'var(--clay)' },
  { key:'waiting', name:'En espera de', color:'var(--slate)' },
  { key:'meetings', name:'Compromisos de reunión', color:'var(--moss)' },
  { key:'portfolio', name:'Rol · Portafolio', color:'var(--plum)' },
  { key:'watch', name:'Vigilancia / Algún día', color:'var(--ink-soft)' },
]
const MOVE_TARGETS = {
  inbox:['next','waiting','meetings','portfolio','watch'],
  meetings:['next','waiting'], next:['waiting'], watch:['next'],
}

const REVIEW_STEPS = [
  'Vaciar el Inbox a cero',
  'Revisar «En espera de» — ¿a quién pingar esta semana?',
  'Cada proyecto: ¿tiene una próxima acción definida?',
  'Revisar el calendario entrante — ¿qué reuniones requieren preparación?',
  'Mirar los OKR — ¿sigo alineado o me desvié a lo reactivo?',
  'Revisar Equilibrio — ¿honré familia, cuerpo y mente esta semana?',
]

const RHYTHMS = [
  { key:'familia', name:'Tiempo en familia', color:'var(--plum)', why:'Con tu esposa e hija de 3 meses — lo primero, no lo que sobra', icon:'♥' },
  { key:'gym', name:'Gimnasio', color:'var(--clay)', why:'Energía física que sostiene todo lo demás', icon:'⚡' },
  { key:'medita', name:'Meditación', color:'var(--moss)', why:'Mente equilibrada — 10 min cuentan', icon:'◯' },
  { key:'lectura', name:'Lectura', color:'var(--slate)', why:'Alimenta criterio y profundidad', icon:'❧' },
  { key:'mente', name:'Mente / espíritu', color:'var(--gold)', why:'Ajedrez, escritura, algo que fortalezca mente y espíritu', icon:'✶' },
  { key:'ingles', name:'Inglés', color:'var(--ink-soft)', why:'Hábito de fondo, 20–30 min', icon:'A' },
]

const TECH_SOURCES = [
  { cat:'Cloud / multi-nube', items:["AWS What's New + AWS Architecture Blog","Google Cloud Blog · Azure Updates","InfoQ — Cloud & Architecture"] },
  { cat:'Nutanix / virtualización', items:["Nutanix .NEXT Blog & Nutanix University","The Forecast (Nutanix)","Notas de migración VMware→AHV"] },
  { cat:'Kubernetes / cloud-native', items:["CNCF Blog + KubeWeekly","Kubernetes blog oficial","killer.sh & CKA changelog"] },
  { cat:'Redes / Juniper Apstra', items:["Juniper Apstra release notes","Packet Pushers (podcast)","NANOG / IETF (fundamentos)"] },
  { cat:'Negocio & estrategia TI', items:["Gartner / Forrester (resúmenes)","a16z + Stratechery","Análisis sector telco LatAm"] },
]
const MENTAL_PRACTICES = [
  { name:'Lectura profunda', desc:'Un libro técnico o de pensamiento en curso, no solo artículos. La profundidad construye criterio de arquitecto.', icon:'❧' },
  { name:'Ajedrez / lógica', desc:'Entrena cálculo, anticipación y reconocimiento de patrones — los mismos músculos del diseño de soluciones.', icon:'♞' },
  { name:'Escritura / síntesis', desc:'Escribir lo aprendido fuerza claridad. Si no lo puedes explicar, no lo entendiste.', icon:'✎' },
  { name:'Aprendizaje deliberado', desc:'Algo fuera de tu zona: un paper, un dominio nuevo. La mente fuerte se incomoda a propósito.', icon:'✶' },
  { name:'Enfoque sin distracción', desc:'Bloques de trabajo profundo sin teléfono. La atención sostenida es la habilidad más rara hoy.', icon:'◎' },
]

const WEEK = [
  { d:'Lunes', blocks:[['Trabajo profundo','Entregables Internexa'],['Estudio','AWS SAA · 90 min'],['Familia','Tarde/noche']] },
  { d:'Martes', blocks:[['Trabajo profundo','Diseño de solución'],['Gimnasio',''],['Inglés','20–30 min'],['Lectura','Noche']] },
  { d:'Miércoles', blocks:[['Vigilancia tech','60–90 min'],['Estudio','AWS SAA · 90 min'],['Familia','Tarde/noche']] },
  { d:'Jueves', blocks:[['Trabajo profundo','Portafolio / negocio'],['Gimnasio',''],['Meditación','10 min'],['Inglés','']] },
  { d:'Viernes', blocks:[['Estudio','AWS SAA · 90 min'],['Revisión semanal','45–60 min'],['Familia','Noche']] },
  { d:'Sáb/Dom', blocks:[['Familia','Prioridad'],['Mente/espíritu','Ajedrez, lectura'],['Simulacro','Si aplica'],['Descanso','']] },
]

/* ---------- helpers de fecha ---------- */
const todayKey = new Date().toISOString().slice(0,10)
function last7(){ const a=[]; for(let i=6;i>=0;i--){ const d=new Date(); d.setDate(d.getDate()-i); a.push(d) } return a }
const DL = ['D','L','M','M','J','V','S']

/* ---------- reloj ---------- */
function tick(){
  const d=new Date()
  const dias=['domingo','lunes','martes','miércoles','jueves','viernes','sábado']
  const mes=['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic']
  clock.value=`<b>${d.toLocaleTimeString('es-CO',{hour:'2-digit',minute:'2-digit'})}</b>${dias[d.getDay()]}, ${d.getDate()} ${mes[d.getMonth()]} ${d.getFullYear()}`
}

/* ---------- carga ---------- */
async function loadAll(){
  try{
    const [t,o,tr,rh,rv] = await Promise.all([
      api.getTasks(), api.getObjectives(), api.getTrends(), api.getRhythms(), api.getReview()
    ])
    tasks.value = t.data
    objectives.value = o.data
    trends.value = tr.data
    rhythmsOn.value = rh.data
    review.value = rv.data.sort((a,b)=>a.index-b.index)
    status.value = 'Guardado en MySQL ✓'
    statusErr.value = false
  }catch(e){
    status.value = 'Sin conexión al backend — revisa que Django esté corriendo'
    statusErr.value = true
  }
}

/* ---------- tareas ---------- */
const tasksByList = computed(()=>{
  const m={}; LISTS.forEach(l=>m[l.key]=[])
  tasks.value.forEach(t=>{ if(m[t.list]) m[t.list].push(t) })
  return m
})
function activeCount(key){ return tasksByList.value[key].filter(t=>!t.done).length }

async function capture(){
  const v=capInput.value.trim(); if(!v) return
  capInput.value=''
  await api.addTask({ text:v, list:'inbox' })
  await loadAll()
}
async function addTo(key){
  const v=(miniInputs[key]||'').trim(); if(!v) return
  miniInputs[key]=''
  const payload={ text:v, list:key }
  if(key==='waiting') payload.meta=`esperando desde ${todayKey}`
  await api.addTask(payload)
  await loadAll()
}
async function toggleTask(id){ await api.toggleTask(id); await loadAll() }
async function delTask(id){ await api.deleteTask(id); await loadAll() }
async function moveTask(id,list){ await api.moveTask(id,list); await loadAll() }

/* ---------- OKR ---------- */
/* ---------- OKR ---------- */
async function setKr(krId,val){
  await api.setKrProgress(krId, val)
  const kr = objectives.value.flatMap(o=>o.krs).find(k=>k.id===krId)
  if(kr) kr.progress = Number(val)
}

// edición de objetivos
const editingObj = ref(null)
const objForm = reactive({ title:'', tag:'', color:'var(--moss)' })
const COLORS = [
  { label:'Musgo', value:'var(--moss)' },
  { label:'Arcilla', value:'var(--clay)' },
  { label:'Dorado', value:'var(--gold)' },
  { label:'Pizarra', value:'var(--slate)' },
  { label:'Ciruela', value:'var(--plum)' },
]
function startNewObj(){
  editingObj.value = 'new'
  objForm.title=''; objForm.tag=''; objForm.color='var(--moss)'
}
function startEditObj(o){
  editingObj.value = o.id
  objForm.title=o.title; objForm.tag=o.tag; objForm.color=o.color
}
function cancelObj(){ editingObj.value = null }
async function saveObj(){
  const title = objForm.title.trim()
  if(!title) return
  const payload = { title, tag:objForm.tag.trim(), color:objForm.color }
  if(editingObj.value === 'new'){
    payload.order = objectives.value.length
    await api.addObjective(payload)
  } else {
    await api.updateObjective(editingObj.value, payload)
  }
  editingObj.value = null
  await loadAll()
}
async function removeObj(o){
  if(!confirm(`¿Eliminar el objetivo "${o.title}" y todos sus key results?`)) return
  await api.deleteObjective(o.id)
  await loadAll()
}

// key results
const krInputs = reactive({})
async function addKr(objId){
  const v = (krInputs[objId]||'').trim()
  if(!v) return
  krInputs[objId]=''
  const obj = objectives.value.find(o=>o.id===objId)
  await api.addKeyResult({ objective:objId, text:v, progress:0, order:obj?obj.krs.length:0 })
  await loadAll()
}
async function removeKr(krId){
  await api.deleteKeyResult(krId)
  await loadAll()
}

/* ---------- tendencias ---------- */
async function addTrend(){
  const v=newTrend.value.trim(); if(!v) return
  newTrend.value=''
  await api.addTrend({ text:v, source:`capturado ${todayKey}` })
  await loadAll()
}
async function toggleTrend(id){ await api.toggleTrend(id); await loadAll() }
async function delTrend(id){ await api.deleteTrend(id); await loadAll() }

/* ---------- ritmos ---------- */
function isOn(rhythm,day){ return rhythmsOn.value.some(r=>r.rhythm===rhythm && r.day===day) }
async function toggleDay(rhythm,day){ await api.toggleRhythm(rhythm,day); await loadAll() }

/* ---------- revisión ---------- */
async function toggleReview(id){ await api.toggleReview(id); await loadAll() }
async function resetReview(){ await api.resetReview(); await loadAll() }

/* ---------- vistas derivadas ---------- */
const top3 = computed(()=> tasksByList.value['next'].filter(t=>!t.done).slice(0,3))
const waitingActive = computed(()=> tasksByList.value['waiting'].filter(t=>!t.done))
const inboxCount = computed(()=> tasksByList.value['inbox'].filter(t=>!t.done).length)

function moveLabel(key){ return LISTS.find(l=>l.key===key).name.split(' ')[0] }

onMounted(()=>{ tick(); setInterval(tick,20000); loadAll() })
</script>

<template>
  <header>
    <div class="head-row">
      <div>
        <h1>Centro de Mando</h1>
        <div class="sub">Daniel · Arquitecto de Portafolio</div>
      </div>
      <div class="clock" v-html="clock"></div>
    </div>
    <div class="capture">
      <input v-model="capInput" @keydown.enter="capture"
        placeholder="Captura rápida — toda solicitud, compromiso o idea entra aquí…" />
      <button @click="capture">Capturar</button>
    </div>
    <div class="cap-hint">Tu cabeza es para tener ideas, no para guardarlas. Lo capturado cae al Inbox y se procesa después.</div>
    <div class="status" :class="{err:statusErr}">{{ status }}</div>
  </header>

  <nav>
    <button v-for="v in VIEWS" :key="v.id" :class="{active:current===v.id}" @click="current=v.id">{{ v.label }}</button>
  </nav>

  <main>
    <!-- HOY -->
    <div v-if="current==='hoy'" class="view">
      <h2 class="view-title">Hoy</h2>
      <div class="section-intro">Máximo 3 prioridades que sí o sí cierras hoy. Lo demás es secundario.</div>
      <div class="cols">
        <div class="card">
          <div class="card-head"><h3><span class="dot" style="background:var(--clay)"></span>Mis 3 prioridades</h3></div>
          <div class="card-body">
            <div v-if="top3.length" v-for="it in top3" :key="it.id" class="item">
              <div class="chk" @click="toggleTask(it.id)"></div><div class="txt">{{ it.text }}</div>
            </div>
            <div v-else class="empty">Define tus prioridades en Próximas acciones</div>
          </div>
        </div>
        <div class="card">
          <div class="card-head"><h3><span class="dot" style="background:var(--slate)"></span>Seguimientos pendientes</h3><span class="count" style="background:var(--slate)">{{ waitingActive.length }}</span></div>
          <div class="card-body">
            <div v-if="waitingActive.length" v-for="it in waitingActive" :key="it.id" class="item">
              <div class="txt">{{ it.text }}<span class="meta">{{ it.meta }}</span></div>
            </div>
            <div v-else class="empty">Nada en espera de otros</div>
          </div>
        </div>
        <div class="card">
          <div class="card-head"><h3><span class="dot" style="background:var(--gold)"></span>Inbox por procesar</h3><span class="count" style="background:var(--gold)">{{ inboxCount }}</span></div>
          <div class="card-body">
            <div v-if="inboxCount" class="empty" style="font-style:normal;color:var(--ink-soft)">
              Tienes {{ inboxCount }} ítem(s) sin procesar.<br>
              <span style="cursor:pointer;color:var(--clay);font-weight:600" @click="current='tareas'">Ir a procesarlos →</span>
            </div>
            <div v-else class="empty">Inbox a cero ✓</div>
          </div>
        </div>
      </div>
      <div class="principle" style="margin-top:18px"><b>Hábitos de hoy:</b> revisa que cada bloque de tu día (familia, trabajo profundo, gimnasio, lectura, meditación) tenga su lugar. Marca tus rachas en <b>Equilibrio</b>.</div>
    </div>

    <!-- SISTEMA DE TAREAS -->
    <div v-else-if="current==='tareas'" class="view">
      <h2 class="view-title">Sistema de tareas</h2>
      <div class="section-intro">Basado en GTD: todo se captura, se aclara y va a una lista. Lo que esperas de otros vive en <b>En espera de</b> para que ningún seguimiento se caiga.</div>
      <div class="principle"><b>Procesar el inbox:</b> por cada ítem pregúntate — ¿es accionable? ¿es mío o de alguien más? ¿es multi-paso (proyecto)? Luego muévelo a su lista con los botones <b>→</b>.</div>
      <div class="cols">
        <div v-for="cfg in LISTS" :key="cfg.key" class="card">
          <div class="card-head">
            <h3><span class="dot" :style="{background:cfg.color}"></span>{{ cfg.name }}</h3>
            <span class="count" :style="{background:cfg.color}">{{ activeCount(cfg.key) }}</span>
          </div>
          <div class="card-body">
            <div v-if="tasksByList[cfg.key].length" v-for="it in tasksByList[cfg.key]" :key="it.id" class="item" :class="{done:it.done}">
              <div class="chk" @click="toggleTask(it.id)">{{ it.done?'✓':'' }}</div>
              <div class="txt">
                {{ it.text }}<span v-if="it.meta" class="meta">{{ it.meta }}</span>
                <div style="margin-top:5px">
                  <span v-for="tk in (MOVE_TARGETS[cfg.key]||[])" :key="tk" class="move" @click="moveTask(it.id,tk)">→ {{ moveLabel(tk) }}</span>
                </div>
              </div>
              <div class="x" @click="delTask(it.id)">×</div>
            </div>
            <div v-else class="empty">Sin pendientes</div>
            <div class="mini-add">
              <input v-model="miniInputs[cfg.key]" @keydown.enter="addTo(cfg.key)" :placeholder="'Añadir a '+cfg.name.toLowerCase()+'…'" />
              <button @click="addTo(cfg.key)">+</button>
            </div>
          </div>
        </div>
      </div>
    </div>

<!-- OKR -->
    <div v-else-if="current==='okrs'" class="view">
      <h2 class="view-title">Objetivos del trimestre</h2>
      <div class="section-intro">3–4 objetivos con resultados medibles. Mueve cada barra según tu avance real. Esto le da el "hacia dónde voy" a las tareas del día.</div>

      <div v-if="editingObj" class="okr" style="border:1.5px dashed var(--moss)">
        <div class="subhead" style="margin-bottom:10px">{{ editingObj==='new' ? 'Nuevo objetivo' : 'Editar objetivo' }}</div>
        <input v-model="objForm.title" placeholder="Título del objetivo…" class="okr-input" @keydown.enter="saveObj" />
        <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:8px;align-items:center">
          <input v-model="objForm.tag" placeholder="Etiqueta (ej. Internexa)" class="okr-input" style="max-width:200px" />
          <select v-model="objForm.color" class="okr-input" style="max-width:150px">
            <option v-for="c in COLORS" :key="c.value" :value="c.value">{{ c.label }}</option>
          </select>
          <span class="okr-tag" :style="{background:objForm.color}">{{ objForm.tag || 'vista previa' }}</span>
        </div>
        <div style="margin-top:12px;display:flex;gap:8px">
          <button class="btn-primary" @click="saveObj">Guardar</button>
          <button class="btn-ghost" @click="cancelObj">Cancelar</button>
        </div>
      </div>

      <button v-if="!editingObj" class="btn-primary" style="margin-bottom:16px" @click="startNewObj">+ Nuevo objetivo</button>

      <div v-for="o in objectives" :key="o.id" class="okr">
        <div class="okr-obj">
          <span class="okr-tag" :style="{background:o.color}">{{ o.tag }}</span>
          <span style="flex:1">{{ o.title }}</span>
          <span class="okr-action" @click="startEditObj(o)" title="Editar">✎</span>
          <span class="okr-action danger" @click="removeObj(o)" title="Eliminar">🗑</span>
        </div>
        <div v-for="k in o.krs" :key="k.id" class="kr">
          <span style="flex:1.4">{{ k.text }}</span>
          <input type="range" min="0" max="100" :value="k.progress" @input="setKr(k.id,$event.target.value)" />
          <div class="bar"><div class="fill" :style="{width:k.progress+'%',background:o.color}"></div></div>
          <span class="pct">{{ k.progress }}%</span>
          <span class="okr-action danger" @click="removeKr(k.id)" title="Eliminar key result">×</span>
        </div>
        <div class="mini-add" style="margin-top:8px">
          <input v-model="krInputs[o.id]" @keydown.enter="addKr(o.id)" placeholder="Añadir key result…" />
          <button @click="addKr(o.id)">+</button>
        </div>
      </div>
    </div>
    <!-- ESTUDIO -->
    <div v-else-if="current==='estudio'" class="view">
      <h2 class="view-title">Plan de estudio</h2>
      <div class="section-intro">Secuenciar, no paralelizar. 1–2 certificaciones en foco intenso + inglés como hábito diario de fondo. El orden aprovecha tu trabajo real (K8s/AHV).</div>
      <div class="phase">
        <h3>AWS SAA-C03 <span class="when">Ahora → examen</span></h3>
        <p>Foco #1 absoluto por tener fecha cercana. Teoría por dominio + simulacros. No te presentes sin sacar ≥80% consistente en Tutorials Dojo.</p>
        <span class="pill focus">Foco intenso</span><span class="pill">Inglés diario de fondo</span><span class="pill">Últimas 2 sem: solo simulacros</span>
      </div>
      <div class="phase">
        <h3>CKA <span class="when">Post-SAA · 4–6 sem</span></h3>
        <p>Examen práctico en terminal real — manos en teclado desde el día uno. Sinérgico con tu trabajo en Kubernetes/AHV/NKP. Simulador killer.sh incluido con la inscripción.</p>
        <span class="pill focus">Foco intenso</span><span class="pill">killer.sh</span><span class="pill">Velocidad bajo cronómetro</span>
      </div>
      <div class="phase">
        <h3>Nutanix NCP-MCI <span class="when">Siguiente bloque</span></h3>
        <p>Se solapa con tu migración activa a AHV/Prism Central — ya lo "estudias" trabajando. Aprovecha Nutanix University (gratuito).</p>
        <span class="pill focus">Foco intenso</span><span class="pill">Nutanix University</span>
      </div>
      <div class="phase" style="border-left-color:var(--slate)">
        <h3>AWS AI Practitioner <span class="when">Repaso ligero</span></h3>
        <p>El más liviano. Se cuela como repaso entre bloques pesados, no compite por foco.</p>
        <span class="pill">Mantenimiento</span>
      </div>
      <div class="phase" style="border-left-color:var(--plum)">
        <h3>Inglés <span class="when">Diario · siempre</span></h3>
        <p>No es un examen puntual, es habilidad por exposición continua. 20–30 min diarios. Input (podcasts técnicos en inglés) + speaking activo. Va en <b>Equilibrio</b> como racha diaria.</p>
        <span class="pill">20–30 min/día</span><span class="pill">Podcasts técnicos</span>
      </div>
    </div>

    <!-- CRECIMIENTO -->
    <div v-else-if="current==='crecimiento'" class="view">
      <h2 class="view-title">Crecimiento</h2>
      <div class="section-intro">Un arquitecto de portafolio que no está al día pierde autoridad técnica. Aquí la vigilancia tecnológica se vuelve hábito con cadencia, y la mente se entrena como un músculo.</div>
      <div class="principle"><b>Cadencia:</b> bloque semanal de vigilancia (60–90 min) → capturas lo relevante abajo → una vez al mes sintetizas: <i>¿qué de esto impacta el portafolio de Internexa?</i></div>

      <div class="cols" style="margin-bottom:22px">
        <div class="card">
          <div class="card-head"><h3><span class="dot" style="background:var(--moss)"></span>Tendencias capturadas</h3><span class="count" style="background:var(--moss)">{{ trends.filter(t=>!t.done).length }}</span></div>
          <div class="card-body">
            <div v-if="trends.length" v-for="it in trends" :key="it.id" class="item" :class="{done:it.done}">
              <div class="chk" @click="toggleTrend(it.id)">{{ it.done?'✓':'' }}</div>
              <div class="txt">{{ it.text }}<span v-if="it.source" class="meta">{{ it.source }}</span></div>
              <div class="x" @click="delTrend(it.id)">×</div>
            </div>
            <div v-else class="empty">Captura aquí lo que encuentres en tu bloque de vigilancia</div>
            <div class="mini-add">
              <input v-model="newTrend" @keydown.enter="addTrend" placeholder="Nueva tendencia / hallazgo…" />
              <button @click="addTrend">+</button>
            </div>
          </div>
        </div>
      </div>

      <h3 class="subhead">Tecnología al día · fuentes por dominio</h3>
      <div class="cols" style="margin-bottom:22px">
        <div v-for="s in TECH_SOURCES" :key="s.cat" class="card">
          <div class="card-head"><h3><span class="dot" style="background:var(--slate)"></span>{{ s.cat }}</h3></div>
          <div class="card-body">
            <div v-for="i in s.items" :key="i" class="item" style="cursor:default"><div class="txt" style="padding-left:2px">› {{ i }}</div></div>
          </div>
        </div>
      </div>

      <h3 class="subhead">Crecimiento mental fuerte · prácticas</h3>
      <div class="cols">
        <div v-for="p in MENTAL_PRACTICES" :key="p.name" class="card">
          <div class="card-body" style="padding:16px">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
              <span style="font-size:1.3rem;color:var(--gold)">{{ p.icon }}</span>
              <b style="font-size:1rem">{{ p.name }}</b>
            </div>
            <p style="font-size:.82rem;color:var(--ink-soft);margin:0">{{ p.desc }}</p>
          </div>
        </div>
      </div>
      <div class="principle" style="margin-top:20px"><b>Regla del músculo mental:</b> mente fuerte no es saber más, es pensar mejor bajo presión. Marca tus prácticas diarias en <b>Equilibrio</b> para que no queden como buena intención.</div>
    </div>

    <!-- EQUILIBRIO -->
    <div v-else-if="current==='equilibrio'" class="view">
      <h2 class="view-title">Equilibrio</h2>
      <div class="section-intro">El sistema no sirve si te quema. Estos ritmos personales se cuidan igual que un entregable. Marca cada día que los honras — la racha es el recordatorio.</div>
      <div v-for="r in RHYTHMS" :key="r.key" class="rhythm">
        <div class="rhythm-head"><span class="dot" :style="{background:r.color,width:'12px',height:'12px'}"></span><h3>{{ r.name }}</h3></div>
        <div class="rhythm-head"><span class="why">{{ r.why }}</span></div>
        <div class="streak-row">
          <div v-for="d in last7()" :key="d.toISOString()"
               class="day"
               :class="{on:isOn(r.key, d.toISOString().slice(0,10)), today:d.toISOString().slice(0,10)===todayKey}"
               @click="toggleDay(r.key, d.toISOString().slice(0,10))">
            <div class="box">{{ isOn(r.key, d.toISOString().slice(0,10)) ? r.icon : '' }}</div>
            <span class="lbl">{{ DL[d.getDay()] }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- SEMANA -->
    <div v-else-if="current==='semana'" class="view">
      <h2 class="view-title">Mi semana</h2>
      <div class="section-intro">Una plantilla de time-blocking para empezar — protege los bloques de trabajo profundo y estudio, que no sobreviven a la fragmentación. Ajústala a tu realidad con el recién nacido en casa.</div>
      <div class="week-grid">
        <div v-for="w in WEEK" :key="w.d" class="slot">
          <div class="d">{{ w.d }}</div>
          <div v-for="(b,i) in w.blocks" :key="i" class="blk"><b>{{ b[0] }}</b><span v-if="b[1]"> · {{ b[1] }}</span></div>
        </div>
      </div>
      <div class="principle" style="margin-top:18px"><b>Regla de oro de reuniones:</b> los últimos 5 minutos de cada reunión, captura quién hace qué y para cuándo. Lo tuyo → Próximas acciones. Lo de otros → En espera de.</div>
    </div>

    <!-- REVISIÓN -->
    <div v-else-if="current==='revision'" class="view">
      <h2 class="view-title">Revisión semanal</h2>
      <div class="section-intro">45–60 min fijos, mismo día cada semana (sugerido: viernes). Es el hábito que mantiene vivo todo el sistema — sin él, se degrada en dos semanas.</div>
      <ul class="review">
        <li v-for="(s,i) in REVIEW_STEPS" :key="i" :class="{done: review[i] && review[i].done}">
          <div class="rchk" @click="review[i] && toggleReview(review[i].id)">{{ review[i] && review[i].done ? '✓' : '' }}</div>
          <span>{{ s }}</span>
        </li>
        <button class="reset" @click="resetReview">Reiniciar para la próxima semana</button>
      </ul>
    </div>
  </main>

  <footer>Datos persistidos en MySQL vía Django REST · Centro de operaciones personal</footer>
</template>
