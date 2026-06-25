# Despliegue · Centro de Mando

Monorepo: `backend/` (Django REST + MySQL) y `frontend/` (Vue 3 + Vite).
Backend → **Railway**. Frontend → **Vercel**. Base de datos → **MySQL gestionado en Railway**.

---

## 0. Subir a GitHub

Desde la raíz del proyecto (`centro_mando/`):

```bash
git init
git add .
git commit -m "Centro de Mando: backend Django + frontend Vue"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/centro-mando.git
git push -u origin main
```

> El `.gitignore` ya excluye `.env`, `node_modules`, `venv` y `staticfiles`.
> **Nunca subas tu `.env`** — las credenciales van en los paneles de Railway/Vercel.

---

## 1. Backend + MySQL en Railway

1. Entra a [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo** → elige tu repo.
2. Railway detecta el monorepo. En **Settings → Root Directory** deja la raíz (el `railway.json` ya apunta a `backend/`).
3. Agrega la base de datos: dentro del proyecto, **+ New → Database → Add MySQL**.
   Railway crea la variable `DATABASE_URL` y la comparte al servicio automáticamente.
4. En el servicio del backend → pestaña **Variables**, añade:

   | Variable | Valor |
   |----------|-------|
   | `SECRET_KEY` | una cadena larga aleatoria |
   | `DEBUG` | `False` |
   | `ALLOWED_HOSTS` | el dominio que te dé Railway (ej. `centro-mando.up.railway.app`) |
   | `CORS_ALLOWED_ORIGINS` | la URL de tu frontend en Vercel (la añades tras el paso 2) |

   > `DATABASE_URL` ya está; no la escribas a mano.
   > `RAILWAY_PUBLIC_DOMAIN` la inyecta Railway sola.

5. Railway construye y ejecuta el `Procfile`: migra, recoge estáticos y arranca gunicorn.
6. Cuando termine, en **Settings → Networking → Generate Domain** obtienes la URL pública.
7. **Sembrar datos iniciales** (una sola vez): en la pestaña del servicio abre la consola
   (o usa Railway CLI) y corre:

   ```bash
   cd backend && python manage.py seed_data
   ```

Verifica entrando a `https://TU-APP.up.railway.app/mando/objectives/` — debe devolver JSON.

---

## 2. Frontend en Vercel

1. Entra a [vercel.com](https://vercel.com) → **Add New → Project** → importa el mismo repo de GitHub.
2. En la configuración del proyecto:
   - **Root Directory**: déjalo en la raíz (el `vercel.json` ya apunta a `frontend/`).
   - Framework Preset: **Other** (lo controla el `vercel.json`).
3. En **Environment Variables**, añade:

   | Variable | Valor |
   |----------|-------|
   | `VITE_API_URL` | `https://TU-APP.up.railway.app/mando` |

   > Usa la URL real de Railway del paso 1, terminando en `/mando`.

4. **Deploy**. Vercel construye el frontend y te da una URL tipo `https://centro-mando.vercel.app`.

---

## 3. Cerrar el círculo (CORS)

Vuelve a Railway → Variables del backend → pon en `CORS_ALLOWED_ORIGINS` la URL de Vercel
(ej. `https://centro-mando.vercel.app`, sin barra final). Railway redespliega solo.

Abre tu frontend de Vercel: el indicador arriba a la derecha debe decir **"Guardado en MySQL ✓"**.

---

## Notas

- **Sin autenticación**: cualquiera con la URL ve y edita tus datos. Cuando quieras
  cerrarlo, se añade login con token (DRF `TokenAuthentication` o JWT) — pídemelo.
- **Redeploys**: cada `git push` a `main` redespliega backend y frontend automáticamente.
- **Migraciones nuevas**: si cambias modelos, corre `makemigrations` en local,
  commitea las migraciones y haz push; Railway aplica `migrate` en cada arranque.
- **Costo**: Railway y Vercel tienen plan gratuito suficiente para uso personal;
  Railway puede pedir tarjeta tras el crédito inicial.
