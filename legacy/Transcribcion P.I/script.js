const btnAction = document.getElementById('btn-action');
const btnClear = document.getElementById('btn-clear');
const display = document.getElementById('texto-transcrito');

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (!SpeechRecognition) {
    display.innerHTML = "❌ Tu navegador no soporta el reconocimiento de voz. Usa Chrome.";
} else {
    const recognition = new SpeechRecognition();
    recognition.lang = 'es-ES';
    recognition.continuous = true;
    recognition.interimResults = true;

    let isListening = false;

    recognition.onresult = (event) => {
        let transcript = '';
        for (let i = 0; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript;
        }
        display.innerText = transcript;
    };

    btnAction.onclick = () => {
        if (!isListening) {
            recognition.start();
            btnAction.innerText = "Detener Escucha";
            btnAction.style.backgroundColor = "#dc3545";
        } else {
            recognition.stop();
            btnAction.innerText = "Iniciar Micrófono";
            btnAction.style.backgroundColor = "#28a745";
        }
        isListening = !isListening;
    };

    btnClear.onclick = () => {
        display.innerText = "";
        if(isListening) {
            recognition.stop();
            setTimeout(() => recognition.start(), 100);
        }
    };

    recognition.onerror = (event) => {
        console.error("Error:", event.error);
    };
}
function guardarNota() {
    const texto = display.innerText;
    if (texto.trim() === "") return;

    const lista = document.getElementById('lista-notas');
    const li = document.createElement('li');
    li.className = "tarjeta-nota"; 
    
    const hora = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    li.innerHTML = `
        <div class="nota-preview">${texto.substring(0, 50)}...</div>
        <div class="nota-info">Nota ${hora}</div>
    `;
    
    li.onclick = () => { display.innerText = texto; };
    lista.prepend(li);
}

