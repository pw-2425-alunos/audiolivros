let mediaRecorder;
let audioChunks = [];
let audioBlob; 

const startButton = document.getElementById('start');
const stopButton = document.getElementById('stop');
const audioPlayer = document.getElementById('player');
const goToCriarButton = document.getElementById('goToCriar');

navigator.mediaDevices.getUserMedia({ audio: true })
  .then((stream) => {
    mediaRecorder = new MediaRecorder(stream);

    // Ao ter dados disponíveis, armazena os chunks
    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data);
    };

    // Quando a gravação parar, cria o Blob e atualiza o player
    mediaRecorder.onstop = () => {
      audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
      audioChunks = []; // Reseta para futuras gravações
      const audioUrl = URL.createObjectURL(audioBlob);
      audioPlayer.src = audioUrl;
      startButton.disabled = false;
      stopButton.disabled = true;
    };
  })
  .catch((error) => {
    console.error('Error accessing microphone:', error);
    alert('Microphone access is required to record audio.');
  });

// Evento para iniciar a gravação
startButton.addEventListener('click', () => {
  if (mediaRecorder) {
    mediaRecorder.start();
    startButton.disabled = true;
    stopButton.disabled = false;
    console.log('Recording started...');
  }
});

// Evento para parar a gravação
stopButton.addEventListener('click', () => {
  if (mediaRecorder) {
    mediaRecorder.stop();
    console.log('Recording stopped.');
  }
});

// Evento para enviar o áudio e redirecionar ao criar audiolivro
goToCriarButton.addEventListener('click', () => {
  // Se não houver áudio gravado, apenas redireciona
  if (!audioBlob) {
    window.location.href = "/audiolivro/novo"; // Ajuste conforme sua URL
    return;
  }

  // Cria um objeto FormData e adiciona o áudio
  const formData = new FormData();
  formData.append('audio', audioBlob, 'gravacao.webm');

  // Envia o áudio para o servidor via fetch
  fetch("/upload_audio/", {  // Certifique-se de que essa URL está configurada no seu urls.py
    method: 'POST',
    body: formData,
    headers: {
      'X-CSRFToken': csrfToken, // O token passado do template
    }
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      // Redireciona para a página de criação com o parâmetro do áudio
      window.location.href = "/audiolivro/novo?audio=" + encodeURIComponent(data.audio_url);
    } else {
      alert('Erro ao fazer upload do áudio.');
    }
  })
  .catch(error => {
    console.error('Erro:', error);
    alert('Erro ao enviar o áudio.');
  });
});
