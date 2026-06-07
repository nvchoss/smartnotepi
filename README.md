# SmartNote Pi

SmartNote Pi es una aplicación web que te permite **dictar notas con tu voz** y guardarlas automáticamente. Ideal para tomar apuntes en clases, reuniones o cualquier situación donde escribir a mano sea poco práctico.

Hablas, el texto aparece en pantalla en tiempo real, le pones un título y lo guardas. Tus notas quedan almacenadas y las puedes ver, descargar o borrar cuando quieras.

---

## ¿Qué necesitas para usarlo?

- Una computadora con Windows, Mac o Linux
- El navegador **Google Chrome** (es el único que soporta el reconocimiento de voz)
- **Python 3** instalado (ver instrucciones más abajo)
- Conexión a internet (solo para que Chrome pueda procesar la voz)

---

## Instalación paso a paso

### 1. Verificar que tienes Python instalado

Abre una terminal y escribe:

```
python3 --version
```

Si aparece algo como `Python 3.10.0` o superior, ya lo tienes. Si no, descárgalo desde [python.org](https://www.python.org/downloads/).

---

### 2. Descargar el proyecto

Si tienes Git instalado, ejecuta en la terminal:

```
git clone https://github.com/RamiroContre/smartnotepi.git
cd smartnotepi
```

Si no tienes Git, puedes descargar el proyecto como ZIP desde GitHub (botón verde "Code" → "Download ZIP"), descomprimirlo y abrir una terminal dentro de la carpeta.

---

### 3. Crear el entorno virtual e instalar dependencias

El entorno virtual no está incluido en el repositorio, así que hay que crearlo la primera vez. Dentro de la carpeta del proyecto, ejecuta:

```
python3 -m venv venv
```

Luego actívalo:

**En Windows:**
```
venv\Scripts\activate
```

**En Mac / Linux:**
```
source venv/bin/activate
```

E instala Flask:

```
pip3 install flask
```

> Notarás que la terminal ahora dice `(venv)` al principio. Eso significa que el entorno virtual está activo. Debes activarlo cada vez que quieras usar la aplicación.

---

### 4. Iniciar la aplicación

Con el entorno virtual activo, ejecuta:

```
python3 app.py
```

Verás algo así:

```
 * Running on http://127.0.0.1:5000
```

---

### 5. Abrir en el navegador

Abre **Google Chrome** y escribe en la barra de direcciones:

```
http://localhost:5000
```

La primera vez que uses el micrófono, Chrome te pedirá permiso. Haz clic en **Permitir**.

---

## ¿Cómo se usa?

| Acción | Cómo hacerlo |
|--------|-------------|
| Grabar | Haz clic en el botón rojo del micrófono |
| Detener | Haz clic de nuevo en el mismo botón |
| Cambiar idioma | Haz clic en la bandera (alterna entre Español e Inglés) |
| Guardar nota | Escribe un título y haz clic en **Guardar** |
| Ver nota guardada | Haz clic en el ícono del ojo en la tarjeta |
| Descargar nota | Haz clic en el ícono de descarga — se guarda como `.txt` |
| Borrar nota | Haz clic en el ícono de la papelera |
| Buscar notas | Escribe en la barra de búsqueda del panel derecho |
| Limpiar texto | Haz clic en el botón **Limpiar** |

---

## Para cerrar la aplicación

En la terminal donde está corriendo el servidor, presiona `Ctrl + C`.

---

## Estructura del proyecto

```
smartnotepi/
├── app.py          → Servidor web y base de datos
├── notas.db        → Base de datos (se crea automáticamente)
├── static/
│   └── index.html  → Interfaz de la aplicación
└── legacy/         → Versiones anteriores del proyecto
```

> `venv/` y `notas.db` no están en el repositorio. Se generan localmente al seguir los pasos de instalación.

---

## Problemas frecuentes

**El micrófono no funciona**
Asegúrate de estar usando Google Chrome y de haber dado permiso al micrófono. La aplicación no funciona en Firefox ni en Safari.

**"Permission denied" al activar el entorno virtual en Windows**
Abre PowerShell como administrador y ejecuta:
```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**La página no carga**
Verifica que el servidor esté corriendo (debe aparecer el mensaje `Running on http://127.0.0.1:5000` en la terminal) y que estés usando `http://localhost:5000` en Chrome.
