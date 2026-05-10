const btnAction = document.getElementById('btn-action');
const btnClear = document.getElementById('btn-clear');
const display = document.getElementById('texto-transcrito');

// Configuración de la API
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

if (!SpeechRecognition) {
    display.innerHTML = "❌ Tu navegador no soporta el reconocimiento de voz. Usa Chrome.";
} else {
    const recognition = new SpeechRecognition();
    recognition.lang = 'es-ES';
    recognition.continuous = true;
    recognition.interimResults = true;

    let isListening = false;

    // Lógica al recibir resultados
    recognition.onresult = (event) => {
        let transcript = '';
        for (let i = 0; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript;
        }
        display.innerText = transcript;
    };

    // Botón Iniciar/Detener
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

    // Botón Limpiar
    btnClear.onclick = () => {
        display.innerText = "";
        // Reiniciamos el reconocimiento para limpiar el buffer interno
        if(isListening) {
            recognition.stop();
            setTimeout(() => recognition.start(), 100);
        }
    };

    recognition.onerror = (event) => {
        console.error("Error:", event.error);
    };
}
